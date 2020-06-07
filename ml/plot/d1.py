import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import matplotlib
import numpy as np
import matplotlib.pyplot as plt


def hist(x, ax, num_bins, y=None, orientation='vertical'):
     ## num_bins太大可能有空隙，下面注释的代码能确保没有空隙
     # ymax = np.max(y)
     # ymin = np.min(y)
     # binwidth = ymax / num_bins
     # lim = ( int(ymax/binwidth) + 1) * binwidth
     # bins = np.arange(-lim, lim + binwidth, binwidth)
     # ax_histy.hist(y, bins=bins, orientation='horizontal')

     n, bins, patches = ax.hist(x, num_bins, density=1, orientation=orientation)
     if y is not None:
          ax.plot(bins, y, '--')
     ax.set_xlabel('Smarts')
     ax.set_ylabel('Probability density')
     ax.set_title(r'Histogram of IQ: $\mu=100$, $\sigma=15$')


def plot_hist(x1, num_bins, y=None):
     fig, axes = plt.subplots(nrows=2, sharex=False)
     hist(x1, axes[0], num_bins)
     axes[1].plot(x1, "ro--")
     axes[1].plot(np.sort(x1))
     plt.show()


if __name__ == "__main__":
    from sklearn import datasets
    iris = datasets.load_iris()
    x1 = iris.data[:, 0] 
    plot_hist(x1, 20)
