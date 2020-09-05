import matplotlib
matplotlib.use('TkAgg')

import numpy as np
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn import datasets
from math import sqrt
from ml.plot import d1


def attr_analyze():
    fig, ax = plt.subplots()
    iris = datasets.load_iris()
    x1 = iris.data[:, 0]  # we only take the first two features.
    y = iris.target
    num_bins = 20
    d1.hist(ax, x1, num_bins)
    plt.show()


def data_normalize():
    y = np.random.randint(10, 1000, 100)
    y2 = np.random.randint(3000, 10000, 10)
    y = np.concatenate((y, y2), axis=None)
    fig, ax = plt.subplots()
    ax.plot(np.arange(len(y)), y)

    fig2 = plt.figure(2)
    ax221 = plt.subplot(221)
    ax221.plot(np.arange(len(y)), preprocessing.minmax_scale(y))


    y = y.reshape((len(y), 1))

    ax222 = plt.subplot(222)
    rst = preprocessing.StandardScaler()
    rst = rst.fit_transform(y)
    rst = np.squeeze(np.asarray(rst))
    ax222.plot(np.arange(len(y)), rst)

    ax223 = plt.subplot(223)
    rst = preprocessing.scale(y, axis=0)
    rst = np.squeeze(np.asarray(rst))
    ax223.plot(np.arange(len(y)), rst)

    ax224 = plt.subplot(224)
    rst = preprocessing.robust_scale(y)
    rst = np.squeeze(np.asarray(rst))
    ax224.plot(np.arange(len(y)), rst)

    plt.show()

if __name__ == "__main__":
    data_normalize()
    #attr_analyze()