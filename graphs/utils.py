import networkx as nx
import matplotlib.pyplot as plt
import sys

def create_graph(nodes, edges, edge_weights, node_weights, max_capacities):
    
    if len(edges) != len(edge_weights):
        raise Exception("Input error: edges and edge-weights have to be of the same length (one to one correspondence).")
    
    # Initialize the graph
    G=nx.Graph()
    
    # add edges
    elist = []
    for i, edge in enumerate(edges):
        elist.append((edge[0], edge[1], edge_weights[i]))
        
    G.add_weighted_edges_from(elist) 
    
    if len(nodes) != len(node_weights):
        raise Exception("Input error: nodes and node-weights have to be of the same length (one to one correspondence).")

    index = 0
    for  node, node_weight in zip(nodes, node_weights):
        G.node[node]["weight"] = node_weight
        G.node[node]["current_capacity"] = node_weight * max_capacities[index]
        G.node[node]["max_capacity"] =  max_capacities[index]
        index = index + 1
        

    return G


def draw_graph(G: nx.Graph, edges: list, weights: list,
               labels=None, graph_layout='shell',
               node_size=1600, node_color='blue', node_alpha=0.3,
               node_text_size=12,
               edge_color='blue', edge_alpha=0.3, edge_tickness=1,
               edge_text_pos=0.3,
               text_font='sans-serif'):
    # these are different layouts for the network you may try
    # shell seems to work best
    if graph_layout == 'spring':
        graph_pos=nx.spring_layout(G)
    elif graph_layout == 'spectral':
        graph_pos=nx.spectral_layout(G)
    elif graph_layout == 'random':
        graph_pos=nx.random_layout(G)
    else:
        graph_pos=nx.shell_layout(G)
        
     # draw graph    
    nx.draw_networkx_labels(G, graph_pos,font_size=node_text_size,
                                font_family=text_font)

    nx.draw_networkx_edges(G,graph_pos,width=edge_tickness,
                               alpha=edge_alpha,edge_color=edge_color)

    nx.draw_networkx_nodes(G,graph_pos,node_size=node_size, 
                               alpha=node_alpha, node_color=node_color)

    if labels is None:
            labels = range(len(edges))

    edge_labels = dict(zip(edges, weights))
    nx.draw_networkx_edge_labels(G, graph_pos, edge_labels=edge_labels, 
                                     label_pos=edge_text_pos)

        # show graph
    plt.show()    