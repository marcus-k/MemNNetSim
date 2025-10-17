#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Marcus Kasdorf
# Date:   July 1, 2021
"""
Characteristic units for a nanowire network.
"""


class NWNUnits:
    """
    Class for characteristic units for a nanowire network. Acts similar to a
    dictionary with key-value pairs to access units.

    The default units for the nanowire network are:
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

    Parameters
    ----------
    new_units : NWNUnits or dict, optional
        Dictionary of any custom units to use. Only base units can be altered.

    Attributes
    ----------
    units : dict
        Dictionary of characteristic units.

    """

    default_units = {
        "v0": 1.0,
        "Ron": 10.0,
        "l0": 7.0,
        "D0": 50.0,
        "w0": 10.0,
        "rho0": 22.6,
        "mu0": 1e-2,
        "Roff_Ron": 160,
    }
    desc = {
        "v0": "V, Voltage",
        "Ron": "Ω, ON Junction resistance",
        "l0": "μm, Wire length",
        "D0": "nm, Wire diameter",
        "w0": "nm, Junction length (2x Wire coating thickness)",
        "rho0": "nΩm, Wire resistivity",
        "mu0": "μm^2 s^-1 V^-1, Ion mobility",
        "Roff_Ron": "Off-On Resistance ratio",
        "i0": "A, Current",
        "t0": "μs, Time",
    }

    settable_units = ("v0", "Ron", "l0", "D0", "w0", "rho0", "mu0", "Roff_Ron")
    not_settable_units = ("i0", "t0")

    def __init__(self, new_units: dict[str, float] = None):
        if isinstance(new_units, NWNUnits):
            # Copy from previous NWNUnits instance
            self.units = new_units.units.copy()
            self.update_derived_units()

        else:
            # Set default and derived units
            self.units = self.default_units.copy()
            self.update_derived_units()

            # Update units and derived units for any new units
            if new_units is not None:
                for key, value in new_units.items():
                    self[key] = value

    def __setitem__(self, key: str, value: float):
        if key in self.settable_units:
            self.units[key] = value
        elif key in self.not_settable_units:
            raise ValueError(f"Cannot set a derived unit: {key}")
        else:
            raise KeyError(f"Unknown unit {key}.")

        self.update_derived_units()

    def __getitem__(self, key: str):
        return self.units[key]

    def update_derived_units(self):
        # A, Current
        self.units["i0"] = self.units["v0"] / self.units["Ron"]
        # μs, Time
        self.units["t0"] = self.units["w0"] ** 2 / (
            self.units["mu0"] * self.units["v0"]
        )

    def keys(self):
        return self.units.keys()

    def values(self):
        return self.units.values()

    def items(self):
        return self.units.items()

    def __repr__(self) -> str:
        # Get max key length
        m1 = max(map(len, list(self.units.keys())))
        m2 = max(map(len, list(map(str, self.units.values()))))

        # Create string representation
        s = "\n".join(
            [
                f"{k:>{m1}}: {v:<{m2}} {self.desc[k]}"
                for k, v in self.units.items()
            ]
        )
        return s

    def __eq__(self, other) -> bool:
        return self.units == other


def get_units(new_units: dict[str, float] = None) -> dict[str, float]:
    """
    Deprecated. Use [`mnns.NWNUnits`](units.md#mnns.units.NWNUnits)
    instead.

    Returns the characteristic units for a nanowire network.

    Parameters
    ----------
    new_units : dict, optional
        Dictionary of any custom units to use. Only base units can be altered.

    Returns
    -------
    units : dict
        Dictionary of characteristic units.

    """
    if new_units is None:
        new_units = dict()

    # Base units
    units = {  # Unit, Description
        "v0": 1.0,  # V, Voltage
        "Ron": 10.0,  # Ω, ON junction resistance
        "l0": 7.0,  # μm, Wire length
        "D0": 50.0,  # nm, Wire diameter
        "w0": 10.0,  # nm, Junction length (2x Wire coating thickness)
        "rho0": 22.6,  # nΩm, Wire resistivity
        "mu0": 1e-2,  # μm^2 s^-1 V^-1, Ion mobility
        "Roff_Ron": 160,  # none, Off-On Resistance ratio
    }

    # Add any custom units
    units.update(new_units)

    # Derived units
    units["i0"] = units["v0"] / units["Ron"]  # A, Current
    units["t0"] = units["w0"] ** 2 / (units["mu0"] * units["v0"])  # μs, Time

    return units
