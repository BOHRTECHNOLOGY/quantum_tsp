# Quantum TSP

This repository contains code for solving Travelling Salesman Problem using quantum computing.

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

### Sources 

- QAOA paper: https://arxiv.org/abs/1411.4028
- Demo from IBM: https://nbviewer.jupyter.org/github/QISKit/qiskit-tutorial/blob/stable/4_applications/classical_optimization.ipynb
- Rigetti Maxcut paper: https://arxiv.org/pdf/1712.05771.pdf

