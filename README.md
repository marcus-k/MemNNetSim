# Memristive Nanowire Network Simulator (MemNNetSim)

MemNNetSim: Memristive Nanowire Network Simulator. A proof-of-concept Python package for modelling and analyzing memristive random nanowire networks (NWNs).

# Table of Contents
* [Installation](#installation)
* [Development](#development)
* [Usage](#usage)
* [Uninstallation](#uninstallation)

# Installation

MemNNetSim has been tested on Python 3.10 to 3.13. It is recommended to install MemNNetSim in a virtual environment such as with venv or conda/mamba.

For installing locally, a pip version of 21.1 or greater is required.

## Installation from PyPI

Install the latest release of MemNNetSim using pip:
```bash
pip install mnns
```

## Installation for development

Download or clone the GitHub repository:
```bash
git clone https://github.com/marcus-k/MemNNetSim.git
cd ./MemNNetSim
```

Then install the package in editable mode using pip:
```bash
pip install -e .[dev]
```

To install for editing the documentation, add the `[docs]` optional dependencies:
```bash
pip install -e .[docs]
```

# Usage

Nanowire network objects are simply [NetworkX](https://github.com/networkx/networkx) graphs with various attributes stored in the graph, edges, and nodes.

```python
>>> import mnns
>>> NWN = mnns.create_NWN(seed=123)
>>> NWN
                Type: JDA
               Wires: 750
          Electrodes: 0
Inner-wire junctions: None
      Wire junctions: 3238
              Length: 50.00 um (7.143 l0)
               Width: 50.00 um (7.143 l0)
        Wire Density: 0.3000 um^-2 (14.70 l0^-2)
>>> mnns.plot_NWN(NWN)
(<Figure size 800x600 with 1 Axes>, <AxesSubplot:>)
```
![Figure_1](https://user-images.githubusercontent.com/81660172/127204015-9f882ef5-dca3-455d-998f-424a5787b141.png)

# Uninstallation

To uninstall the package, use:

`pip uninstall mnns`
