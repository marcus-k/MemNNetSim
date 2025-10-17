#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Marcus Kasdorf
# Date:   July 8, 2024
"""
Functions to create nanowire networks.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
from collections import Counter
from scipy.integrate import solve_ivp
from functools import lru_cache

import numpy.typing as npt
from scipy.integrate._ivp.ivp import OdeResult
from typing import Callable, Literal, Any, Optional
from shapely.geometry import LineString, Point
from numbers import Number
from .typing import *

from .units import NWNUnits
from .line_functions import create_line
from .nanowires import add_wires, convert_NWN_to_MNR
from . import models


class ParameterNotSetError(Exception):
    """
    Raised when an parameter that needs to used has not been set yet.

    Parameters
    ----------
    param : str
        Name of the parameter that needs to be set.

    message : str, optional
        Explanation of the error.

    """

    def __init__(self, message: str, param: Any | None = None):
        super().__init__(message)
        self.param = param


class NanowireNetwork(nx.Graph):
    """
    Internal nanowire network object. Should not be instantiated directly.
    Use [`mnns.create_NWN`](nanowire_network.md#mnns.nanowire_network.create_NWN)
    instead.

    Parameters
    ----------
    incoming_graph_data : input graph, optional
        Data to initialize graph. Same as networkx.Graph object.

    **attr
        Keyword arguments. Same as networkx.Graph object.

    """

    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)
        self._resist_func = None
        self._state_vars: list[str] = []
        self._state_vars_is_set: list[bool] = []
        self._wire_junctions = None

    @property
    def type(self) -> Literal["JDA", "MNR"]:
        return self.graph["type"]

    @property
    def electrodes(self) -> list[JDANode]:
        return self.graph["electrode_list"]

    @property
    def n_electrodes(self) -> int:
        return len(self.electrodes)

    @property
    def n_wires(self) -> int:
        """Number of wires in the network. Does not include electrodes."""
        return self.graph["wire_num"] - self.n_electrodes

    @property
    def n_inner_junctions(self) -> int | None:
        if self.type != "MNR":
            return None

        _ = Counter(nx.get_edge_attributes(self, "type").values())
        return _["inner"]

    @property
    def n_wire_junctions(self) -> int:
        _ = Counter(nx.get_edge_attributes(self, "type").values())
        return _["junction"]

    @property
    def units(self) -> dict[str, float]:
        return self.graph["units"]

    @property
    def lines(self) -> list[LineString]:
        """List of LineStrings representing the nanowires. Includes electrodes."""
        return self.graph["lines"]

    @property
    def wire_density(self) -> float:
        """Wire density in units of (l0)^-2. Does not include electrodes."""
        return self.graph["wire_density"]

    @property
    def loc(self) -> dict[tuple[int, int], Point]:
        """
        Dictionary of graph edge locations (nanowire junctions). Only
        represents anything meaningful for JDA NWNs. MNR NWNs do not update
        this value. Indexes with a NWNEdge but without the nested tuples.

        Does not have a guaranteed ordering.

        """
        return self.graph["loc"]

    def get_index(self, node: NWNNode | list[NWNNode]) -> NWNNodeIndex:
        """Return the unique index of a node in the network."""
        return self.graph["node_indices"][node]

    def get_node(self, index: NWNNodeIndex) -> NWNNode:
        """Return the node corresponding to the index."""
        try:
            return next(
                k for k, v in self.graph["node_indices"].items() if v == index
            )
        except StopIteration as e:
            raise ValueError("given index does not have a node") from e

    def get_index_from_edge(
        self, edge: NWNEdge | list[NWNEdge]
    ) -> NWNEdgeIndex | list[NWNEdgeIndex]:
        """Return the indices of the nodes in the edge as a tuple."""
        if isinstance(edge, list):
            return [tuple(map(self.get_index, e)) for e in edge]
        else:
            return tuple(map(self.get_index, edge))

    def to_MNR(self) -> None:
        """Converts the NWN to the multi-nodal representation (MNR)."""
        convert_NWN_to_MNR(self)

    @property
    def wire_junctions(self) -> list[NWNEdge]:
        """
        Return a list of edges with the "type" attribute set to "junction".
        Once called, the list is cached so the ordering can be fixed. If wires
        are added, clear the cache by deleting the property.

        """
        if self._wire_junctions is None:
            self._wire_junctions = [
                (u, v)
                for u, v, d in self.edges(data=True)
                if d["type"] == "junction"
            ]

        return self._wire_junctions

    @wire_junctions.deleter
    def wire_junctions(self) -> None:
        self._wire_junctions = None
        self.wire_junction_indices.cache_clear()

    @lru_cache
    def wire_junction_indices(
        self,
    ) -> tuple[list[NWNNodeIndex], list[NWNNodeIndex]]:
        """
        Return the start and end indices of the wire junctions in the network
        as a tuple of lists.

        """
        return np.asarray(self.get_index_from_edge(self.wire_junctions)).T

    @property
    def state_vars(self) -> list[str]:
        return self._state_vars

    @state_vars.setter
    def state_vars(self, names: list[str]) -> None:
        self._state_vars = names
        self._state_vars_is_set = {name: False for name in names}

    @property
    def resistance_function(
        self,
    ) -> Callable[[NanowireNetwork, npt.ArrayLike], npt.ArrayLike]:
        """
        Resistance function of the nanowire network. Should have the calling
        signature `func(NWN, param1, [param2, ...])` where `NWN` is the
        nanowire network, and `param1`, `param2`, etc. are the state variables
        of the memristor element(s).

        You can also pass the string "linear" to choose a default linear
        resistance function based on the state variable x in [0, 1].

        The resistance should be nondimensionalized, i.e. the resistance should
        be in units of Ron.

        """
        return self._resist_func

    @resistance_function.setter
    def resistance_function(
        self,
        func: str | Callable[[NanowireNetwork, npt.ArrayLike], npt.ArrayLike],
    ) -> None:
        if func == "linear":
            self._resist_func = models.resist_func
        else:
            self._resist_func = func

    def set_state_var(
        self,
        var_name: str,
        value: npt.ArrayLike,
        edge_list: list[NWNEdge] | None = None,
    ) -> None:
        """
        Set the state variable of the memristors (nanowire network wire
        junctions) in the network.

        Parameters
        ----------
        var_name : str
            Name of the state variable(s) to set.

        value : ndarray or scalar
            Value to set the state variable(s) to.

        edge_list : list of edges, optional
            List of edges to set the state variable for. If None, all wire
            junction edges will be used. Should be the same length as the value
            array.

        """
        value = np.atleast_1d(value)

        if var_name not in self.state_vars:
            cls = self.__class__
            raise ParameterNotSetError(
                f"'{var_name}' is not in {cls.__qualname__}.state_vars (currently is {self.state_vars})."
                f"\nDid you set it using {cls.__qualname__}.state_vars = ['{var_name}', ...]?"
            )

        edge_list = self.wire_junctions if edge_list is None else edge_list

        # Set the state variable for the given edges to the same value...
        if value.size == 1:
            nx.set_edge_attributes(
                self, {edge: {var_name: value[0]} for edge in edge_list}
            )

        # or to different values
        elif value.size == len(edge_list):
            nx.set_edge_attributes(
                self,
                {
                    edge: {var_name: value[i]}
                    for i, edge in enumerate(edge_list)
                },
            )

        else:
            raise ValueError(
                f"Length of value array ({value.size}) does not match the number of edges ({len(edge_list)})."
            )

        self._state_vars_is_set[var_name] = True

    def get_state_var(
        self, var_name: str, edge_list: list[NWNEdge] | None = None
    ) -> npt.ArrayLike:
        """
        Get the state variable of the memristors (nanowire network wire
        junctions) in the network.

        Parameters
        ----------
        var_name : str
            Name of the state variable(s) to get.

        edge_list : list of edges, optional
            List of edges to get the state variable from. If None, all wire
            junction edges will be used.

        Returns
        -------
        ndarray or scalar
            Value of the state variable(s).

        """
        if var_name not in self.state_vars:
            cls = self.__class__
            raise AttributeError(
                f"'{var_name}' is not in {cls.__qualname__}.state_vars (currently is {self.state_vars})."
                f"\nDid you set it using {cls.__qualname__}.state_vars = ['{var_name}', ...]?"
            )

        if edge_list is None:
            edge_list = self.wire_junctions

        try:
            return np.array(
                [self[edge[0]][edge[1]][var_name] for edge in edge_list]
            )
        except KeyError as e:
            raise ParameterNotSetError(
                f"'{var_name}' has not been set yet using `set_state_var`."
            ) from e

    def update_resistance(
        self,
        state_var_vals: npt.ArrayLike | list[npt.ArrayLike],
        edge_list: list[NWNEdge] | None = None,
    ) -> None:
        """
        Update the resistance of the nanowire network based on the provided
        state variable values. The resistance function should be set before
        calling this method.

        Parameters
        ----------
        state_var_vals : ndarray or list of ndarrays
            An array of values of the state variables to use in the resistance
            function. The should be in the same order as the state variables.
            If the resistance function takes multiple state variables, pass a
            list of arrays in the same order as `NanowireNetwork.state_vars`.

        edge_list : list of edges, optional
            List of edges to update the resistance for. If None, all wire
            junction edges will be used. In this case, the length of the
            `state_var_vals` array should be the same as the number of wire
            junctions.

        Returns
        -------
        ndarray
            Array of updated resistance values for each edge in the edge_list.

        """
        if self.resistance_function is None:
            raise ParameterNotSetError(
                "Resistance function attribute must be set before updating resistance."
            )

        if not isinstance(state_var_vals, list):
            state_var_vals = [state_var_vals]

        if edge_list is None:
            edge_list = self.wire_junctions

        R = self.resistance_function(self, *state_var_vals)
        attrs = {
            edge: {"conductance": 1 / R[i]} for i, edge in enumerate(edge_list)
        }
        nx.set_edge_attributes(self, attrs)

        return R

    def evolve(
        self,
        model: Callable[..., npt.ArrayLike],
        t_eval: npt.NDArray,
        args: tuple[Any, ...] = (),
        state_vars: Optional[list[str]] = None,
        ivp_options: dict = {},
    ) -> OdeResult:
        """
        Evolve the nanowire network using the given model and state variables.
        Returns the solution of the initial value problem solver from scipy
        at the given time points.

        Parameters
        ----------
        model : callable
            Model to use for the evolution. Should be a function with the
            signature `func(t, y, *args)` where `t` is the time, `y` is the
            state variable(s), and `args` are any additional arguments.
            Pre-implemented models include:
            [`mnns.models.HP_model`](models.md#mnns.models.HP_model),
            [`mnns.models.decay_HP_model`](models.md#mnns.models.decay_HP_model),
            and [`mnns.models.SLT_HP_model`](models.md#mnns.models.SLT_HP_model).

        t_eval : ndarray
            Time points to evaluate the solution at.

        state_vars : list of str, optional
            List of state variables to evolve. If not provided, all
            state variables in `self.state_vars` will be used.

        args : tuple, optional
            Additional arguments to pass to the model function. Most likely,
            you will need to provide args for the source node(s), drain node(s)
            and voltage function.

        ivp_options : dict, optional
            Additional keyword arguments to pass to the IVP solver.

        """
        if state_vars is None:
            state_vars = self.state_vars

        # Check if state variables are set
        if not all([self._state_vars_is_set[var] for var in state_vars]):
            raise ParameterNotSetError(
                "Not all state variables have not been set yet."
            )

        # Get initial state variable, if there are more than one, they
        # will be concatenated.
        y0 = np.hstack([self.get_state_var(var) for var in state_vars])

        # Set the tolerance value for the IVP solver
        if "atol" not in ivp_options.keys():
            ivp_options["atol"] = 1e-7
        if "rtol" not in ivp_options.keys():
            ivp_options["rtol"] = 1e-7

        t_span = (t_eval[0], t_eval[-1])

        # Solve how the state variables change over time
        sol = solve_ivp(
            model, t_span, y0, "DOP853", t_eval, args=args, **ivp_options
        )

        # Update the state variables
        split = np.split(sol.y[:, -1], len(state_vars))
        for var, new_vals in zip(state_vars, split):
            self.set_state_var(var, new_vals)

        return sol

    def __str__(self) -> str:
        d = {
            "Type": self.type,
            "Wires": self.n_wires,
            "Electrodes": self.n_electrodes,
            "Inner-wire junctions": self.n_inner_junctions,
            "Wire junctions": self.n_wire_junctions,
            "Length": f"{self.graph['length'] * self.units['l0']:#.4g} um ({self.graph['length']:#.4g} l0)",
            "Width": f"{self.graph['width'] * self.units['l0']:#.4g} um ({self.graph['width']:#.4g} l0)",
            "Wire Density": f"{self.graph['wire_density'] / self.units['l0']**2:#.4g} um^-2 ({self.graph['wire_density']:#.4g} l0^-2)",
        }
        # Get max key length
        m = max(map(len, list(d.keys())))

        # Create string representation
        s = "\n".join([f"{k:>{m}}: {v}" for k, v in d.items()])
        return s


def create_NWN(
    wire_length: float = (7.0 / 7),
    shape: tuple[float, float] = ((50.0 / 7), (50.0 / 7)),
    density: float = (0.3 * 7**2),
    seed: int = None,
    conductance: float = (0.1 / 0.1),
    capacitance: float = 1000,
    diameter: float = (50.0 / 50.0),
    resistivity: float = (22.6 / 22.6),
    units: dict[str, float] = None,
    angle_dist: str = "uniform",
    angle_kwargs: dict | None = None,
) -> NanowireNetwork:
    """
    Create a nanowire network represented by a NetworkX graph. Wires are
    represented by the graph's vertices, while the wire junctions are
    represented by the graph's edges.

    The nanowire network starts in the junction-dominated assumption (JDA), but
    can be converted to the multi-nodal representation (MNR) after creation.

    The desired density may not be attainable with the given shape, as there
    can only be a integer number of wires. Thus, the closest density to an
    integer number of wires is used and stored as an attribute (see
    [NWN Attributes](../../attributes.md) for more information).

    See [`mnns.NWNUnits`](units.md#mnns.units.NWNUnits) for the units used by
    the parameters.

    Parameters
    ----------
    wire_length : float, optional
        Length of each nanowire. Given in units of l0.

    shape : 2-tuple of float
        The shape of the nanowire network given in units of l0. Assumed to
        have the shape of (x-length, y-length).

        The x direction is labeled `length`, while the y direction is labeled
        `width`.

    density : float, optional
        Density of nanowires in the area determined by the width.
        Given in units of (l0)^-2.

    seed : int, optional
        Seed for random nanowire generation.

    conductance : float, optional
        The junction conductance of the nanowires where they intersect.
        Given in units of (Ron)^-1.

    capacitance : float, optional
        The junction capacitance of the nanowires where they intersect.
        Given in microfarads. (Currently unused)

    diameter : float, optional
        The diameter of each nanowire. Given in units of D0.

    resistivity : float, optional
        The resistivity of each nanowire. Given in units of rho0.

    units : dict, optional
        Dictionary of custom base units. Defaults to None which will use the
        default units given in `units.py`

    Returns
    -------
    NWN : Graph
        The created random nanowire network.

    """
    # Find total area in (l0)^2 of the nanowire network
    length = shape[0]
    width = shape[1]
    area = shape[0] * shape[1]

    # Get closest density with an integer number of wires.
    wire_num = round(area * density)
    density = wire_num / area

    # Get characteristic units
    units = NWNUnits(units)

    # Create NWN graph
    NWN = NanowireNetwork(
        wire_length=wire_length,
        length=length,
        width=width,
        shape=shape,
        wire_density=density,
        wire_num=0,
        junction_conductance=conductance,
        junction_capacitance=capacitance,
        wire_diameter=diameter,
        wire_resistivity=resistivity,
        electrode_list=[],
        lines=[],
        type="JDA",
        units=units,
        loc={},
        node_indices={},
    )

    # Create seeded random generator for testing
    rng = np.random.default_rng(seed)

    # Create the underlying line that represent the nanowires
    lines = []
    for _ in range(wire_num):
        lines.append(
            create_line(
                length=wire_length,
                xmax=length,
                ymax=width,
                rng=rng,
                angle_dist=angle_dist,
                angle_kwargs=angle_kwargs,
            )
        )

    # Create nanowire from lines
    add_wires(NWN, lines, [False] * len(lines))

    # Find junction density
    NWN.graph["junction_density"] = len(NWN.graph["loc"].keys()) / area

    return NWN
