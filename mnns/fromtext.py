#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Marcus Kasdorf
# Date:   July 15, 2021
"""
Not for production. Functions to create nanowire networks from text file.
"""

from typing import Dict
import numpy as np
from shapely.geometry import LineString

from .nanowires import add_wires
from .units import NWNUnits
from .nanowire_network import NanowireNetwork


def create_NWN_from_txt(
    filename: str,
    conductance: float = 1.0,
    diameter: float = 1.0,
    resistivity: float = 1.0,
    units: Dict[str, float] = None,
) -> NanowireNetwork:
    """
    Create a nanowire network represented by a NetworkX graph. Wires are
    represented by the graph's vertices, while the wire junctions are
    represented by the graph's edges.

    The text file input is assumed to be in two columns: x and y.
    Each wire is a pair of rows, one row containing the start point and the
    following containing the end point. The first two pairs of rows are the
    electrodes.

    Parameters
    ----------
    filename : str
        Text file containing the start and end locations of the wires.

    conductance : float, optional
        The junction conductance of the nanowires where they intersect.
        Given in units of (Ron)^-1.

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
    # Get coordinates from text file
    x, y = np.loadtxt(filename, unpack=True)

    # Convert to LineStrings
    line_list = []
    for i in range(0, len(x), 2):
        line_list.append(LineString([(x[i], y[i]), (x[i + 1], y[i + 1])]))

    # Find dimensions
    length = np.max(x) - np.min(x)
    width = np.max(y) - np.min(y)
    shape = (length, width)
    area = length * width

    # Get characteristic units
    units = NWNUnits(units)

    # Create NWN graph
    NWN = NanowireNetwork(
        wire_length=None,
        length=length,
        width=width,
        shape=shape,
        wire_density=0,
        wire_num=0,
        junction_conductance=conductance,
        junction_capacitance=None,
        wire_diameter=diameter,
        wire_resistivity=resistivity,
        electrode_list=[],
        lines=[],
        type="JDA",
        units=units,
        loc={},
        node_indices={},
    )

    # Split lines
    electrode_lines = line_list[0:2]
    wire_lines = line_list[2:]

    # Add wires to the graph
    add_wires(NWN, electrode_lines, [True] * len(electrode_lines))
    add_wires(NWN, wire_lines, [False] * len(wire_lines))

    # Find junction density
    NWN.graph["junction_density"] = len(NWN.graph["loc"].keys()) / area

    return NWN
