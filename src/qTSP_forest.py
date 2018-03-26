import pyquil.api as api
import numpy as np
from grove.pyqaoa.qaoa import QAOA
from pyquil.paulis import PauliTerm, PauliSum
import scipy.optimize
import TSP_utilities
import pdb

def solve_tsp(nodes_array):
    nodes_array = np.array([[0, 0], [0, 1]])
    qvm = api.QVMConnection()


    number_of_qubits = get_number_of_qubits(len(nodes_array))
    steps = 3

    cost_operators = []
    cost_operators += create_cost_operators(nodes_array)

    driver_operators = create_driver_operators(number_of_qubits)

    minimizer_kwargs = {'method': 'Nelder-Mead',
                            'options': {'ftol': 1.0e-2, 'xtol': 1.0e-2,
                                        'disp': False}}

    vqe_option = {'disp': print_fun, 'return_all': True,
                  'samples': None}

    # init_gammas = np.array([1.0])
    qaoa_inst = QAOA(qvm, number_of_qubits, steps=steps, cost_ham=cost_operators,
                     ref_hamiltonian=driver_operators, store_basis=True,
                     minimizer=scipy.optimize.minimize,
                     minimizer_kwargs=minimizer_kwargs,
                     vqe_options=vqe_option)

    betas = np.array([2.7])
    betas, gammas = qaoa_inst.get_angles()
    # For 2 nodes, z_term only, weight = 0.5
    betas = np.array([1.0])
    gammas = np.array([1.0])

    print("BETAS", betas)
    print("GAMMAS", gammas)
    probs = qaoa_inst.probabilities(np.hstack((betas, gammas)))
    visualize_cost_matrix(qaoa_inst, cost_operators, number_of_qubits, gammas, steps=steps)

    print("Most frequent bitstring from sampling")
    most_freq_string, sampling_results = qaoa_inst.get_string(betas, gammas, samples=10000)
    # [print(el) for el in sampling_results.most_common()[:10]]
    pdb.set_trace()
    quantum_order = TSP_utilities.binary_state_to_points_order_full(most_freq_string)
    return quantum_order


def create_cost_operators(nodes_array):
    cost_operators = []
    # cost_operators += create_weights_cost_operators(nodes_array)
    cost_operators += create_penalty_operators_for_bilocation(nodes_array)
    cost_operators += create_penalty_operators_for_repetition(nodes_array)
    return cost_operators


def create_weights_cost_operators(nodes_array):
    cost_operators = []
    number_of_nodes = len(nodes_array)
    tsp_matrix = TSP_utilities.get_tsp_matrix(nodes_array)
    
    for i in range(number_of_nodes):
        for j in range(i, number_of_nodes):
            for t in range(number_of_nodes - 1):
                weight = tsp_matrix[i][j] / 2
                if tsp_matrix[i][j] != 0:
                    qubit_1 = t * number_of_nodes + i
                    qubit_2 = (t + 1) * number_of_nodes + j
                    cost_operators.append(PauliTerm("Z", qubit_1, weight) * PauliTerm("Z", qubit_2) + PauliTerm("I", 0, -weight))

    return cost_operators


def create_penalty_operators_for_bilocation(nodes_array):
    # Additional cost for visiting more than one node in given time t
    cost_operators = []
    number_of_nodes = len(nodes_array)
    for t in range(number_of_nodes):
        range_of_qubits = list(range(t * number_of_nodes, (t + 1) * number_of_nodes))
        cost_operators += create_penalty_operators_for_qubit_range(nodes_array, range_of_qubits)
    return cost_operators


def create_penalty_operators_for_repetition(nodes_array):
    # Additional cost for visiting given node more than one time
    cost_operators = []
    number_of_nodes = len(nodes_array)
    for i in range(number_of_nodes):
        range_of_qubits = list(range(i, number_of_nodes**2, number_of_nodes))
        cost_operators += create_penalty_operators_for_qubit_range(nodes_array, range_of_qubits)
    return cost_operators


def create_penalty_operators_for_qubit_range(nodes_array, range_of_qubits):
    cost_operators = []
    tsp_matrix = TSP_utilities.get_tsp_matrix(nodes_array)
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
    print(z_term)
    # Not sure what's the mathematical justification for the value of 2
    # But it works consistently.
    # cost_operators.append(z_term + 2 * all_ones_term)
    cost_operators.append(PauliTerm("I", 0, weight) - z_term)

    return cost_operators


def create_driver_operators(number_of_qubits):
    driver_operators = []
    
    for i in range(number_of_qubits):
        driver_operators.append(PauliSum([PauliTerm("X", i, -1.0)]))

    return driver_operators


def print_fun(x):
    print(x)


def get_number_of_qubits(n):
    return n**2


def visualize_cost_matrix(qaoa_inst, cost_operators, number_of_qubits, gammas=np.array([1.0]), steps=1):
    from referenceqvm.api import QVMConnection as debug_QVMConnectiont
    debug_qvm = debug_QVMConnectiont(type_trans='unitary')
    param_prog, cost_param_programs = qaoa_inst.get_parameterized_program()
    import pyquil.quil as pq
    final_cost_prog = pq.Program()

    for idx in range(steps):
        for fprog in cost_param_programs[idx]:
            final_cost_prog += fprog(gammas[idx])

    # for prog in cost_param_programs:
    #     for exp_map in prog:
    #         final_cost_prog += exp_map(gammas[0])

    final_matrix = debug_qvm.unitary(final_cost_prog)
    costs = np.diag(final_matrix)
    pure_costs = np.real(np.round(-np.log(costs)*1j,3))
    for i in range(2**number_of_qubits):
        print(np.binary_repr(i, width=number_of_qubits), pure_costs[i], np.round(costs[i],3))
    most_freq_string, sampling_results = qaoa_inst.get_string(gammas, gammas, samples=100000)
    print("Most common results")
    [print(el) for el in sampling_results.most_common()[:10]]
    print("Least common results")
    [print(el) for el in sampling_results.most_common()[-10:]]
    pdb.set_trace()

if __name__ == '__main__':
    solve_tsp(np.array([[0, 0], [0, 7], [0, 14]]))