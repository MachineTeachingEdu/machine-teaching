# Helpers
import numpy as np
import pandas as pd

# Learning
from sklearn.decomposition import LatentDirichletAllocation, NMF
from scipy.cluster import hierarchy
from sklearn.mixture import GaussianMixture
from sklearn.cluster import SpectralClustering

# Plots
import matplotlib.pyplot as plt
import seaborn as sns


class Clustering(object):
    """ Class used to cluster the dataset using different methods with pre-defined arguments """
    # TODO: allow kwargs to be used to set different arguments in each method
    def __init__(self, X, k, **kwargs):
        self.X = X
        self.k = k
        self.kwargs = kwargs
        self.seed = 0

        # Create result variables
        self.model = None
        self.document_topic = None
        self.word_topic = None

        # Generate seed
        self._generate_random_state()

    def _generate_random_state(self):
        self.seed = np.random.randint(2**32 - 1)

    def _normalize_per_row(self, matrix):
        """ Normalize sum per row """
        row_sums = matrix.sum(axis=1)
        matrix_norm = matrix / row_sums[:, np.newaxis]
        return matrix_norm

    def _sort_distribution(self, df, columns, min_score=0.3):
        """ Sort topic assignment distribution """
        ids = []
        for col in columns:
            ids_col = np.where(df.idxmax(axis=1) == col)
            ids_col = df.loc[ids_col].sort_values([col], ascending=False).index.tolist()
            ids += ids_col

        df_sorted = df.loc[ids]
        return df_sorted

    def nmf(self):
        """ Use NMF clustering method """
        model = NMF(n_components=self.k, random_state=self.seed)
        document_topic = model.fit_transform(self.X)
        word_topic = model.components_.T

        # Save result variables
        self.model = model
        self.document_topic = document_topic
        self.word_topic = word_topic

#        return model, document_topic, clusters
        return model, document_topic, word_topic

    def lda(self):
        """ Use LDA clustering method """
        model = LatentDirichletAllocation(n_components=self.k, max_iter=10,
                                          learning_method='batch',
                                          random_state=self.seed)
        document_topic = model.fit_transform(self.X)
        word_topic = model.components_.T

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
        self.word_topic = word_topic

#        return model, document_topic, clusters
        return model, document_topic, word_topic

    def hierarchical(self):
        """ Use hierarchical clustering method """
        # Create linkage matrix for original data
        model = hierarchy.linkage(self.X, 'ward', metric=self.kwargs['metric'])
        clusters = hierarchy.fcluster(model, self.k, criterion='maxclust')
        document_topic = np.zeros((self.X.shape[0], self.k))
        for row in range(len(clusters)):
            document_topic[row, clusters[row]-1] = 1

        word_topic = None

        # Save result variables
        self.model = model
        self.document_topic = document_topic
        self.word_topic = word_topic

        return model, document_topic, word_topic

    def gaussian_mixture(self):
        """ Use gaussian mixture clustering method """
        model = GaussianMixture(n_components=self.k,
                                random_state=self.seed).fit(self.X)
        document_topic = model.predict_proba(self.X)
        word_topic = model.means_
#        clusters = {}
#        for key in set(document_topic):
#            clusters[key] = np.where(document_topic == key)[0]

        # Save result variables
        self.model = model
        self.document_topic = document_topic
        self.word_topic = word_topic

#        return model, document_topic, clusters
        return model, document_topic, word_topic

    def spectral_clustering(self):
        """ Use spectral clustering method """
        model = SpectralClustering(n_clusters=self.k,
                                   random_state=self.seed,
                                   assign_labels="discretize").fit(self.X)
        clusters = model.fit_predict(self.X)
        document_topic = np.zeros((self.X.shape[0], self.k))
        for row in range(len(clusters)):
            document_topic[row, clusters[row]] = 1

        word_topic = None

        # Save result variables
        self.model = model
        self.document_topic = document_topic
        self.word_topic = word_topic

#        return model, document_topic, clusters
        return model, document_topic, word_topic

    def _plot_distribution(self, topic_distribution, xlabel,
                           topics=None, min_score=0.3, cmap=sns.cm.rocket,
                           ylabel=None, title=None, savefig=None):
        # If topic names are not set, set general topic name
        if not topics:
            topics = ["Topic %d" %d for d in range(1, self.k+1)]

        if topic_distribution.any() == None:
            raise AttributeError("Plotting not available yet. Please run one of"
                                 " the clustering functions before plotting results")

        # Normalize document per topic distribution per document (row)
        topic_distribution_norm = self._normalize_per_row(topic_distribution)

        topic_distribution_df = pd.DataFrame(topic_distribution_norm,
                                             index=xlabel,
                                             columns=topics)

        # Sort docs according to topic assignment
        topic_distribution_df = self._sort_distribution(topic_distribution_df,
                                                        topics,
                                                        min_score=min_score)

        # Create a figure instance, and the two subplots
        fig = plt.figure(figsize=(8,10))
        ax = fig.add_subplot(111)

        sns.heatmap(topic_distribution_df, ax=ax, cmap=cmap, cbar_kws={'label': 'Topic weight'})
        # use matplotlib.colorbar.Colorbar object
        cbar = ax.collections[0].colorbar
        # here set the labelsize by 20
        cbar.ax.tick_params(labelsize=14)
        cbar.ax.set_ylabel("Topic weight", fontsize=14)
        ax.tick_params(labelsize=12)
        ax.xaxis.tick_top()
        ax.tick_params('x', labelrotation=45)

        if ylabel:
            ax.set_ylabel(ylabel, fontsize=14)

        if title:
            ax.set_title(title, fontsize=18, y=1.04)
        if savefig:
            plt.savefig('images/' + savefig + '.eps', format='eps')
            plt.savefig('images/' + savefig + '.png', format='png')

        plt.show()
        plt.tight_layout()
        return topic_distribution_df


    def plot_topic_distribution(self, **kwargs):
        self._plot_distribution(self.document_topic, range(0, self.X.shape[0]),
                                **kwargs)


    def plot_word_distribution(self, words, **kwargs):
        kwargs["xlabel"] = ["Topic %d" %d for d in range(1,self.k+1)]
        df = self._plot_distribution(self.word_topic, **kwargs)
        return df
