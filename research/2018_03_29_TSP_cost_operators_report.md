# TSP cost operators test

This report was originally posted in https://github.com/mstechly/quantum_computing/tree/master/Experiments/2018_03_29_TSP_cost_operators. If a file is referenced in this report, you should look for it in that repository. The version updated according to the suggestion in this report is one with commit hash: `66922554fc2016baf9c2fbc0417de051be57fd2c`.

## Introduction

While working on the script for solving Traveling Salesman Problem with quantum computer, we encountered the following problems:

- the results were not consistent - for the same parameters we could got different results depending on how the final angles for QAOA.
- We've observed some correlation between the QAOA parameters and quality of results, but we weren't able to say how exactly changes in parameters influences time of computation and quality of the results.
- due to that it was hard to determine if the changes we've introduced to the cost_operators are actually helping to achieve desirable results.

Taking all of the above into the account we decided to take a more systematic approach.

The main goals of this experiment were:
- Create a setup for systematic testing different sets of parameters
- Find set of parameters that's working reasonably well
- Check what's the proper coefficient for all_ones_term 

## Dependencies

As a main engine for solving TSP we used code from this repository: https://github.com/BOHRTECHNOLOGY/quantum_tsp, imported as a subtree.

We were using pyquil and grove.
Pyquil version about 1.8.0 (Unfortunately we have not written down the exact version).
Grove version 1.6.0 + commit `c1f51f671e5704cb246025b85c9d24d5d8bee2a8`.

We had to use a modified version of grove due to a bug (commit `c1f51f671e5704cb246025b85c9d24d5d8bee2a8` fixes it). We decided to commit the exact same version we used.

## Experiment description

The whole experiment was performed on a 3-nodes graphs. The coordinates of the graph were fixed and equal to [[0, 0], [0, 7], [0, 14]].
The case of 2 nodes was trivial, and for 4 nodes the calculations took too much time.

### Phase 1

In the first phase we've created a script for running forest_tsp_solver with different parameters.
Parameters we were changing were: `steps` and `tol`.  `steps` is number of steps in the QAOA algorithms. `xtol` and `ftol` are parameters of the classical minizer used in QAOA, however we used the same value for both of them and called it `tol`.

Since running Forest code requires internet access and for the given test we didn't have a access to a reliable internet connection, we decided to use randomized choice of parameters. 
This way we were sure that even if the internet connection is broken, none set of parameters will be over or under represented in our results.

We were rating the results based on the following criterias:
- what's the percentage of the correct solutions
- is the best solution valid.

The best set of parameters was `steps=3` and `tol=1e-4`. The more detailed results can be found below.


### Phase 2

After finding a reasonably good set of parameters in Phase 1, we used it to find proper coefficients for all_ones_term in forest_tsp_solver.
This term is used to ban [1, 1, 1] groups in the TSP solution.

During the initial tests we crossed out values of 1 and 2 of the coefficient and decided to test values of -1 and -2.

Both values gave very similar results - the proper solution was the most probable in about 73% of cases, and the mean number of correct solutions was about 3300/10000. These results are labeled as `phase_2_1`.

We then repeated the calculations, but this time for all the possible combinations of parameters. For -1 there were about 20 results for each parameter set, for -2 about 70.
Using -2 gave slightly better results (68% vs 60% and 2354/10000 vs 2121/10000), which may indicate that making this value even lower, may bring even better results. We decided to stay with the -2 value for now.

These results are labeled as `phase_2_2`. You can find some visualizations of these results in `results/plots`.

### Phase 3

In the third phase we decided to check if we can get a good solution of the actual TSP problem. So we added cost associated with the distances between nodes.

Since the initial tests showed that the number of valid solutions dropped, we decided to check if using higher weight for the penalty operators will help with this. We checked values of 10 and 100. By valid solution we mean a solution where we visit every city once and only one city at any given point in time.
The results are stored in `phase_3_results_weight_10_standard_case.csv` and `phase_3_results_weight_100_standard_case.csv`.

Indeed, using higher weight gave better results in most cases. We checked the following metrics. The numbers given here are for the best set of parameters (steps=3 and tol=10e-4):
1. Percentage of best solutions being valid (71% vs 83%)
2. Mean count of valid solutions in all of the results (1030/10000 vs 1677/10000)
3. Mean count of the best solution if it was valid (377/10000 vs 1162/10000)
4. Mean error of valid solutions (3.5 vs 2.65)

The differences for other sets of parameters were also present, but not as high as in this case.

Changing the weight has not changed calculation time significantly - mean calculation times for this case were 430 and 417 seconds respectively. Higher weights may lead to faster convergence but in this case it's more probable that the difference is statistically insignificant.

You can find some visualizations of the results in `results/plots`.

## Results

What we achieved with this experiment:
- we've written code which solves the TSP problem for 3 nodes with specific coordinates: [[0,0], [0,7], [0,14]]. 
- we've checked what's the relationship between the algorithm performance and different parameters.
- we've created basic framework for running repeatable tests of quantum algorithms.

The final set of parameters that we recommend is: 
- steps = 3
- tol = 1e-4
- all_ones coefficient = -2
- penalty operators weight = 100

## Next steps

The next steps should be:
- Check how the algorithm works for any set of coordinates with 3 nodes
- Check how the algorithm works for 4 nodes


