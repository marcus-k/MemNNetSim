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
    shape = (8, 5), 
    seed = 5,
    conductance = 1.0
)
```

The [`add_electrodes()`](reference/mnns/nanowires.md#mnns.nanowires.add_electrodes) 
function provides different ways to add electrodes to a NWN and return
their index. These are equipotential nanowires with no memristive junctions.
```python
left, right = mnns.add_electrodes(NWN, "left", "right")
```

By default, NWNs are created using the junction dominated assumption (JDA).
This assumes nanowires are equipotential and have no internal resistance. Only 
after all desired electrodes are added, the NWN can be converted to the 
multi-nodal representation (MNR) in-place.
```python
NWN.to_MNR()
```
This adds internal nanowire resistance based on the nanowire diameter and
resistivity (specified when initializing the NWN) and recreates the 
underlying graph object to add these additional nodes and edges. 

## NWN Units

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

## NWN Indices

Since MemNNetSim uses NetworkX graphs as the parent class for NWNs, the nodes
and edges can still be indexed using `NWN.nodes` and `NWN.edges` respectively;
however, the index labels are different depending on if the NWN is using JDA
or MNR.

For JDA NWNs, the indices used are a one-tuple of integers.
```python
>>> NWN.nodes[(0,)]
{'electrode': False}
```
JDA nodes represent individual nanowires and edges represent a junction between
nanowires.

For MNR NWNs, the indices used are a two-tuple of integers.
```python
>>> NWN.nodes[(0, 0)]
{'loc': <POINT (6.443 3.971)>, 'electrode': False}
```
MNR nodes represent specific points on a nanowire and edges represent either a
junction between nanowires or an inner-nanowire connection.

!!! note "Electrode Indices"
    Regardless of if a NWN is using JDA or MNR, electrodes will always be
    indexed using a one-tuple since by definition they are equipotential!

Edges can then be indexed as expected.
```python
>>> NWN.edges[((0, 0), ((0, 5)))]
{'conductance': 1.7122000108743876, 'capacitance': 0, 'type': 'inner'}
```
The `type` edge attribute stores whether the edges is an inner-nanowire
connection or a nanowire junction. Currently, the `capacitance` edge attribute 
is not used for anything.

## Static Solution

The [`solve_network()`](reference/mnns/calculations.md#mnns.calculations.solve_network)
function is used to obtain the NWN nanowire voltages given the location of the
source and drain nanowires and a voltage for the sources. Often, it is 
desirable to use electrodes for these nodes.
```python
out = mnns.solve_network(NWN, left, right, voltage)
```
If the NWN has `N` nanowires and `M` voltage sources, then the output will have
the first `N` elements correspond to the nanowire voltages and the last `M`
elements correspond to the current draw of the voltage sources.

!!! note "Modified Nodal Analysis"
    The implemented algorithm of solving the nanowire voltages follows the
    *modified nodal analysis* scheme. More information about the algorithm
    can be found on the [Swarthmore College website](https://lpsa.swarthmore.edu/Systems/Electrical/mna/MNA3.html).
    

## Dynamic Solution

To solve the NWN nanowire voltages over time, [`NWN.evolve()`](reference/mnns/nanowire_network.md#mnns.nanowire_network.NanowireNetwork.evolve) 
is performed to the network. Various parameters must be set first before
evolving the network. A walkthrough of an example parameters follows.

Define the voltage and window functions.
```python
def voltage_func(t):
    """DC Voltage"""
    V0 = 20
    return V0 * np.ones_like(t)

def window_func(x):
    """Strukov window function"""
    x = np.clip(x, 0, 1)
    return x * (1 - x)
```

Define the memristive model with the desired resistance function and the 
associated state variables.
```python
model = mnns.models.HP_model
NWN.resistance_function = "linear"
NWN.state_vars = ["x"]
NWN.set_state_var("x", 0.1)
```
!!! info "Model Parameters"
    For models with extra parameters, for example in the [Decay HP model](reference/mnns/models.md#mnns.models.decay_HP_model),
    they can be set with graph attributes.
    ```python
    NWN.graph["tau"] = 100
    ```

!!! info "State Variable Order"
    For models which use multiple state variables (such as [`mnns.models.SLT_HP_model`](reference/mnns/models.md#mnns.models.SLT_HP_model)),
    the order of `NWN.state_vars` matters! The pre-implemented linear resistance
    function is evaluated using the first state variable in the list.

Define the time steps.
```python
min_time = 0
max_time = 10000
dt = 1.0
t_eval = np.arange(min_time, max_time, dt)
```

Evolve the NWN and return the state variables as a function of time. The `args`
parameters is passed to the memristive model function. Evolving the network
over time is perform using SciPy's [`solve_ivp`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html) 
function. `ivp_options` is passed directly to there.
```python
tol = 1e-7
args = (NWN, left, right, voltage_func, window_func)
sol = NWN.evolve(
    model, t_eval, args=args, ivp_options={"rtol": tol, "atol": tol}
)
```

Using the state variable solution, the current through each of the grounded
nodes could be found by updating the state variables iteratively with the
dynamic solution and solving the [static case](#static-solution). This
is implemented in [`mnns.get_evolution_current()`](reference/mnns/dynamics.md#mnns.dynamics.get_evolution_current).
```python
I = mnns.get_evolution_current(NWN, sol, left, right, voltage_func)
```
