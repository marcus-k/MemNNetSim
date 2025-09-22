import pytest
from pathlib import Path

import mnns
import mnns.fromtext
import numpy as np
import networkx as nx
from collections import Counter

from mnns.nanowire_network import NanowireNetwork


@pytest.fixture
def NWN_benchmark_JDA() -> NanowireNetwork:
    # Get benchmark file
    current_path = Path(__file__).parent.resolve()
    benchmark = current_path.joinpath("test_networks/benchmark.txt")

    # Create nanowire network
    units = {"Ron": 20.0, "rho0": 22.63676, "D0": 60.0, "l0": 1.0}
    NWN = mnns.fromtext.create_NWN_from_txt(str(benchmark), units=units)
    return NWN


@pytest.fixture
def NWN_benchmark_MNR(NWN_benchmark_JDA: NanowireNetwork) -> NanowireNetwork:
    NWN = NWN_benchmark_JDA
    NWN.to_MNR()
    return NWN


@pytest.fixture
def NWN_test1() -> NanowireNetwork:
    NWN = mnns.create_NWN(shape=(8, 5), seed=123)
    mnns.add_electrodes(
        NWN, ["left", 2, 1, [-0.5, 0.5]], ["right", 2, 1, [-0.5, 0.5]]
    )
    return NWN


def test_shortest_path() -> None:
    NWN = mnns.create_NWN(seed=123)
    assert NWN.graph["type"] == "JDA"

    path_len, path = nx.single_source_dijkstra(NWN, (33,), (138,))
    ans = [(33,), (330,), (373,), (622,), (420,), (76,), (21,), (723,), (19,), 
        (232,), (123,), (422,), (308,), (166,), (406,), (53,), (736,), (138,)]

    assert path_len == len(ans) - 1
    assert path == ans


@pytest.mark.parametrize("NWN", ["NWN_benchmark_JDA", "NWN_test1"])
def test_MNR_node_count(NWN: str, request: pytest.FixtureRequest) -> None:
    NWN: NanowireNetwork = request.getfixturevalue(NWN)
    assert NWN.graph["type"] == "JDA"
    NWN.to_MNR()

    # Number of wire junction edges
    n_wire_junctions = Counter(nx.get_edge_attributes(NWN, "type").values())["junction"]

    # Number of edges connected to an electrode
    n_edges_electrode = len(NWN.edges(NWN.graph["electrode_list"]))

    # Number of connected electrodes
    n_connected_electrodes = len([node for node, deg in NWN.degree(NWN.graph["electrode_list"]) if deg > 0])

    # Number of isolated wires
    n_isolated_wires = len([x for x in nx.connected_components(NWN) if len(x) == 1])

    # Compare the number of nodes obtained via edge and node count
    node_count = 2 * n_wire_junctions \
        - n_edges_electrode \
        + n_connected_electrodes \
        + n_isolated_wires
    
    assert node_count == NWN.number_of_nodes()


@pytest.mark.parametrize("NWN", ["NWN_benchmark_JDA", "NWN_test1"])
def test_state_vars(NWN: str, request: pytest.FixtureRequest) -> None:
    """Test assigning state variables."""
    NWN: NanowireNetwork = request.getfixturevalue(NWN)
    assert NWN.graph["type"] == "JDA"

    # Parameters
    value = 0.05
    var = "x"

    # Set state vars
    NWN.state_vars = [var]
    NWN.set_state_var(var, value)

    # Obtain values manually
    data = np.array(list(nx.get_edge_attributes(NWN, var).values()))

    # Check expected
    assert len(data) == NWN.n_wire_junctions
    assert np.all(data == value)

    # Check get state var
    data = NWN.get_state_var(var)

    # Check expected
    assert len(data) == NWN.n_wire_junctions
    assert np.all(data == value)




    