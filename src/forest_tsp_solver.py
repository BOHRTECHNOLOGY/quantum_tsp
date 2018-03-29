import pyquil.api as api
import numpy as np
from grove.pyqaoa.qaoa import QAOA
from pyquil.paulis import PauliTerm, PauliSum
import scipy.optimize
import TSP_utilities
import pdb

class ForestTSPSolver(object):
    """docstring for TSPSolver"""
    def __init__(self, nodes_array, steps=3, ftol=1.0e-4, xtol=1.0e-4):
        self.nodes_array = nodes_array
        self.qvm = api.QVMConnection()
        self.steps = 3
        self.ftol = ftol
        self.xtol = xtol
        self.betas = None
        self.gammas = None
        self.qaoa_inst = None
        self.most_freq_string = None
        
    def solve_tsp(self):
        self.find_angles()
        return self.get_solution()

    def find_angles(self):
        self.number_of_qubits = self.get_number_of_qubits()

        cost_operators = self.create_cost_operators()
        driver_operators = self.create_driver_operators()

        minimizer_kwargs = {'method': 'Nelder-Mead',
                                'options': {'ftol': self.ftol, 'xtol': self.xtol,
                                            'disp': False}}

        vqe_option = {'disp': print_fun, 'return_all': True,
                      'samples': None}

        self.qaoa_inst = QAOA(self.qvm, self.number_of_qubits, steps=self.steps, cost_ham=cost_operators,
                         ref_hamiltonian=driver_operators, store_basis=True,
                         minimizer=scipy.optimize.minimize,
                         minimizer_kwargs=minimizer_kwargs,
                         vqe_options=vqe_option)

        self.betas, self.gammas = self.qaoa_inst.get_angles()

    def get_results(self):
        print("Most frequent bitstring from sampling")
        most_freq_string, sampling_results = self.qaoa_inst.get_string(self.betas, self.gammas, samples=10000)
        self.most_freq_string = most_freq_string
        return sampling_results

    def get_solution(self):
        if self.most_freq_string is None:
            self.most_freq_string, _ = self.qaoa_inst.get_string(self.betas, self.gammas, samples=10000)
        quantum_order = TSP_utilities.binary_state_to_points_order_full(self.most_freq_string)
        return quantum_order

    def create_cost_operators(self):
        cost_operators = []
        cost_operators += self.create_penalty_operators_for_bilocation()
        cost_operators += self.create_penalty_operators_for_repetition()
        # cost_operators += create_weights_cost_operators(nodes_array)
        return cost_operators

    def create_penalty_operators_for_bilocation(self):
        # Additional cost for visiting more than one node in given time t
        cost_operators = []
        number_of_nodes = len(self.nodes_array)
        for t in range(number_of_nodes):
            range_of_qubits = list(range(t * number_of_nodes, (t + 1) * number_of_nodes))
            cost_operators += self.create_penalty_operators_for_qubit_range(range_of_qubits)
        return cost_operators

    def create_penalty_operators_for_repetition(self):
        # Additional cost for visiting given node more than one time
        cost_operators = []
        number_of_nodes = len(self.nodes_array)
        for i in range(number_of_nodes):
            range_of_qubits = list(range(i, number_of_nodes**2, number_of_nodes))
            cost_operators += self.create_penalty_operators_for_qubit_range(range_of_qubits)
        return cost_operators

    def create_penalty_operators_for_qubit_range(self, range_of_qubits):
        cost_operators = []
        tsp_matrix = TSP_utilities.get_tsp_matrix(self.nodes_array)
        # weight = -10 * np.max(tsp_matrix)
        weight = 0.5
        for i in range_of_qubits:
            if i == range_of_qubits[0]:
                z_term = PauliTerm("Z", i, weight)
                all_ones_term = PauliTerm("I", 0, 0.5 * weight) - PauliTerm("Z", i, 0.5 * weight)
            else:
                z_term = z_term * PauliTerm("Z", i)
                all_ones_term = all_ones_term * (PauliTerm("I", 0, 0.5) - PauliTerm("Z", i, 0.5))

        z_term = PauliSum([z_term])
        cost_operators.append(PauliTerm("I", 0, weight) - z_term)

        return cost_operators

    def create_weights_cost_operators(self):
        cost_operators = []
        number_of_nodes = len(self.nodes_array)
        tsp_matrix = TSP_utilities.get_tsp_matrix(self.nodes_array)
        
        for i in range(number_of_nodes):
            for j in range(i, number_of_nodes):
                for t in range(number_of_nodes - 1):
                    weight = tsp_matrix[i][j] / 2
                    if tsp_matrix[i][j] != 0:
                        qubit_1 = t * number_of_nodes + i
                        qubit_2 = (t + 1) * number_of_nodes + j
                        cost_operators.append(PauliTerm("I", 0, weight) - PauliTerm("Z", qubit_1, weight) * PauliTerm("Z", qubit_2))

        return cost_operators

    def create_driver_operators(self):
        driver_operators = []
        
        for i in range(self.number_of_qubits):
            driver_operators.append(PauliSum([PauliTerm("X", i, -1.0)]))

        return driver_operators

    def get_number_of_qubits(self):
        return len(self.nodes_array)**2


def print_fun(x):
    print(x)


def visualize_cost_matrix(qaoa_inst, cost_operators, number_of_qubits, gammas=np.array([1.0]), steps=1):
    from referenceqvm.api import QVMConnection as debug_QVMConnectiont
    debug_qvm = debug_QVMConnectiont(type_trans='unitary')
    param_prog, cost_param_programs = qaoa_inst.get_parameterized_program()
    import pyquil.quil as pq
    final_cost_prog = pq.Program()

    for idx in range(steps):
        for fprog in cost_param_programs[idx]:
            final_cost_prog += fprog(gammas[idx])

    final_matrix = debug_qvm.unitary(final_cost_prog)
    costs = np.diag(final_matrix)
    pure_costs = np.real(np.round(-np.log(costs)*1j,3))
    for i in range(2**self.number_of_qubits):
        print(np.binary_repr(i, width=self.number_of_qubits), pure_costs[i], np.round(costs[i],3))
    most_freq_string, sampling_results = qaoa_inst.get_string(betas, gammas, samples=100000)
    print("Most common results")
    [print(el) for el in sampling_results.most_common()[:10]]
    print("Least common results")
    [print(el) for el in sampling_results.most_common()[-10:]]
    pdb.set_trace()