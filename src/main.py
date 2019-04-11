import time
import TSP_utilities
from forest_tsp_solver import ForestTSPSolver
from dwave_tsp_solver import DWaveTSPSolver

def main():
    nodes_array = TSP_utilities.create_nodes_array(4)
    tsp_matrix = TSP_utilities.get_tsp_matrix(nodes_array)
    starting_node = 0
    sapi_token = None
    dwave_url = 'https://cloud.dwavesys.com/sapi'

    print("Brute Force solution")
    start_time = time.time()
    bf_start_time = start_time
    brute_force_solution = TSP_utilities.solve_tsp_brute_force_from_given_node(nodes_array, starting_node)
    end_time = time.time()
    calculation_time = end_time - start_time
    print("Calculation time:", calculation_time)
    TSP_utilities.plot_solution('brute_force_' + str(start_time), nodes_array, brute_force_solution)

    if sapi_token is None or dwave_url is None:
        print("You cannot run code on DWave without specifying your sapi_token and url")
    elif len(nodes_array) >= 10:
        print("This problem size is to big to run on D-Wave.")
    else:
        print("DWave solution")
        start_time = time.time()
        dwave_solver = DWaveTSPSolver(tsp_matrix, sapi_token=sapi_token, url=dwave_url)
        dwave_solution, dwave_distribution = dwave_solver.solve_tsp()
        end_time = time.time()
        calculation_time = end_time - start_time
        print("Calculation time:", calculation_time)
        costs = [(sol, TSP_utilities.calculate_cost(tsp_matrix, sol), dwave_distribution[sol]) for sol in dwave_distribution]
        solution_cost = TSP_utilities.calculate_cost(tsp_matrix, dwave_solution)
        print("DWave:", dwave_solution, solution_cost)
        for cost in costs:
            print(cost)
        TSP_utilities.plot_solution('dwave_' + str(bf_start_time), nodes_array, dwave_solution)


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