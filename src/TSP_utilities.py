import numpy as np
import itertools
import matplotlib.pyplot as plt

def create_nodes_array(N, seed=None):
    """
    Creates array of random points of size N.
    """
    if seed:
        print("seed", seed)
        np.random.seed(seed)

    nodes_list = []
    for i in range(N):
        nodes_list.append(np.random.rand(2) * 10)
    return np.array(nodes_list)


def get_tsp_matrix(nodes_array):
    """
    Creates distance matrix out of given coordinates.
    """
    number_of_nodes = len(nodes_array)
    matrix = np.zeros((number_of_nodes, number_of_nodes))
    for i in range(number_of_nodes):
        for j in range(i, number_of_nodes):
            matrix[i][j] = distance_between_points(nodes_array[i], nodes_array[j])
            matrix[j][i] = matrix[i][j]
    return matrix


def distance_between_points(point_A, point_B):
    return np.sqrt((point_A[0] - point_B[0])**2 + (point_A[1] - point_B[1])**2)


def solve_tsp_brute_force(nodes_array):
    number_of_nodes = len(nodes_array)
    initial_order = range(0, number_of_nodes)
    all_permutations = [list(x) for x in itertools.permutations(initial_order)]
    cost_matrix = get_tsp_matrix(nodes_array)
    best_permutation = all_permutations[0]
    best_cost = calculate_cost(cost_matrix, all_permutations[0])
    for permutation in all_permutations:
        current_cost = calculate_cost(cost_matrix, permutation)
        if current_cost < best_cost:
            best_permutation = permutation
            best_cost = current_cost
    print("Brute force:", best_permutation, best_cost)
    return best_permutation


def solve_tsp_brute_force_from_given_node(nodes_array, starting_node):
    number_of_nodes = len(nodes_array)
    initial_order = range(0, number_of_nodes)
    all_permutations = [list(x) for x in itertools.permutations(initial_order)]
    cost_matrix = get_tsp_matrix(nodes_array)
    best_permutation = all_permutations[0]
    best_cost = calculate_cost(cost_matrix, all_permutations[0])*1000
    for permutation in all_permutations:
        if permutation[0] != starting_node:
            continue
        current_cost = calculate_cost(cost_matrix, permutation)
        if current_cost < best_cost:
            best_permutation = permutation
            best_cost = current_cost
    print("Brute force:", best_permutation, best_cost)
    return best_permutation


def calculate_cost(cost_matrix, solution):
    cost = 0
    for i in range(len(solution)):
        a = i%len(solution)
        b = (i+1)%len(solution)
        cost += cost_matrix[solution[a]][solution[b]]

    return cost


def plot_solution(name, nodes_array, solution):
    plt.scatter(nodes_array[:, 0], nodes_array[:, 1], s=200)
    for i in range(len(nodes_array)):
        plt.annotate(i, (nodes_array[i, 0] + 0.15, nodes_array[i, 1] + 0.15), size=16, color='r')

    plt.xlim([min(nodes_array[:, 0]) - 1, max(nodes_array[:, 0]) + 1])
    plt.ylim([min(nodes_array[:, 1]) - 1, max(nodes_array[:, 1]) + 1])
    for i in range(len(solution)):
        a = i%len(solution)
        b = (i+1)%len(solution)
        A = solution[a]
        B = solution[b]
        plt.plot([nodes_array[A, 0], nodes_array[B, 0]], [nodes_array[A, 1], nodes_array[B, 1]], c='r')

    cost = calculate_cost(get_tsp_matrix(nodes_array), solution)
    title_string = "Cost:" + str(cost)
    title_string += "\n" + str(solution)
    plt.title(title_string)
    plt.savefig(name + '.png')
    plt.clf()

def points_order_to_binary_state(points_order):
    """
    Transforms the order of points from the standard representation: [0, 1, 2],
    to the binary one: [1,0,0,0,1,0,0,0,1]
    """
    number_of_points = len(points_order)
    binary_state = np.zeros((len(points_order) - 1)**2)
    for j in range(1, len(points_order)):
        p = points_order[j]
        binary_state[(number_of_points - 1) * (j - 1) + (p - 1)] = 1
    return binary_state

def binary_state_to_points_order(binary_state):
    """
    Transforms the the order of points from the binary representation: [1,0,0,0,1,0,0,0,1],
    to the binary one: [0, 1, 2]
    """
    points_order = []
    number_of_points = int(np.sqrt(len(binary_state)))
    for p in range(number_of_points):
        for j in range(number_of_points):
            if binary_state[(number_of_points) * p + j] == 1:
                points_order.append(j)
    return points_order
