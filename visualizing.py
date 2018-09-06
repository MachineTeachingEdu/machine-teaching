# Visualization
#from sklearn.manifold import TSNE
import matplotlib.cm as cm
import matplotlib.colors as mpl_colors

class Plot2D():
    """ Reduce data to 2 dimensions to plot it."""
    def __init__(self, clusters=None):
        if clusters is None:
            clusters = ['']

        self.cluster_names = clusters
        self.clusters_colors = {}

    def set_clusters(self):
        """ Set clusters colors """
        # Set color for each pre-labelled cluster
        for i in range(len(self.cluster_names)):
            color = cm.tab10(i / len(self.cluster_names))
            color_hex = mpl_colors.rgb2hex(color[:3])
            self.cluster_colors[self.cluster_names[i]] = color_hex
