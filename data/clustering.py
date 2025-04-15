import numpy as np

import os
os.environ["OMP_NUM_THREADS"] = '1'

#Testing clustering for the NIST database lines
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


from typing import List, Tuple


def determine_clusters(data: List[float], kmax: int = 10):
    sil = []
    
    # dissimilarity would not be defined for a single cluster, thus, minimum number of clusters should be 2
    for k in range(2, kmax+1):
        kmeans = KMeans(n_clusters = k).fit(np.array(data).reshape(-1, 1))
        labels = kmeans.labels_
        sil.append(silhouette_score(np.array(data).reshape(-1, 1), labels, metric = 'euclidean'))
    
    return sil.index(max(sil)) + 2


def cluster(data: List[float], k: int):
    model = KMeans(n_clusters = k)
    model.fit(np.array(data).reshape(-1, 1))
    
    labels = model.predict(np.array(data).reshape(-1, 1))
    
    cluster_windows: List[Tuple[float, float]] = []
    
    for cluster in range(k):
        cluster_points = []
        for i, label in enumerate(labels):
            if label == cluster:
                cluster_points.append(data[i])
        
        cluster_windows.append((min(cluster_points), max(cluster_points)))
    
    return cluster_windows