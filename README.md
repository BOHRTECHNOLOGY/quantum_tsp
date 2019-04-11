# Quantum TSP

This repository contains code for an open source program solving the Travelling Salesman Problem with Quantum Computing.

## Structure

There are two directories.
`src` contains all the source code necessary to solve TSP.
`research` contains reports and references to research, which lead to improving the code base.


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

### DWave

DWave is a quantum annealer - another type of quantum computing devices. To use it you need the following library:

    pip install dwave-system

and have your own `sapi-token`. You can obtain it here: https://cloud.dwavesys.com/qubist/apikey/, though I am not sure if anyone is eligible to get it.

*Warning!*

There are a couple of things worth knowing when it comes to this version:

1. The biggest number of cities that can be solved on D-Wave 2000Q is 9. The amount of qubits needed to solve the problem grows as N^2 and finding embedding for the case with 10 cities will fail in most (if not all) cases.

2. This implementation doesn't allow you to specify the starting point - it needs some modifications to take this information into account.

3. If you experience any unexpected problems with D-Wave libraries, you might want to install an older version - this script definitely worked with `dwave-system==0.5.1`:

## Sources 

- QAOA paper: https://arxiv.org/abs/1411.4028
- Demo from IBM: https://nbviewer.jupyter.org/github/Qiskit/qiskit-tutorial/blob/master/qiskit/aqua/optimization/maxcut_and_tsp.ipynb
- Rigetti Maxcut paper: https://arxiv.org/pdf/1712.05771.pdf


