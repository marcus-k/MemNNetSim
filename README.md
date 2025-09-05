# Memristive Nanowire Network Simulator (MemNNetSim)

Python package for modelling and analyzing random nanowire networks.

# Table of Contents
* [Installation](#installation)
* [Usage](#usage)
* [Uninstallation](#uninstallation)

# Installation

The latest version of MemNNetSim can be installed from PyPI:

`pip install mnns`

An Anaconda environment file is also provided to create a new virtual 
environment with the minimum required dependencies required to run the package.

`conda env create -n mnns -f environment.yml`

Be sure you activate the environment before using the package!

`conda activate mnns`

# Development

One can use the `dev-environment.yml` file with Anaconda to create a new 
virtual environment with all the required dependencies for development.

`conda env create -n randomnwn -f dev-environment.yml`

This will also install the randomnwn package in editable mode (i.e. as if 
running `pip install -e .` in the base folder).

A pip version of [21.1](https://pip.pypa.io/en/latest/news/#v21-1) or greater is required.

# Usage

Nanowire network objects are simply [NetworkX](https://github.com/networkx/networkx) graphs with various attributes stored in the graph, edges, and nodes.

```python
>>> import randomnwn as rnwn
>>> NWN = rnwn.create_NWN(seed=123)
>>> NWN
                Type: JDA
               Wires: 750
          Electrodes: 0
Inner-wire junctions: None
      Wire junctions: 3238
              Length: 50.00 um (7.143 l0)
               Width: 50.00 um (7.143 l0)
        Wire Density: 0.3000 um^-2 (14.70 l0^-2)
>>> rnwn.plot_NWN(NWN)
(<Figure size 800x600 with 1 Axes>, <AxesSubplot:>)
```
![Figure_1](https://user-images.githubusercontent.com/81660172/127204015-9f882ef5-dca3-455d-998f-424a5787b141.png)

See the [wiki pages](https://github.com/Marcus-Repository/Random-NWNs/wiki) for more detail on usage.

# Uninstallation

To uninstall the package, use:

`pip uninstall randomnwn`
