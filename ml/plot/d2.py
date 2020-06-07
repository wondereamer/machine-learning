
# %%
import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Cursor
from ml.plot import d1


def scatter_hist(x, y, ax, colors="red", ax_histx=None, ax_histy=None, num_bins=50):
    """
    num_bins 太大的话会有空隙
    """
    ax.scatter(x, y, c=colors,
               edgecolor='k')
    # ax.grid(True)

    if ax_histx:
        ax_histx.tick_params(axis="x", labelbottom=False)
        d1.hist(x, ax_histx, num_bins)

    if ax_histy:
        ax_histy.tick_params(axis="y", labelleft=False)
        d1.hist(y, ax_histy, num_bins, orientation="horizontal")


def plot_scatter_hist(x1, x2, target):
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    spacing = 0.005
    offset = 1
    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom + height + spacing, width, 0.2]
    rect_histy = [left + width + spacing, bottom, 0.2, height]

    # start with a square Figure
    fig = plt.figure(figsize=(8, 8))

    ax = fig.add_axes(rect_scatter)
    ax_histx = fig.add_axes(rect_histx, sharex=ax)
    ax_histy = fig.add_axes(rect_histy, sharey=ax)

    ax.set_xlim(np.min(x1) - offset, np.max(x1) + offset)
    ax.set_ylim(np.min(x2) - offset, np.max(x2) + offset)
    ax_histx.set_xlim(ax.get_xlim() )
    ax_histy.set_ylim(ax.get_ylim() )

    scatter_hist(x1, x2, ax, y, ax_histx, ax_histy, 20)
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    from sklearn import datasets
    iris = datasets.load_iris()
    x1 = iris.data[:, 0] 
    x2 = iris.data[:, 1] 
    y = iris.target
    plot_scatter_hist(x1, x2, y)


# %%