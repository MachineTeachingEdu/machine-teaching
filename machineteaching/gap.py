from scipy.spatial.distance import pdist
import scipy
import numpy as np
from clustering import Clustering

class Gap(object):
    def __init__(self, data, k, nrefs=20, distance='cosine'):
        self._prepare_ref_dataset(data, nrefs)
        self.k = k
        self.X = data
        self.distance = distance

    def _prepare_ref_dataset(self, data, nrefs=20):
        shape = data.shape
        # Set bounding box
        tops = data.max(axis=0)
        bots = data.min(axis=0)

        # Generate distribution
        self.refs = scipy.random.random_sample(size=(shape[0],shape[1],nrefs))

        # Set offset for random uniform samples to be inside bounding boxes
        dists = scipy.matrix(scipy.diag(tops-bots))
        for i in range(nrefs):
            self.refs[:,:,i] = self.refs[:,:,i]*dists+bots

        return self.refs

    def calculate_wk(self, X, y):
        """ Calculate nr, dr and wk """
        min_k = np.array(y).min()
        max_k = np.array(y).max()
        wk = []

        for i in range(min_k, max_k+1):
            # Calculate Dr for each cluster
            obs_idx = np.where(y == i)[0]
            nr = obs_idx.shape[0]

    #         if nr == 0:
    #             raise TypeError("There are empty clusters.")

            # Get pairwise distance
            dist = pdist(X[obs_idx], self.distance).sum()

            # Calculate Wk
            wki = dist/(2*nr)
            wk.append(wki)

        return np.array(wk).sum()

    def calculate_ref_wk(self, method, k):
        self.wk_refs = []

        for ref in range(self.refs.shape[2]):
            ref_clustering = Clustering(self.refs[:,:,ref], k)
            model, document_topic, word_topic = getattr(ref_clustering, method)()
            clusters = ref_clustering.document_topic.argmax(axis=1)
            wk_ref = self.calculate_wk(self.refs[:,:,ref], clusters)
            log_wk_ref = np.log(wk_ref)
            self.wk_refs.append(log_wk_ref)

        return self.wk_refs

    def calculate_gap(self, clustering, method):
        # Calculate Wk for original data
        clusters = clustering.document_topic.argmax(axis=1)
        wk = self.calculate_wk(self.X, clusters)
        log_wk = np.log(wk)

        # Calculate Wk for reference distribution
        wk_refs = self.calculate_ref_wk(method, self.k)
        wkb = np.array(wk_refs)
        wkb_sum = wkb.sum()
        wkb_std = wkb.std()
        B = wkb.shape[0]

        # Calculate Gap
        gap_k = (1/B*wkb_sum) - log_wk
        error = wkb_std*np.sqrt(1+(1/B))

        return gap_k, error

def define_k(gaps, error):
    for i in range(2,len(gaps)):
        k = i-2
        gapi = gaps[k]
        gapi1 = gaps[k+1]
        std = error[k+1]

        if gapi >= (gapi1-std):
            print("k = %d" % (k+2))
            break

    diff = np.array(gaps) - np.array(error)
    gaps[1:] = gaps[:-1]
    gap_diff = np.array(gaps) > diff
    k = np.argmax(gap_diff[1:] == True)
    return k+2
