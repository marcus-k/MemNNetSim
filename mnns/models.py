#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Marcus Kasdorf
# Date:   July 28, 2021
"""
Various dynamic models for nanowire networks.
"""

from __future__ import annotations

import numpy as np
import networkx as nx

import numpy.typing as npt
from .typing import *
from typing import Callable, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .nanowire_network import NanowireNetwork

from .calculations import solve_network


def resist_func(
    NWN: NanowireNetwork, w: float | npt.NDArray
) -> float | npt.NDArray:
    """
    Linear resistance function in nondimensionalized form.

    Obtained from Strukov et al. *Nature*, 2008, **453**, 80-83.

    Parameters
    ----------
    NWN : NanowireNetwork
        Nanowire network.

    w : ndarray or scalar
        Nondimensionalized state variable of the memristor element(s).

    Returns
    -------
    R : ndarray or scalar
        Resistance of the memristor element(s).

    """
    Roff_Ron = NWN.graph["units"]["Roff_Ron"]
    R = w * (1 - Roff_Ron) + Roff_Ron
    return R


def HP_model(
    t: float,
    x: npt.NDArray,
    NWN: NanowireNetwork,
    source_node: NWNNode | list[NWNNode],
    drain_node: NWNNode | list[NWNNode],
    voltage_func: Callable,
    window_func: Callable,
    solver: str = "spsolve",
    kwargs: Optional[dict] = None,
) -> npt.NDArray:
    """
    HP Model [1]. Provides the time derivative of the state variable `x` (the
    dimensionless version of `w`). Assumes voltage sources are used.

    Parameters
    ----------
    t : float
        Current time to solve at.

    x : ndarray
        Array containing the state variable `x` for each junction in the NWN.

    NWN : NanowireNetwork
        Input nanowire network graph.

    source_node : NWNNode or list of NWNNode
        Source node(s) of the input voltage.

    drain_node : NWNNode or list of NWNNode
        Drain/grounded node(s).

    voltage_func : Callable
        Function which inputs the time as a scalar and returns the voltage of
        all the source nodes as a scalar.

    window_func : Callable
        Function which inputs the state variable `x` as an array and returns
        the window function value as an array.

    solver : str
        SciPy sparse matrix equation solver.

    **kwargs
        Keyword arguments to pass to the SciPy sparse matrix equation solver.

    Returns
    -------
    dxdt : ndarray
        Array of the time derivative of the state variable `x`.

    References
    ----------
    [1] D. B. Strukov, G. S. Snider, D. R. Stewart and R. S. Williams,
        *Nature*, 2008, **453**, 80-83

    """
    if kwargs is None:
        kwargs = dict()

    # Update all wire junction resistances
    R = NWN.update_resistance(x)

    # Find applied voltage at the current time
    applied_V = voltage_func(t)

    # Solve for voltage at each node
    *V, I = solve_network(
        NWN, source_node, drain_node, applied_V, "voltage", solver, **kwargs
    )
    V = np.asarray(V)

    # Get start and end indices
    start, end = NWN.wire_junction_indices()

    # Find voltage differences
    v0 = V[start]
    v1 = V[end]
    V_delta = np.abs(v0 - v1) * np.sign(applied_V)

    # Find dw/dt
    dxdt = V_delta / R * window_func(x)

    return dxdt


