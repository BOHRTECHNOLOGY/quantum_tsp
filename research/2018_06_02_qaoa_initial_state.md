# Hadfield QAOA - initial states

This report was originally posted in https://github.com/mstechly/quantum_computing/tree/master/Experiments/2018_06_02_qaoa_initial_state. If a file is referenced in this report, you should look for it in that repository. At the moment the results from this research have not been implemented here - it will be after adding some additional features.

## Introduction

The goal of this experiment was to check how implementation of Hadfield's QAOA works when initialized with various initial states.

## Dependencies

As a main engine for solving TSP we use the code from this repository: https://github.com/BOHRTECHNOLOGY/quantum_tsp, imported as a subtree.

We were using pyquil and grove.
Pyquil: commit hash: `26ae363e9f5c85dc3aab298daebc9ec5023a32a1`
Grove: commit hash: `e3fd7b9f3188e820dd19ff487dbf56c8faf43822`

The exact versions of these repositories are commited to this project.

## Tests

We've changed the initial state of the algorithm to the following:

- [2 -> 0 -> 1]
- [2 -> 1 -> 0]
- superposition of all possible states

We also had data from the previous experiment with the [0 -> 1 -> 2] state.
In the rest of this report we will name states not being superposition ([0 -> 1 -> 2], [2 -> 0 -> 1] and [2 -> 1 -> 0]) as simple states as opposed to the complex state (superposition of all states).

Tests were similar to those from the previous experiment, with the following parameters:

- steps = 2
- tol = 1e-3

The variables were city placements (same as in the previous experiment, see appendix) and the initial states.

## Results

Based on the results we've made the following observations:

### Observation 1

Mean calculation time of all the simple states was very similar.

### Observation 2

Mean calculation for complex state was about 2.5 times longer than for the simple states.

### Observation 3 

Algorithm starting from complex state explores all possible solution much better than for simple case. Best solution mean probability is roughly equal to 50% in the cases where there are two optimal solutions (e.g. 0 -> 1 -> 2 and 2 -> 1 -> 0) and to 17% in case of equilateral triangle, where every solution is optimal, so it should have probability of 16.6%.

### Observation 4

The results are in general pretty good. For the random state number of correct solutions varied between 84 - 100% . What's interesting, state 2 -> 1 -> 0 gave good results in all 34 cases, where others had worse performance. Probably more simulations would level this effect. 


## Conclusions

Most of the observations are consistent with intuition. This is good since there are no unexpected effects, that affect the algorithm.

Initializing algorithm with superposition of simple states is a good idea if we want to fully explore the space of possible solutions, however the time of calculation is longer. 
There are two ways to balance these approaches:
- use weaker parameters (steps and tol) with complex state initialization
- initialize algorithm with superposition of some, not all states

Both methods have pros and cons and could be researched.

## Appendix - City placement

Here is a list of the city placement we were using. Below we describe them with the following information:
- Symmetrical/Asymmetrical
- Order of the optimal route: e.g. [0 -> 1 -> 2]. In all cases at least two orderings were correct, since we don't specify the starting point.
- Coordinates e.g.: [[0, 0], [0, 10], [0, 20]]
- 1D / 2D - were all the points on one line or not.


The coordinates were randomly scaled and shifted, so those listed here are just an example.

0. 1D, Symmetrical, [0 -> 1 -> 2] 

[[0, 0], [0, 10], [0, 20]] 

1. 1D, Symmetrical [0 -> 2 -> 1]

[[0, 0], [0, 20], [0, 10]]

2. 1D, Symmetrical [1 -> 0 -> 2]

[[0, 10], [0, 20], [0, 0]]

3. 1D, Asymmetrical [0 -> 1 -> 2]

[[0, 0], [0, 1], [0, 10]]

4. 1D, Asymmetrical [2 -> 0 -> 1]

[[0, 1], [0, 0], [0, 10]]

5. 2D, Symmetrical (equilateral angle), all orderings are the same

[[0, 0], [1, 0], [0.5, np.sqrt(3)/2]]

6. 2D, Symmetrical triangle [0 -> 2 -> 1]

[[-5, 0], [5, 0], [0, 1]]

7. 2D, Assymetrical triangle [0 -> 2 -> 1]

[[0, 0], [15, 0], [0, 1]]

8. 2D, random triangle

In this case it was just a set of random points, so each case was different.