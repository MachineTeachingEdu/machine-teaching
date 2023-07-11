# Helpers
import numpy as np
import pandas as pd

# Learning
from sklearn.decomposition import LatentDirichletAllocation
from scipy.cluster import hierarchy
from sklearn.mixture import GaussianMixture

# Plots
import matplotlib.pyplot as plt
import seaborn as sns


class Clustering():
    """ Class used to cluster the dataset using different methods with pre-defined arguments """
    # TODO: allow kwargs to be used to set different arguments in each method
    def __init__(self, X, k, **kwargs):
        self.X = X
        self.k = k
        self.kwargs = kwargs

        # Create result variables
        self.model = None
        self.document_topic = None

    def _normalize_per_row(matrix):
        """ Normalize sum per row """
        row_sums = matrix.sum(axis=1)
        matrix_norm = matrix / row_sums[:, np.newaxis]
        return matrix_norm

    def _sort_distribution(self, df, columns, min_score=0.3):
        """ Sort topic assignment distribution """
        ids = []

        for col in columns:
            ids = ids + df[df[col] > min_score].sort_values([col], ascending=False).index.tolist()

        for col in columns:
            ids = ids + df.sort_values([col], ascending=False).index.tolist()

        index = df.loc[ids].index.drop_duplicates()
        df_sorted = df.loc[index]
        return df_sorted

    def lda(self):
        """ Use LDA clustering method """
        model = LatentDirichletAllocation(n_components=self.k, max_iter=10, learning_method='batch')
        document_topic = model.fit_transform(self.X)
    #     docs_names = docs_id
#        topics = [d for d in range(1, document_topic.shape[1]+1)]
#        document_topic_norm = self._normalize_per_row(document_topic)
#        document_topic_df = pd.DataFrame(document_topic_norm, columns=topics)
#        data = document_topic_df[document_topic_df > 0.3]
#        clusters = {}
#        for i in document_topic_df.columns:
#            clusters[i] = data[i].dropna().index.tolist()

        # Save result variables
        self.model = model
        self.document_topic = document_topic

#        return model, document_topic, clusters
        return model, document_topic

    def hierarchical(self):
        """ Use hierarchical clustering method """
        # Create linkage matrix for original data
        model = hierarchy.linkage(self.X, 'ward')
        document_topic = hierarchy.fcluster(model, self.k, criterion='maxclust')
#        clusters = {}
#        for key in set(document_topic):
#            clusters[key] = np.where(document_topic == key)[0]

        # Save result variables
        self.model = model
        self.document_topic = document_topic

#        return model, document_topic, clusters
        return model, document_topic

    def gaussian_mixture(self):
        """ Use gaussian mixture clustering method """
        model = GaussianMixture(n_components=self.k).fit(self.X)
        document_topic = model.predict(self.X)
#        clusters = {}
#        for key in set(document_topic):
#            clusters[key] = np.where(document_topic == key)[0]

        # Save result variables
        self.model = model
        self.document_topic = document_topic

#        return model, document_topic, clusters
        return model, document_topic

    def plot_topic_distribution(self, topics=None, min_score=0.3):

        # If topic names are not set, set general topic name
        if not topics:
            topics = ["Topic %d" %d for d in range(1, self.k+1)]

        if not self.document_topic:
            raise AttributeError("Plotting not available yet. Please run one of"
                                 " the clustering functions before plotting results")

        # Normalize document per topic distribution per document (row)
        document_topic_norm = self._normalize_per_row(self.document_topic)

        document_topic_df = pd.DataFrame(document_topic_norm,
                                         index=range(0, self.X.shape[0]),
                                         columns=topics)

        # Sort docs according to topic assignment
        document_topic_df = self._sort_distribution(document_topic_df,
                                                    topics,
                                                    min_score=min_score)

        # Create a figure instance, and the two subplots
        fig = plt.figure(figsize=(12,12))
        ax1 = fig.add_subplot(211)
#        ax2 = fig.add_subplot(212)
        # fig, (ax1, ax2) = plt.subplots(2, 1, sharex='col', figsize=(12,12))


        sns.heatmap(document_topic_df, ax=ax1)
        ax1.xaxis.tick_top()
        plt.show()
