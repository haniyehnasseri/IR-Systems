import networkx as nx
import matplotlib.pyplot as plt

## pagerank calculation

G = nx.read_edgelist("Cit-HepTh.txt", comments='#', delimiter='\t', create_using=nx.DiGraph)

pr = nx.pagerank(G, max_iter=1000, alpha=0.85)

#print(pr)

sorted_pr = dict(sorted(pr.items(), key=lambda item: item[1]))

#print(sorted_pr)

## rel


citations_dict = dict()

for n in G.nodes:
    citations_dict[n] = len(list(G.predecessors(n)))

sorted_citations_dict = dict(sorted(citations_dict.items(), key=lambda item: item[1]))

x_value = list(G.nodes)

citation_y = list()
pagerank_y = list()

for n in G.nodes:
    citation_y.append(citations_dict[n])
    pagerank_y.append(pr[n])

fig, ax1 = plt.subplots()

ax2 = ax1.twinx()

ax1.plot(x_value, citation_y, 'g-')
ax2.plot(x_value, pagerank_y, 'b-')

plt.show()

## HITS

hubs, authorities = nx.hits(G, max_iter = 1000, normalized = True)
sorted_authorities = dict(sorted(authorities.items(), key=lambda item: item[1]))

print(sorted_authorities)
