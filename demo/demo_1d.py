import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import matplotlib
import numpy as np
import matplotlib.pyplot as plt


def plot_hist():
     np.random.seed(19680801)
     # example data
     mu = 100  # mean of distribution
     sigma = 15  # standard deviation of distribution
     x = mu + sigma * np.random.randn(437)
     num_bins = 50
     fig, ax = plt.subplots()
     # add a 'best fit' line
     hist_plot_specific(x, ax, num_bins, sigma, mu)
     # Tweak spacing to prevent clipping of ylabel
     fig.tight_layout()
     plt.show()


def hist_plot_specific(x, ax, num_bins, sigma, mu):
     # the histogram of the data
     n, bins, patches = ax.hist(x, num_bins, density=1)
     y = ((1 / (np.sqrt(2 * np.pi) * sigma)) *
          np.exp(-0.5 * (1 / sigma * (bins - mu))**2))
     ax.plot(bins, y, '--')
     ax.set_xlabel('Smarts')
     ax.set_ylabel('Probability density')
     ax.set_title(r'Histogram of IQ: $\mu=100$, $\sigma=15$')


if __name__ == "__main__":
    plot_hist()