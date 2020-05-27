import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor


def scatter_hist(x, y, ax, ax_histx, ax_histy, binnum=50):
    # no labels
    ax_histx.tick_params(axis="x", labelbottom=False)
    ax_histy.tick_params(axis="y", labelleft=False)

    # the scatter plot:
    ax.scatter(x, y)

    # now determine nice limits by hand:
    xmax = np.max(x)
    xmin = np.min(x)
    binwidth = xmax / binnum
    lim = ( int(xmax/binwidth) + 1) * binwidth
    bins = np.arange(-lim, lim + binwidth, binwidth)
    ax_histx.hist(x, bins=bins, color="red")

    xmax = np.max(x)
    xmin = np.min(x)
    binwidth = xmax / binnum
    lim = ( int(xmax/binwidth) + 1) * binwidth
    bins = np.arange(-lim, lim + binwidth, binwidth)
    ax_histy.hist(y, bins=bins, orientation='horizontal')

def scatter_demo(x, y):
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

    ax.set_xlim(np.min(x) - offset, np.max(x) + offset)
    ax.set_ylim(np.min(y) - offset, np.max(y) + offset)
    ax_histx.set_xlim(ax.get_xlim() )
    ax_histy.set_ylim(ax.get_ylim() )

    # use the previously defined function
    scatter_hist(x, y, ax, ax_histx, ax_histy)

    plt.show()



def plot_scatter2(fig, x2,  binnum, doc="Distribution", offset=1):
    y2 = np.arange(len(x2))
    fig.canvas.set_window_title(doc)
    # definitions for the axes 
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left+width+0.02

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]

    # start with a rectangular Figure

    axScatter = plt.axes(rect_scatter)
    axHistx = plt.axes(rect_histx)

    axScatter.plot(x2, y2, 'o', color = 'blue')

    # now determine nice limits by hand:
    xmax = np.max(x2)
    xmin = np.min(x2)
    binwidth = xmax / binnum
    lim = ( int(xmax/binwidth) + 1) * binwidth
    bins = np.arange(-lim, lim + binwidth, binwidth)
    axHistx.hist(x2, bins=bins)

    axScatter.axhline(color='black')
    axScatter.set_xlim(np.min(x2) - offset, np.max(x2) + offset)
    axScatter.set_ylim(np.min(y2) - offset, np.max(y2) + offset)

    axHistx.set_xlim( axScatter.get_xlim() )
    axScatter.set_xlabel(doc)
    axHistx.set_xticks([])

    axScatter.grid(True)
    axHistx.grid(True)
    c = Cursor(axScatter, useblit=True, color='red', linewidth=1, vertOn = True, horizOn = True)
    return [axScatter, axHistx], [c]

if __name__ == "__main__":
    import numpy as np
    attr1 = np.random.normal(loc=25, scale=5, size=50)
    attr2 = np.random.normal(loc=25, scale=5, size=50)
    # figure = plt.figure(1)
    #plot_scatter(figure, attr1, attr2, 50, "Distribution")
    # plot_scatter2(figure, attr1, 50, "Distribution")
    scatter_demo(attr1, attr2)