def decay_HP_model(
    t: float,
    x: npt.NDArray,
    NWN: NanowireNetwork,
    source_node: NWNNode | list[NWNNode],
    drain_node: NWNNode | list[NWNNode],
    voltage_func: Callable,
    window_func: Callable,
    solver: str = "spsolve",
    kwargs: dict = None,
) -> npt.NDArray:
    """
    Decay HP Model [1]. Provides the time derivative of the state variable `x`
    (the dimensionless version of `w`). Assumes voltage sources are used.

    Requires `NWN.graph["tau"]` to be set to the decay constant value.

    Parameters
    ----------
    t : float
        Current time to solve at.

    x : ndarray
        Array containing the state variable `x` for each junction in the NWN.

    NWN : NanowireNetwork
        Input nanowire network graph.

    source_node : NWNNode or list of NWNNode
        Source node(s) of the input voltage.

    drain_node : NWNNode or list of NWNNode
        Drain/grounded node(s).

    voltage_func : Callable
        Function which inputs the time as a scalar and returns the voltage of
        all the source nodes as a scalar.

    window_func : Callable
        Function which inputs the state variable `x` as an array and returns
        the window function value as an array.

    solver : str
        SciPy sparse matrix equation solver.

    **kwargs
        Keyword arguments to pass to the SciPy sparse matrix equation solver.

    Returns
    -------
    dxdt : ndarray
        Array of the time derivative of the state variable `x`.

    References
    ----------
    [1] H. O. Sillin, R. Aguilera, H.-H. Shieh, A. V. Avizienis, M. Aono,
        A. Z. Stieg and J. K. Gimzewski, *Nanotechnology*, 2013, **24**, 384004.

    """
    if kwargs is None:
        kwargs = dict()

    # Update all wire junction resistances
    R = NWN.update_resistance(x)

    # Find applied voltage at the current time
    applied_V = voltage_func(t)

    # Solve for voltage at each node
    *V, I = solve_network(
        NWN, source_node, drain_node, applied_V, "voltage", solver, **kwargs
    )
    V = np.array(V)

    # Get start and end indices
    start, end = NWN.wire_junction_indices()

    # Find voltage differences
    v0 = V[start]
    v1 = V[end]
    V_delta = np.abs(v0 - v1) * np.sign(applied_V)

    # Get decay constant
    tau = NWN.graph["tau"]

    # Find dw/dt
    dxdt = (V_delta / R * window_func(x)) - (x / tau)

    return dxdt


def SLT_HP_model(
    t: float,
    y: npt.NDArray,
    NWN: NanowireNetwork,
    source_node: NWNNode | list[NWNNode],
    drain_node: NWNNode | list[NWNNode],
    voltage_func: Callable,
    window_func: Callable,
    solver: str = "spsolve",
    kwargs: Optional[dict] = None,
) -> npt.NDArray:
    """
    SLT HP Model [1]. Provides the time derivative of the state variable `x`
    (the dimensionless version of `w`), `tau`, and `epsilon`. Assumes that
    these state variable are concatenated into a single 1D array input.

    Assumes voltage sources are used.

    Requires `NWN.graph["tau"]` to be set to the decay constant value.

    Parameters
    ----------
    t : float
        Current time to solve at.

    y : ndarray
        Array containing the state variables `x`, `tau`, and `epsilon` for each
        junction in the NWN concatenated into a single 1D array input.

    NWN : NanowireNetwork
        Input nanowire network graph.

    source_node : NWNNode or list of NWNNode
        Source node(s) of the input voltage.

    drain_node : NWNNode or list of NWNNode
        Drain/grounded node(s).

    voltage_func : Callable
        Function which inputs the time as a scalar and returns the voltage of
        all the source nodes as a scalar.

    window_func : Callable
        Function which inputs the state variable `x` as an array and returns
        the window function value as an array.

    solver : str
        SciPy sparse matrix equation solver.

    **kwargs
        Keyword arguments to pass to the SciPy sparse matrix equation solver.

    Returns
    -------
    dydt : ndarray
        Array of the time derivative of the state variables `x`, `tau`, and
        `epsilon`, concatenated into a 1D array.

    References
    ----------
    [1] L. Chen, C. Li, T. Huang, H. G. Ahmad and Y. Chen, *Physics Letters A*,
        2014, **378**, 2924-2930

    """
    if kwargs is None:
        kwargs = dict()

    # Unpack values
    w, tau, epsilon = np.split(y, 3)
    sigma, theta, a = NWN.graph["sigma"], NWN.graph["theta"], NWN.graph["a"]

    # Update all wire junction resistances
    R = NWN.update_resistance(w)

    # Find applied voltage at the current time
    applied_V = voltage_func(t)

    # Solve for voltage at each node
    *V, I = solve_network(
        NWN, source_node, drain_node, applied_V, "voltage", solver, **kwargs
    )
    V = np.asarray(V)

    # Get start and end indices
    start, end = NWN.wire_junction_indices()

    # Find voltage differences
    v0 = V[start]
    v1 = V[end]
    V_delta = np.abs(v0 - v1) * np.sign(applied_V)

    # Find derivatives
    l = V_delta / R
    dw_dt = (l - ((w - epsilon) / tau)) * window_func(w)
    dtau_dt = theta * l * (a - w)
    deps_dt = sigma * l * window_func(w)
    dydt = np.hstack((dw_dt, dtau_dt, deps_dt))

    return dydt


# Legacy functions
def set_SLT_params(NWN: NanowireNetwork, sigma, theta, a):
    NWN.graph["sigma"] = sigma
    NWN.graph["theta"] = theta
    NWN.graph["a"] = a


set_chen_params = set_SLT_params
