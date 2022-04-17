import networkx as nx
from pymongo import MongoClient
client=MongoClient("localhost",27017)
db=client["SC"]
sc_tree=db["sc_tree"]
edge=db["edge"]

def get_edges(pkg,timestamp):
    edges = []
    for d in edge.find({"pkg":pkg}):
        if d["timestamp"] <= timestamp:
            edges.append((d["from"],d["to"]))
    return edges

edges=get_edges("torch","1585670399")
print(edges)
G = nx.Graph()
G.add_edges_from(edges)
#print(G.number_of_nodes())
b = nx.betweenness_centrality(G, k=None, normalized=False, weight=None, endpoints=False, seed=None)
c = nx.closeness_centrality(G)
d = nx.degree_centrality(G)
res_ = dict()
for k in b.keys():
	res_[k] = [b[k]]
for k in d.keys():
	res_[k].append(d[k]*(len(G)-1))

print(c)
print(res_)