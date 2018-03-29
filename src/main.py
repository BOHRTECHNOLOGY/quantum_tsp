import time
import TSP_utilities
from forest_tsp_solver import ForestTSPSolver

def main():
    # seed = 5406
    # nodes_array = TSP_utilities.create_nodes_array(4, seed=seed)
    nodes_array = TSP_utilities.create_nodes_array(3)

    print("Brute Force solution")
    start_time = time.time()
    brute_force_solution = TSP_utilities.solve_tsp_brute_force(nodes_array)
    end_time = time.time()
    calculation_time = end_time - start_time
    print("Calculation time:", calculation_time)
    TSP_utilities.plot_solution('brute_force', nodes_array, brute_force_solution)

    print("QAOA solution - Forest")
    start_time = time.time()
    forest_solver = ForestTSPSolver(nodes_array)
    forest_solution = forest_solver.solve_tsp()
    end_time = time.time()
    calculation_time = end_time - start_time
    print("Calculation time:", calculation_time)
    TSP_utilities.plot_solution('forest_' + str(start_time), nodes_array, forest_solution)


if __name__ == '__main__':
    main()