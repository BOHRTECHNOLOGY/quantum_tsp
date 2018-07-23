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
    def __init__(self, distance_matrix, steps=2, ftol=1.0e-3, xtol=1.0e-3, initial_state="all", starting_node=0):

        self.distance_matrix = distance_matrix
        self.starting_node = starting_node
        # Since we fixed the starting city, the effective number of nodes is smaller by 1
        self.reduced_number_of_nodes = len(self.distance_matrix) - 1
        self.qvm = api.QVMConnection()
        self.steps = steps
        self.ftol = ftol
        self.xtol = xtol
        self.betas = None
        self.gammas = None
        self.qaoa_inst = None
        self.number_of_qubits = self.get_number_of_qubits()
        self.solution = None
        self.distribution = None

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
        self.calculate_solution()
        return self.solution, self.distribution

    def find_angles(self):
        """
        Runs the QAOA algorithm for finding the optimal angles.
        """
        self.betas, self.gammas = self.qaoa_inst.get_angles()
        return self.betas, self.gammas

    def calculate_solution(self):
        """
        Samples the QVM for the results of the algorithm 
        and returns a list containing the order of nodes.
        """
        most_frequent_string, sampling_results = self.qaoa_inst.get_string(self.betas, self.gammas, samples=10000)
        reduced_solution = TSP_utilities.binary_state_to_points_order(most_frequent_string)
        full_solution = self.get_solution_for_full_array(reduced_solution)
        self.solution = full_solution
        
        all_solutions = sampling_results.keys()
        distribution = {}
        for sol in all_solutions:
            reduced_sol = TSP_utilities.binary_state_to_points_order(sol)
            full_sol = self.get_solution_for_full_array(reduced_sol)
            distribution[tuple(full_sol)] = sampling_results[sol]
        self.distribution = distribution

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
        reduced_distance_matrix = np.delete(self.distance_matrix, self.starting_node, axis=0)
        reduced_distance_matrix = np.delete(reduced_distance_matrix, self.starting_node, axis=1)
        for t in range(self.reduced_number_of_nodes - 1):
            for city_1 in range(self.reduced_number_of_nodes):
                for city_2 in range(self.reduced_number_of_nodes):
                    if city_1 != city_2:
                        distance = reduced_distance_matrix[city_1, city_2]
                        qubit_1 = t * (self.reduced_number_of_nodes) + city_1
                        qubit_2 = (t + 1) * (self.reduced_number_of_nodes) + city_2
                        cost_operators.append(PauliTerm("Z", qubit_1, distance) * PauliTerm("Z", qubit_2))

        costs_to_starting_node = np.delete(self.distance_matrix[:, self.starting_node], self.starting_node)

        for city in range(self.reduced_number_of_nodes):
            distance_from_0 = -costs_to_starting_node[city]
            qubit = city
            cost_operators.append(PauliTerm("Z", qubit, distance_from_0))

        for city in range(self.reduced_number_of_nodes):
            distance_from_0 = -costs_to_starting_node[city]
            qubit = self.number_of_qubits - (self.reduced_number_of_nodes) + city
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

        for t in range(self.reduced_number_of_nodes - 1):
            for city_1 in range(self.reduced_number_of_nodes):
                for city_2 in range(self.reduced_number_of_nodes):
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
        if type(initial_state) is list:
            for i in range(self.reduced_number_of_nodes):
                initial_state_program.inst(X(i * (self.reduced_number_of_nodes) + initial_state[i]))

        elif initial_state == "all":
            vector_of_states = np.zeros(2**self.number_of_qubits)
            list_of_possible_states = []
            initial_order = range(0, self.reduced_number_of_nodes)
            all_permutations = [list(x) for x in itertools.permutations(initial_order)]
            for permutation in all_permutations:
                coding_of_permutation = 0
                for i in range(len(permutation)):
                    coding_of_permutation += 2**(i * (self.reduced_number_of_nodes) + permutation[i])
                vector_of_states[coding_of_permutation] = 1
            initial_state_program = create_arbitrary_state(vector_of_states)

        return initial_state_program

    def get_number_of_qubits(self):
        return (self.reduced_number_of_nodes)**2

    def s_plus(self, city, time):
        qubit = time * (self.reduced_number_of_nodes) + city
        return PauliTerm("X", qubit) + PauliTerm("Y", qubit, 1j)

    def s_minus(self, city, time):
        qubit = time * (self.reduced_number_of_nodes) + city
        return PauliTerm("X", qubit) - PauliTerm("Y", qubit, 1j)


def print_fun(x):
    print(x)
