# Nanowire Network Attributes

Nanowire network (NWN) objects are represented internally as standard [NetworkX](https://networkx.org/documentation/stable/tutorial.html)
graphs. All the attributes are listed below. 

## NWN Graph

Attributes accessed via `NWN.graph["attribute"]`. Most of these are set from
the NWN constructor [create_NWN()](reference/mnns/nanowire_network.md#mnns.nanowire_network.create_NWN).

| Attribute              | Description                                                                                                                    |
|------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| `wire_length`          | Length of each nanowire. (l₀)                                                                                                  |
| `length`               | x-length of the nanowire network. (l₀)                                                                                         |
| `width`                | y-length of the nanowire network. (l₀)                                                                                         |
| `size`                 | Size of the network (`length * width`). (l₀²)                                                                                  |
| `wire_density`         | Wire density of the network. (l₀)                                                                                              |
| `wire_num`             | Number of wires in the network.                                                                                                |
| `junction_conductance` | Conductance of the junctions. (Rₒₙ⁻¹)                                                                                          |
| `wire_diameter`        | Diameter of each nanowire. (D₀)                                                                                                |
| `wire_resistivity`     | Resistivity of each nanowire. (ρ₀)                                                                                             |
| `electrode_list`       | List of electrode nodes.                                                                                                       |
| `lines`                | List of the Shapely LineStrings uses to represent the nanowires.                                                               |
| `type`                 | Type of nanowire network representation (`"JDA"` or `"MNR"`).                                                                  |
| `units`                | Dictionary of characteristic units for the NWN. See [Units](usage.md#units).                                                   |
| `loc`                  | (JDA only) Dictionary with a two-tuple of node indices as keys and Shapely Points as values. Maps junctions to their location. |
| `junction_density`     | Junction density of the network. (l₀⁻²)                                                                                        |
| `node_indices`         | Dictionary with nodes as keys and indices as values. Maps nodes to a unique index.                                             |

## NWN Nodes

The NWN [nodes](https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.nodes.html) 
are tuples of integers. In the junction-dominated assumption (JDA) NWN graph 
representation, these are one-tuples. In the multi-nodal representation (MNR) 
NWN graph representation, they can either be two-tuples in the general case, 
or one-tuples in the case of electrodes or wires with only one junction.

| Attribute   | Description                                             |
|-------------|---------------------------------------------------------|
| `electrode` | Whether or not this node is an electrode.               |
| `loc`       | (MNR only) Location of the junction as a Shapely Point. |

## NWN Edges

The NWN [edges](https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.edges.html) 
represent the junctions between nanowires for JDA NWNs, or additionally 
inner-wire connections between nodes for MNR NWNs. They are just a two-tuple 
of NWN Nodes.

| Attribute     | Description                                    |
|---------------|------------------------------------------------|
| `conductance` | Maximum conductance of the nanowire junction.  |
| `type`        | Either "junction" (JDA, MNR) or "inner" (MNR). |

Using [`NWN.set_state_var("name")`](reference/mnns/nanowire_network.md#mnns.nanowire_network.NanowireNetwork.set_state_var),
an edge attribute `name` will be added to store that state variable value.