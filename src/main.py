import time
import TSP_utilities
from forest_tsp_solver import ForestTSPSolver

def main():
    nodes_array = TSP_utilities.create_nodes_array(4)
    tsp_matrix = TSP_utilities.get_tsp_matrix(nodes_array)
    starting_node = 0

    print("Brute Force solution")
    start_time = time.time()
    bf_start_time = start_time
    brute_force_solution = TSP_utilities.solve_tsp_brute_force_from_given_node(nodes_array, starting_node)
    end_time = time.time()
    calculation_time = end_time - start_time
    print("Calculation time:", calculation_time)
    TSP_utilities.plot_solution('brute_force_' + str(start_time), nodes_array, brute_force_solution)

    print("QAOA solution - Forest")
    start_time = time.time()
    forest_solver = ForestTSPSolver(tsp_matrix, starting_node=starting_node)
    forest_solution, forest_distribution = forest_solver.solve_tsp()
    end_time = time.time()
    calculation_time = end_time - start_time
    print("Calculation time:", calculation_time)
    costs = [(sol, TSP_utilities.calculate_cost(tsp_matrix, sol), forest_distribution[sol]) for sol in forest_distribution]
    print("Forest:")
    for cost in costs:
        print(cost)
    TSP_utilities.plot_solution('forest_' + str(bf_start_time), nodes_array, forest_solution)


if __name__ == '__main__':
    main()