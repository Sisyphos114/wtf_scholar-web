# Find papers in mds/ of the same content (checks first 1000 letters)
import os
import numpy as np
from itertools import combinations
from leven import levenshtein
from scipy.spatial.distance import squareform

docnames = []
docs = []
dirname = 'md'
for filename in os.listdir(dirname):
    docnames.append( filename )
    filepath = os.path.join(dirname, filename)
    content = open(filepath, "r").read()
    docs.append( content[:1000] )

distances = [levenshtein(i, j) for (i, j) in combinations(docs, 2)]
distance_matrix = squareform(distances)
np.save("dist", distance_matrix)

#distance_matrix = np.load("dist.npy")

next_clus_num = 1
clusters = np.zeros(len(docs))
for i in range(len(docs)-1):
    for j in range(i+1, len(docs)-1):
        if distance_matrix[i,j] < 10:
            if clusters[i] == 0 and clusters[j] == 0:
                clusters[i] = clusters[j] = next_clus_num
                next_clus_num += 1
            elif clusters[i] != 0 or clusters[j] != 0:
                if clusters[i] == 0:
                    clusters[i] = next_clus_num
                if clusters[j] == 0:
                    clusters[j] = next_clus_num
                clus = np.min([clusters[i], clusters[j]])
                for k in range(len(clusters)-1):
                    if clusters[k] == clusters[i] or clusters[k] == clusters[j]:
                        clusters[k] = clus

X = sorted([(doc, int(cls)) for cls, doc in zip(clusters, docnames) if cls != 0], key=lambda x:x[1])
for c in list(set([cls for _, cls in X])):
    dups = sorted([name for name, cls in X if cls == c], key=lambda x:int(x.split('.')[0]))
    for dup in dups[1:]:
        print(dup)
