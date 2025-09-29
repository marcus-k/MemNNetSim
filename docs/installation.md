# Installation

MemNNetSim has been tested on Python 3.10 to 3.13. It is recommended to install
MemNNetSim in a virtual environment such as with [venv](https://docs.python.org/3/library/venv.html) 
or [conda](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html)/[mamba](https://github.com/conda-forge/miniforge).

For installing locally, a pip version of [21.1](https://pip.pypa.io/en/latest/news/#v21-1) 
or greater is required.

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

## Uninstallation

Uninstall MemNNetSim using pip:
```bash
pip uninstall mnns
```

## Testing

MemNNetSim uses `pytest` to run the tests in the `tests/` directory and is
installed when installing MemNNetSim with the `[dev]` optional dependencies.

In the root directory of the package, run the tests with:
```bash
pytest
```
