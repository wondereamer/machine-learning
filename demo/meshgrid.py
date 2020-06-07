#!/usr/bin/env python
# encoding: utf-8
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt


def sinus2d(x, y):
    return np.sin(x) + np.sin(y)


points = np.arange(-5, 5, 0.01)
xx, yy = np.meshgrid(points, points)
z = np.sqrt(xx**2 + yy**2)
plt.imshow(z, origin='lower', interpolation='none', cmap=plt.cm.gray)
plt.colorbar()
plt.show()
