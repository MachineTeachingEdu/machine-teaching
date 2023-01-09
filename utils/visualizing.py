# Data
import numpy as np
import pandas as pd

# Visualization
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import matplotlib.cm as cm
import matplotlib.colors as mpl_colors

class Plot2D():
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

        self._set_clusters()
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

    def reduce(self, solution_sample):
        # convert two components as we're plotting points in a two-dimensional plane
        # we will also specify `random_state` so the plot is reproducible.
        self.seed = self._generate_random_state()
        solution_tsne = TSNE(n_components=2, metric='cosine',
                             random_state=self.seed)
        pos = solution_tsne.fit_transform(solution_sample)  # shape (n_components, n_samples)
        self.xs, self.ys = pos[:, 0], pos[:, 1]

    def plot(self, show_clusters=True, highlight=None):
        # set up plot
        fig, ax = plt.subplots(figsize=(17, 9)) # set size
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
                        mec='none', alpha=0.5)
                ax.set_aspect('auto')
                ax.tick_params(\
                    axis= 'x',          # changes apply to the x-axis
                    which='both',      # both major and minor ticks are affected
                    bottom='off',      # ticks along the bottom edge are off
                    top='off',         # ticks along the top edge are off
                    labelbottom='off')
                ax.tick_params(\
                    axis= 'y',         # changes apply to the y-axis
                    which='both',      # both major and minor ticks are affected
                    left='off',      # ticks along the bottom edge are off
                    top='off',         # ticks along the top edge are off
                    labelleft='off')

            ax.legend(numpoints=1)  #show legend with only 1 point

        # Plot all docs
        plt.scatter(self.xs, self.ys, alpha=0.5)

        # If highlight is set, show observation with different color
        if highlight is not None:
            plt.scatter(self.xs[highlight], self.ys[highlight],
                        color='r', marker='x', s=12)


        plt.show() #show the plot
