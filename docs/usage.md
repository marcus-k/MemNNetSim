# Usage

## Creating a NWN

Create a NWN with the default parameters.
```python
>>> import mnns
>>> NWN = mnns.create_NWN()
```

## Units

MemNNetSim performs all calculation using nondimensionalized units. Inputs
into the various functions MemNNetSim provides as such require inputs which
have had their units removed.

To get the default units for the physical and electrical quantities:
```python
>>> units = mnns.get_units()
>>> print(units)
{'v0': 1.0,
 'Ron': 10.0,
 'l0': 7.0,
 'D0': 50.0,
 'w0': 10.0,
 'rho0': 22.6,
 'mu0': 0.01,
 'Roff_Ron': 160,
 'i0': 0.1,
 't0': 10000.0}
```

## Static Solution

## Dynamic Solution