# Hadfield QAOA

This report was originally posted in https://github.com/mstechly/quantum_computing/tree/master/Experiments/2018_05_26_hadfield_qaoa. If a file is referenced in this report, you should look for it in that repository. At the moment the results from this research have not been implemented here - it will be after adding some additional features.

## Introduction

The goal of this experiment was to implement version of QAOA more suited for bounded problems like TSP. It's description is in the `resources` directory.

## Dependencies

As a main engine for solving TSP we used code from this repository: https://github.com/BOHRTECHNOLOGY/quantum_tsp, imported as a subtree.

We were using pyquil and grove.
Pyquil: commit hash: `26ae363e9f5c85dc3aab298daebc9ec5023a32a1`
Grove: commit hash: `e3fd7b9f3188e820dd19ff487dbf56c8faf43822`

The exact versions of these repositories are commited to this project.

## Tests

After implementing the algorithm we decided to test how it works for different cases city placement and parameters. 
We decided to use the following set of parameters:
- steps: 1, 2 or 3
- tolerance: 1e-2, 1e-3, 1e-4

After the initial tests we decided to remove `steps=3` and `tol=1e-4` since other parameters seemed sufficient for this problem and the time of calculation for these was significantly larger.

We also tried many different types of city placement to how the algorithm behaves in various cases. You can find the description in the appendix below and the results in the `results` directory.
Below are the most interesting observations we made:

### Observation 1

In 4 cases 100% of the results were correct. These were cases 0, 1, 5 and 6, which all are symmetrical and all of them have optimal solution starting from city 0.
In case 2, which is same as cases 0 and 1, but the optimal solution needs to start from city 1 or 2, algorithm achieved 20% accuracy for `steps=1` and 100% accuracy for `steps=2`.

### Observation 2

In all cases results for `steps=2` are higher than the results for `steps=1` and usually are enough to achieve correct results. Calculation time for the former is usually 2 times longer than for the latter - about 100 seconds for the `tol=1e-2` and 150 for `tol=1e-3`.

### Observation 3

The worst results were achieved for highly assymetric cases: 3, 4 and 7.
What's interesting, for case 3 `steps=1` gave correct results in 100% cases and `steps=2` in only 45/60 (depending on `tol`). That's probably because the initial state was actually a correct solution, since for case 4, which has the same coordinates, but in different order, for `steps=1` there were no correct solutions (same for case 7).

### Observation 4

For cities placed on the vertices of an equilateral triangle (case 5) all the solutions are correct, so all should be equally probable.
However, it wasn't the case. It's interesting to see, that with more precise parameters of the algorithm, we get better distribution. Below is the list containing parameters and the mean probability of the best solution.

- `steps=1`, `tol=1e-2`: 70(25)%
- `steps=1`, `tol=1e-3`: 67(24)%
- `steps=2`, `tol=1e-2`: 61(19)%
- `steps=2`, `tol=1e-3`: 57(19)%

The ideal value would be 16.6%, and even though the mean values presented here are far from that, teh standard deviation is pretty high, which shows that this algorithm sometimes may give sometimes yield well or badly distributed results.

### Observation 5

Since we have not introduced any boundary conditions, for every case there should be at least two correct solutions, e.g.: 0 -> 1 -> 2 and 2 -> 1 -> 0. However, the probability of the correct solution returned by the algorithm was usually very close to 100%. It means, that it was finding only one of the two possible solutions. Usually it was the one same as inital state or closest to it.

### Observation 6 

When we tried to calculate the 4-city case, the Forest API returned a 400 error. That's probably due to the fact, that the payload - Quil program containing the quantum code - was too big. This, however, need to be confirmed by Rigetti engineers.

## Conclusions

Based on the observations made in the previous section we drew the following about this implementation of the algorithm:

- it's sensitive to the initial state
- it gives correct results in most cases - for the random city placement and `steps=2` algorithm yields correct results in 90% of cases.
- in case of multiple correct solution it's not very good at distinguishing between them

We also decided to use `steps=2` and `tol=1e-2` for further research.

### Further steps

The next step would be checking how this algorithm works when initialized with different initial states, e.g. mixture of all possible states or some subset of them.

The other thing is explaining error we got for bigger number of cities. One way to go around this would be test if it's possible to add boundary condition (e.g. we start from city 0) in order to make number of qubits scale like (N - 1)^2 instead of N^2.


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