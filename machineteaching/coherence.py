from itertools import permutations
import numpy as np

def calculate_umass_coherence(X, word_topic, clusters, k, N=5):
    k_coherence = []
    for idx_cluster in range(k):
        cluster_data = X[clusters == idx_cluster]

        # If there aren't any documents assigned to the cluster, skip it
        if cluster_data.shape[0] == 0:
            continue

        # Calculate cooccurence matrix
        cluster_data[np.where(cluster_data > 1)] = 1
        cooccurence = np.dot(cluster_data.T, cluster_data)

        # For each topic, get N top words
        idx = word_topic[:,idx_cluster].argsort()[::-1][:N]
        perms = permutations(idx, 2)
        k_score = []
        for i,j in perms:
            if cooccurence[i,i] == 0:
                continue
            score = np.log((cooccurence[i,j]+0.01)/cooccurence[i,i])
            k_score.append(score)
        k_topic = np.mean(np.asarray(k_score))
        k_coherence.append(k_topic)
    return k_coherence, np.median(k_coherence), np.std(k_coherence)
