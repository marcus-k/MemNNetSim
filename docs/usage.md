# Usage

Import MemNNetSim using:
```python
import mnns
```

## Creating a NWN

Create a NWN with the default parameters.
```python
NWN = mnns.create_NWN()
```

The [`create_NWN()`](reference/mnns/nanowire_network.md#mnns.nanowire_network.create_NWN)
constructor has various parameters to initialize and customize it.
```python
NWN = mnns.create_NWN(
    size = (8, 5), 
    seed = 5,
    conductance = 1.0
)
```

Add electrodes (equipotential wires with no memristive junctions) to a NWN.
```python
left, right = mnns.add_electrodes(NWN, "left", "right")
```

## Units

MemNNetSim performs all calculations using nondimensionalized units. As such, 
inputs into various MemNNetSim functions require inputs which have no units.

To get the default units for the physical and electrical quantities:
```python
units = mnns.NWNUnits()
print(units)
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
units = mnns.NWNUnits({"v0": 2.0})
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

To solve for the voltages of each of the nanowires in a NWN and the current
through each of the voltage sources. 
```python
out = mnns.solve_network(NWN, left, right, voltage)
```
If the NWN has `N` nanowires and `M` voltage sources, then the output will have
the first `N` elements correspond to the nanowire voltage and the last `M`
elements correspond to the voltage source currents.

!!! note "Modified Nodal Analysis"
    The implemented algorithm of solving the nanowire voltages follows the
    [*modified nodal analysis*](https://lpsa.swarthmore.edu/Systems/Electrical/mna/MNA3.html) 
    scheme. 

## Dynamic Solution

To solve the NWN nanowire voltages over time, [`NWN.evolve()`](reference/mnns/nanowire_network.md#mnns.nanowire_network.NanowireNetwork.evolve) 
is performed to the network. Various parameters must be set first before
evolving the network.

