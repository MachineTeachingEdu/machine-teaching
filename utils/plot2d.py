# Data
import numpy as np
import pandas as pd

# Visualization
import matplotlib as mpl
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE, MDS
from sklearn.decomposition import PCA, TruncatedSVD
import matplotlib.cm as cm
import matplotlib.colors as mpl_colors
from sklearn.metrics.pairwise import cosine_distances

class Plot2D(object):
    """ Reduce data to 2 dimensions to plot it."""
    def __init__(self, clusters=None, doc_category=None, doc_id=None):
        if clusters is None:
            clusters = ['']

        self.doc_category = doc_category
        self.doc_id = doc_id
        self.cluster_names = clusters
        self.cluster_colors = {}
        self.seed = 0
        self.xs = None
        self.ys = None
        self.X = None
        self.solution_tsne = None

        self._set_clusters()
        # Generate seed
        self._generate_random_state()

    def _generate_random_state(self):
        self.seed = np.random.randint(2**32 - 1)

    def _set_clusters(self):
        """ Set clusters colors """
        # Set color for each pre-labelled cluster
        for i in range(len(self.cluster_names)):
            color = cm.tab10(i / len(self.cluster_names))
            color_hex = mpl_colors.rgb2hex(color[:3])
            self.cluster_colors[self.cluster_names[i]] = color_hex

    def reduce_pca(self, solution_sample):
        # convert two components as we're plotting points in a two-dimensional plane
        # we will also specify `random_state` so the plot is reproducible.
        self.solution_reduced = PCA(n_components=2, random_state=self.seed)

        pos = self.solution_reduced.fit_transform(solution_sample)  # shape (n_components, n_samples)
        self.X = pos
        self.xs, self.ys = pos[:, 0], pos[:, 1]

    def reduce_svd(self, solution_sample):
        # convert two components as we're plotting points in a two-dimensional plane
        # we will also specify `random_state` so the plot is reproducible.
        self.solution_reduced = TruncatedSVD(n_components=2, random_state=self.seed)

        pos = self.solution_reduced.fit_transform(solution_sample)  # shape (n_components, n_samples)
        self.X = pos
        self.xs, self.ys = pos[:, 0], pos[:, 1]

    def reduce_tsne(self, solution_sample):
        # convert two components as we're plotting points in a two-dimensional plane
        # we will also specify `random_state` so the plot is reproducible.
        self.solution_reduced = TSNE(n_components=2, metric='cosine',
                                     random_state=self.seed)

        pos = self.solution_reduced.fit_transform(solution_sample)  # shape (n_components, n_samples)
        self.X = pos
        self.xs, self.ys = pos[:, 0], pos[:, 1]

    def reduce_mds(self, solution_sample):
        # convert two components as we're plotting points in a two-dimensional plane
        # we will also specify `random_state` so the plot is reproducible.
        self.solution_reduced = MDS(n_components=2, dissimilarity='precomputed',
                                    random_state=self.seed)
        dissimilarity = cosine_distances(solution_sample)
        pos = self.solution_reduced.fit_transform(dissimilarity)  # shape (n_components, n_samples)
        self.X = pos
        self.xs, self.ys = pos[:, 0], pos[:, 1]

    def make_ellipses(self, gmm, ax, clusters):
        colors = []
        for i in range(clusters):
            color = cm.tab10(i / clusters)
            color_hex = mpl_colors.rgb2hex(color[:3])
            colors.append(color_hex)

        for n, color in enumerate(colors):
            if gmm.covariance_type == 'full':
                covariances = gmm.covariances_[n][:2, :2]
            elif gmm.covariance_type == 'tied':
                covariances = gmm.covariances_[:2, :2]
            elif gmm.covariance_type == 'diag':
                covariances = np.diag(gmm.covariances_[n][:2])
            elif gmm.covariance_type == 'spherical':
                covariances = np.eye(gmm.means_.shape[1]) * gmm.covariances_[n]
            v, w = np.linalg.eigh(covariances)
            u = w[0] / np.linalg.norm(w[0])
            angle = np.arctan2(u[1], u[0])
            angle = 180 * angle / np.pi  # convert to degrees
            v = 2. * np.sqrt(2.) * np.sqrt(v)
            ell = mpl.patches.Ellipse(gmm.means_[n, :2], v[0], v[1],
                                    180 + angle, color=color)
            ell.set_clip_box(ax.bbox)
            ell.set_alpha(0.5)
            ax.add_artist(ell)

    def plot(self, show_clusters=True, highlight=None, show=True,
             savefig=False, make_ellipses=False):
        # set up plot
        fig, ax = plt.subplots(figsize=(13,9)) # set size
        ax.margins(0.05) # Optional, just adds 5% padding to the autoscaling

        # Show pre-labeled (not by the student!!) samples with the respective color
        if show_clusters:
            #create data frame that has the result of the MDS plus the cluster numbers and titles
            df = pd.DataFrame(dict(x=self.xs, y=self.ys, label=self.doc_category,
                                title=self.doc_id))

            #group by cluster
            groups = df.groupby('label')


            #iterate through groups to layer the plot
            #note that I use the cluster_name and cluster_color dicts with the 'name' lookup to return the appropriate color/label
            for name, group in groups:
                # Skip math and string categories
                # They are all over the place. Not good manual label.
                if name == 'math' or name == 'string':
                    continue

                # Plot other categories
                ax.plot(group.x, group.y, marker='o', linestyle='', ms=12,
                        label=name, color=self.cluster_colors[name],
                        mec='none')
                ax.set_aspect('auto')
                ax.tick_params(\
                    axis= 'x',          # changes apply to the x-axis
                    which='both',      # both major and minor ticks are affected
                    bottom='on',      # ticks along the bottom edge are off
                    top='on',         # ticks along the top edge are off
                    labelbottom='on')
                ax.tick_params(\
                    axis= 'y',         # changes apply to the y-axis
                    which='both',      # both major and minor ticks are affected
                    left='on',      # ticks along the bottom edge are off
                    top='on',         # ticks along the top edge are off
                    labelleft='on')

            ax.legend(numpoints=1)  #show legend with only 1 point

        # Plot all docs
        plt.scatter(self.xs, self.ys, alpha=0)
        plt.title("Documents projected using PCA - First 2 components", fontsize=20)
        plt.xlabel("PC1", fontsize=14)
        plt.ylabel("PC2", fontsize=14)

        # If highlight is set, show observation with different color
        if highlight is not None:

            colors = []
            if isinstance(highlight, list):
                for i in range(len(highlight)):
                    color = cm.tab10(i / len(highlight))
                    color_hex = mpl_colors.rgb2hex(color[:3])
                    colors.append(color_hex)
            else:
                colors = ['r']

            plt.scatter(self.xs[highlight], self.ys[highlight],
                        color=colors, marker=r'$\star$', s=400)
        if make_ellipses:
            make_ellipses["ax"] = ax
            self.make_ellipses(**make_ellipses)

        if savefig:
            plt.savefig('images/' + savefig + '.eps', format='eps')
            plt.savefig('images/' + savefig + '.png', format='png')

        if show:
            plt.show() #show the plot
