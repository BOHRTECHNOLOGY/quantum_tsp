import pyquil.api as api
import numpy as np
from grove.pyqaoa.qaoa import QAOA
from grove.alpha.arbitrary_state.arbitrary_state import create_arbitrary_state
from pyquil.paulis import PauliTerm, PauliSum
import pyquil.quil as pq
from pyquil.gates import X
import itertools

import scipy.optimize
import TSP_utilities
import pdb

class ForestTSPSolver(object):
    """
    Class for solving Travelling Salesman Problem (with starting point) using Forest - quantum computing library.
    It uses QAOA method with operators as described in the following paper:
    https://arxiv.org/pdf/1709.03489.pdf by Stuart Hadfield et al.
    
    """
    def __init__(self, full_nodes_array, steps=2, ftol=1.0e-3, xtol=1.0e-3, initial_state="all", starting_node=0):
        reduced_nodes_array, costs_to_starting_node = self.reduce_nodes_array(full_nodes_array, starting_node)

        self.nodes_array = reduced_nodes_array
        self.starting_node = starting_node
        self.full_nodes_array = full_nodes_array
        self.costs_to_starting_node = costs_to_starting_node
        self.qvm = api.QVMConnection()
        self.steps = steps
        self.ftol = ftol
        self.xtol = xtol
        self.betas = None
        self.gammas = None
        self.qaoa_inst = None
        self.number_of_qubits = self.get_number_of_qubits()

        cost_operators = self.create_phase_separator()
        driver_operators = self.create_mixer()
        initial_state_program = self.create_initial_state_program(initial_state)

        minimizer_kwargs = {'method': 'Nelder-Mead',
                                'options': {'ftol': self.ftol, 'xtol': self.xtol,
                                            'disp': False}}

        vqe_option = {'disp': print_fun, 'return_all': True,
                      'samples': None}

        self.qaoa_inst = QAOA(self.qvm, self.number_of_qubits, steps=self.steps, cost_ham=cost_operators,
                         ref_hamiltonian=driver_operators, driver_ref=initial_state_program, store_basis=True,
                         minimizer=scipy.optimize.minimize,
                         minimizer_kwargs=minimizer_kwargs,
                         vqe_options=vqe_option)
        
    def solve_tsp(self):
        """
        Calculates the optimal angles (betas and gammas) for the QAOA algorithm 
        and returns a list containing the order of nodes.
        """
        self.find_angles()
        return self.get_solution()

    def find_angles(self):
        """
        Runs the QAOA algorithm for finding the optimal angles.
        """
        self.betas, self.gammas = self.qaoa_inst.get_angles()
        return self.betas, self.gammas

    def get_solution(self):
        """
        Samples the QVM for the results of the algorithm 
        and returns a list containing the order of nodes.
        """
        most_frequent_string, sampling_results = self.qaoa_inst.get_string(self.betas, self.gammas, samples=10000)
        reduced_solution = TSP_utilities.binary_state_to_points_order(most_frequent_string)
        full_solution = self.get_solution_for_full_array(reduced_solution)
        return full_solution

    def reduce_nodes_array(self, full_nodes_array, starting_node):
        """
        Creates an array of points which exclude the starting one.
        Returns:
        reduced_nodes_array: the reduced array of points without the starting point
        costs_to_starting_node: array with distances from the starting node to points (ordered in the "reduced base")
        """
        reduced_nodes_array = np.delete(full_nodes_array, starting_node, 0)
        tsp_matrix = TSP_utilities.get_tsp_matrix(full_nodes_array)
        costs_to_starting_node = np.delete(tsp_matrix[:, starting_node], starting_node)
        return reduced_nodes_array, costs_to_starting_node

    def get_solution_for_full_array(self, reduced_solution):
        """
        Transforms the solution from its reduced version to the full initial version.
        """
        full_solution = reduced_solution
        for i in range(len(full_solution)):
            if full_solution[i] >= self.starting_node:
                full_solution[i] += 1
        full_solution.insert(0, self.starting_node)
        return full_solution

    def create_phase_separator(self):
        """
        Creates phase-separation operators, which depend on the objective function.
        """
        cost_operators = []
        for t in range(len(self.nodes_array) - 1):
            for city_1 in range(len(self.nodes_array)):
                for city_2 in range(len(self.nodes_array)):
                    if city_1 != city_2:
                        tsp_matrix = TSP_utilities.get_tsp_matrix(self.nodes_array)
                        distance = tsp_matrix[city_1, city_2]
                        qubit_1 = t * len(self.nodes_array) + city_1
                        qubit_2 = (t + 1) * len(self.nodes_array) + city_2
                        cost_operators.append(PauliTerm("Z", qubit_1, distance) * PauliTerm("Z", qubit_2))

        for city in range(len(self.costs_to_starting_node)):
            distance_from_0 = -self.costs_to_starting_node[city]
            qubit = city
            cost_operators.append(PauliTerm("Z", qubit, distance_from_0))

        phase_separator = [PauliSum(cost_operators)]
        return phase_separator

    def create_mixer(self):
        """
        Creates mixing operators, which depend on the structure of the problem.
        Indexing comes directly from 4.1.2 from the  https://arxiv.org/pdf/1709.03489.pdf article, 
        equations 54 - 58.
        """
        mixer_operators = []

        n = len(self.nodes_array)
        for t in range(n - 1):
            for city_1 in range(n):
                for city_2 in range(n):
                    i = t
                    u = city_1
                    v = city_2
                    first_part = 1
                    first_part *= self.s_plus(u, i)
                    first_part *= self.s_plus(v, i+1)
                    first_part *= self.s_minus(u, i+1)
                    first_part *= self.s_minus(v, i)

                    second_part = 1
                    second_part *= self.s_minus(u, i)
                    second_part *= self.s_minus(v, i+1)
                    second_part *= self.s_plus(u, i+1)
                    second_part *= self.s_plus(v, i)
                    mixer_operators.append(first_part + second_part)
        return mixer_operators

    def create_initial_state_program(self, initial_state):
        """
        Creates a pyquil program representing the initial state for the QAOA.
        As an argument it takes either a list with order of the cities, or 
        a string "all". In the second case the initial state is superposition
        of all possible states for this problem.
        """
        initial_state_program = pq.Program()
        number_of_nodes = len(self.nodes_array)
        if type(initial_state) is list:
            for i in range(number_of_nodes):
                initial_state_program.inst(X(i * number_of_nodes + initial_state[i]))

        elif initial_state == "all":
            vector_of_states = np.zeros(2**self.number_of_qubits)
            list_of_possible_states = []
            initial_order = range(0, number_of_nodes)
            all_permutations = [list(x) for x in itertools.permutations(initial_order)]
            for permutation in all_permutations:
                coding_of_permutation = 0
                for i in range(len(permutation)):
                    coding_of_permutation += 2**(i * number_of_nodes + permutation[i])
                vector_of_states[coding_of_permutation] = 1
            initial_state_program = create_arbitrary_state(vector_of_states)

        return initial_state_program

    def get_number_of_qubits(self):
        return len(self.nodes_array)**2

    def s_plus(self, city, time):
        qubit = time * len(self.nodes_array) + city
        return PauliTerm("X", qubit) + PauliTerm("Y", qubit, 1j)

    def s_minus(self, city, time):
        qubit = time * len(self.nodes_array) + city
        return PauliTerm("X", qubit) - PauliTerm("Y", qubit, 1j)


def print_fun(x):
    print(x)
