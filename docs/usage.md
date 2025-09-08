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
>>> units = mnns.NWNUnits()
>>> print(units)
      v0: 1.0     V, Voltage
     Ron: 10.0    Ω, ON Junction resistance
      l0: 7.0     μm, Wire length
      D0: 50.0    nm, Wire diameter
      w0: 10.0    nm, Junction length (2x Wire coating thickness)
    rho0: 22.6    nΩm, Wire resistivity
     mu0: 0.01    μm^2 s^-1 V^-1, Ion mobility
Roff_Ron: 160     Off-On Resistance ratio
      i0: 0.1     A, Current
      t0: 10000.0 μs, Time
```

By passing a dictionary of units, one can change what the unit values are:
```python
>>> units = mnns.NWNUnits({"v0": 2.0})
```

!!! note "Derived Units"
    Units `i0` and `t0` are *derived units*, that is, they are derived
    from the other base units. They cannot be set directly by passing in a
    dictionary like the others. Instead, you must set the units they depend on.

    They are calculated with the following formula:
    ```python
    i0 = v0 / Ron
    t0 = w0**2 / (mu0 * v0)
    ```

These units can then be used when creating a NWN.
```python
units = mnns.NWNUnits({"v0": 2.0})
NWN = mnns.create_NWN(units=units)
```

## Static Solution

## Dynamic Solution