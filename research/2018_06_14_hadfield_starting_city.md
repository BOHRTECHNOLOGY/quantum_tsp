# Hadfield QAOA - adding starting city

## Introduction

The goal of this experiment was to implement an version of algorithm with specified starting node. This allows to change scaling of number of qubits from N^2 to (N-1)^2.

## Dependencies

As a main engine for solving TSP we used code from this repository: https://github.com/BOHRTECHNOLOGY/quantum_tsp, imported as a subtree.

We were using pyquil and grove.
Pyquil: commit hash: `26ae363e9f5c85dc3aab298daebc9ec5023a32a1`
Grove: commit hash: `e3fd7b9f3188e820dd19ff487dbf56c8faf43822`

The exact versions of these repositories are commited to this project.

## Tests

After the implementation we decided to check if it is correct. We ran the tests for 3 and 4 cities (4 and 9 qubits). 

We used the following parameters:

- `tol=1e-3`
- `steps=2`
- `initial_state="all"`

The placement of the cities was random.

## Results

### Observation 1

This modification has not changed the calculation time for given number of qubits or the difference was too small to measure.

### Observation 2

There were no significant differences between performance of different starting nodes.

### Observation 3 

For 4 qubits case (3 cities), the results were correct in 100% cases. For 9 qubits (4 cities) the results were correct in 70% of the cases. 
In the previous experiment for 9 qubits and 3 cities the accuracy was about 90%. 


## Conclusions

Adding starting point has not changed the performance of the algorithm very much and improved the size of the problem that can be feasibly tackled with it.

Lower percentage of correct results for given number of qubits might be a result of slightly harder problem to solve - there are additional constraints for the initial point. It may be probably still improved by using different parameters.

