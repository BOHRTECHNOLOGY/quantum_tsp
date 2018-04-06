# Quantum TSP

This repository contains code for solving Travelling Salesman Problem using quantum computing.

## Subtree

If you want to use this repository as a subtree follow those instructions. If not - you can skip to the next section.

### Setup

To add a new remote run the following:

```bash
git remote add qtsp_subtree git@github.com:BOHRTECHNOLOGY/quantum_tsp.git
```

From now on, instead of writing the whole path `git@github.com:BOHRTECHNOLOGY/quantum_tsp.git`, you can use `qtsp_subtree`. So to add the subtree you can use either:

```bash
git subtree add --prefix path/to/your/dir/qtsp_subtree qtsp_subtree master --squash
```

or:

```bash
git subtree add --prefix path/to/your/dir/qtsp_subtree qtsp_subtree master --squash
```

`path/to/your/dir/qtsp_subtree` should be the path from the top directory of the repository you are in. It automatically generates a new commit.

### Updating

```bash
git subtree pull --prefix path/to/your/dir/qtsp_subtree qtsp_subtree master --squash
```

### Commiting

If you want to commit to this repo with subtree do the following:

1. Commit changes. AFAIK git deals with changes in other files properly - i.e. when you push to subtree it sees only changes in subtree. Remember that commit name will be transfered too!
2. Push on new-branch: 

```bash
git subtree push --prefix path/to/your/dir/qtsp_subtree qtsp_subtree new-branch
```


## Libraries used

This project makes a use of quantum computing libraries, you can install them with pip:

    pip install pyquil
    pip install quantum-grove

### Pyquil

Pyquil is a library allowing you to create code for quantum computers to be executed using Rigetti Forest platform. It's developed by Rigetti Computing.
To run your code on the quantum virtual machine or quantum processor you need to configure file, as described here:
http://pyquil.readthedocs.io/en/latest/start.html#connecting-to-the-rigetti-forest

### Grove

Grove is a collection of quantum algorithms built using the Rigetti Forest platform. I use its implementation of QAOA for pyquil.

https://github.com/rigetticomputing/grove

## Sources 

- QAOA paper: https://arxiv.org/abs/1411.4028
- Demo from IBM: https://nbviewer.jupyter.org/github/QISKit/qiskit-tutorial/blob/stable/4_applications/classical_optimization.ipynb
- Rigetti Maxcut paper: https://arxiv.org/pdf/1712.05771.pdf

