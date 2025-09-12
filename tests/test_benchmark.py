import pytest
import numpy as np
from pathlib import Path

import mnns
import mnns.fromtext
from mnns.nanowire_network import NanowireNetwork


@pytest.fixture
def NWN_benchmark_JDA() -> NanowireNetwork:
    # Get benchmark file
    benchmark = Path(__file__).parent.resolve() / "test_networks/benchmark.txt"

    # Create nanowire network
    units = mnns.NWNUnits(
        {"Ron": 20.0, "rho0": 22.63676, "D0": 60.0, "l0": 1.0}
    )
    NWN = mnns.fromtext.create_NWN_from_txt(str(benchmark), units=units)
    return NWN


@pytest.fixture
def NWN_benchmark_MNR(NWN_benchmark_JDA: NanowireNetwork) -> NanowireNetwork:
    NWN = NWN_benchmark_JDA
    NWN.to_MNR()
    return NWN


@pytest.mark.parametrize("NWN", ["NWN_benchmark_JDA", "NWN_benchmark_MNR"])
def test_n_wires(NWN: str, request: pytest.FixtureRequest) -> None:
    NWN: NanowireNetwork = request.getfixturevalue(NWN)
    assert NWN.n_wires == 4


@pytest.mark.parametrize("NWN", ["NWN_benchmark_JDA", "NWN_benchmark_MNR"])
def test_n_electrodes(NWN: str, request: pytest.FixtureRequest) -> None:
    NWN: NanowireNetwork = request.getfixturevalue(NWN)
    assert NWN.n_electrodes == 2


@pytest.mark.parametrize("NWN", ["NWN_benchmark_JDA", "NWN_benchmark_MNR"])
def test_wire_density(NWN: str, request: pytest.FixtureRequest) -> None:
    NWN: NanowireNetwork = request.getfixturevalue(NWN)
    assert abs(NWN.wire_density - 4 / (3 * 5)) < 1e-8


@pytest.mark.parametrize("NWN", ["NWN_benchmark_JDA", "NWN_benchmark_MNR"])
def test_NWN_units(NWN: str, request: pytest.FixtureRequest) -> None:
    NWN: NanowireNetwork = request.getfixturevalue(NWN)
    units = {
        "v0": 1.0, "Ron": 20.0, "l0": 1.0, "D0": 60.0, "w0": 10.0,
        "rho0": 22.63676, "mu0": 1e-2, "Roff_Ron": 160, "i0": 0.05, "t0": 10000
    }
    for k1, k2 in zip(units.keys(), NWN.units.keys()):
        assert abs(units[k1] - NWN.units[k2]) < 1e-8


@pytest.mark.parametrize("NWN", ["NWN_benchmark_JDA", "NWN_benchmark_MNR"])
def test_electrodes(NWN: str, request: pytest.FixtureRequest) -> None:
    NWN: NanowireNetwork = request.getfixturevalue(NWN)
    electrodes = [(0,), (1,)]
    assert NWN.electrodes == electrodes


@pytest.mark.parametrize("NWN", ["NWN_benchmark_JDA", "NWN_benchmark_MNR"])
def test_n_wire_junctions(NWN: str, request: pytest.FixtureRequest) -> None:
    NWN: NanowireNetwork = request.getfixturevalue(NWN)
    assert NWN.n_wire_junctions == 5


def test_n_inner_junctions(NWN_benchmark_MNR: NanowireNetwork) -> None:
    NWN = NWN_benchmark_MNR
    assert NWN.n_inner_junctions == 4


def test_JDA_resistance(NWN_benchmark_JDA: NanowireNetwork) -> None:
    # Get benchmark network
    NWN = NWN_benchmark_JDA
    assert NWN.graph["type"] == "JDA"

    # Calculate JDA resistance
    V = 1.0
    sol = mnns.solve_network(NWN, (0,), (1,), V)
    R = V / sol[-1]
    R *= NWN.graph["units"]["Ron"]

    # Check for the correct JDA resistance
    R_JDA = 20 + 20 + 1 / (1 / (20 + 20) + 1 / 20)  # 160/3
    assert abs(R - R_JDA) < 1e-8


def test_MNR_resistance(NWN_benchmark_MNR: NanowireNetwork) -> None:
    # Get benchmark network
    NWN = NWN_benchmark_MNR
    assert NWN.graph["type"] == "MNR"
    units = NWN.graph["units"]

    # Calculate MNR resistance
    V = 1.0
    sol = mnns.solve_network(NWN, (0,), (1,), V)
    R = V / sol[-1]
    R *= units["Ron"]

    # Check for the correct MNR resistance
    const = units["rho0"] / (np.pi/4 * units["D0"]**2) * 1e3
    Rin1 = const * 1.2
    Rin2 = const * np.hypot(0.3, 0.3)
    Rin3 = const * np.hypot(1.5, 1.5)
    Rin4 = const * 1.5

    R_MNR = 20 + Rin1 + 20 + Rin2 + \
        1 / (1 / (Rin3 + 20) + 1 / (20 + Rin4 + 20))    # ~74.618
    assert abs(R - R_MNR) < 1e-8