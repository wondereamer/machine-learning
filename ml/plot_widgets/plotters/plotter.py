'''
Author: your name
Date: 2022-02-19 10:04:35
LastEditTime: 2022-07-21 13:39:44
LastEditors: wondereamer wells7.wong@gmail.com
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/widgets/plotter.py
'''
# -*- coding: utf-8 -*-
##
# @file plotter.py
# @brief 统一绘图接口, 帮助指标类的绘图。
# @author wondereamer
# @version 0.15
# @date 2015-06-13

import numpy as np
from matplotlib.colors import colorConverter
from matplotlib.collections import LineCollection, PolyCollection
from ml.plot_widgets import events

class SliderPlotter(object):
    """
    """
    def __init__(self, ax, name, lower_data, upper_data):
        """_summary_

        Args:
            ax (Axes): 
            name (str): plotter name
            lower_data (pd.Series): used to comppute lower of data
            upper_data (pd.Series): used to comppute upper of data
        """
        self.name = name
        self.ax = ax
        self.zorder = 0
        self.zorder_switch = False
        self.visible_switch = False
        self._upper = lower_data
        self._lower = upper_data

    def y_interval(self, w_left, w_right):
        """ 可视区域[w_left, w_right]移动时候重新计算纵坐标范围。 """
        # @todo 只存储上下界, 每次缩放的时候计算一次, 在移动时候无需计算。
        if len(self._upper) == 2:
            # 就两个值，分别代表上下界。
            ymax = max(self._upper)
            ymin = min(self._upper)
            print("*" * 30)
            print(self.name, ymax, ymin)
            print("*" * 30)
            return ymax, ymin
        if w_right > len(self._upper) or w_right > len(self._lower):
            raise Exception("数据长度不一致导致，需要换算出对应的数据索引。plotter: %s, len: %s, w_right: %s, w_left: %s" \
                % (self.name, len(self._upper), w_right, w_left))
        ymax = np.nanmax(self._upper[w_left: w_right])
        ymin = np.nanmin(self._lower[w_left: w_right])
        print("*" * 30)
        print("plotter y_interval")
        print(self.name, ymax, ymin)
        print("*" * 30)
        return ymax, ymin

    def plot(self, axes):
        pass

    def set_visible(self, to_show):
        pass

    def on_slider(self, event):
        pass


class LinePlotter(SliderPlotter):
    """ 柱状图。 """
    def __init__(self, axes, upper, lower, name="Line"):
        super(LinePlotter, self).__init__(axes, name, upper, lower)

    def plot(self, x, y, *args, **kwargs):
        plot = self.ax.plot(x, y, *args, **kwargs)
        return plot


class Volume(SliderPlotter):
    """ 柱状图。 """
    def __init__(self, open, close, volume, name='volume',
                 colorup='r', colordown='g', width=1):
        self.volume = np.asarray(volume)
        super(Volume, self).__init__(None, name, self.volume, self.volume)
        self.open = open
        self.close = close
        self.colorup = colorup
        self.colordown = colordown
        self.width = width
        self.name = name
        self.volume_collections = None

    def plot(self, axes):
        import mpl_finance as finance
        self.volume_collections = finance.volume_overlay(axes, self.open, self.close, self.volume,
                               self.colorup, self.colordown, self.width)

    def set_visible(self, to_show):
        self.volume_collections.set_visible(to_show)

    def on_slider(self, event):
        if event.name == events.MouseMotionEvent:
            self.set_visible(False)
        elif event.name == events.ButtonReleaseEvent:
            self.set_visible(True)


class Candles(SliderPlotter):
    """
    画蜡烛线。
    """
    def __init__(self, data, name='candle',
                 width=0.6, colorup='r', colordown='g',
                 lc='k', alpha=1):
        """ Represent the open, close as a bar line and high low range as a
        vertical line.


        ax          : an Axes instance to plot to

        width       : the bar width in points

        colorup     : the color of the lines where close >= open

        colordown   : the color of the lines where close <  open

        alpha       : bar transparency

        return value is lineCollection, barCollection
        """
        super(Candles, self).__init__(None, name, data.high.values, data.low.values)
        self.data = data
        self.name = name
        self.width = width
        self.colorup = colorup
        self.colordown = colordown
        self.lc = lc
        self.alpha = alpha
        self.lineCollection = []
        self.barCollection = []

    # note this code assumes if any value open, close, low, high is
    # missing they all are missing
    def plot(self, ax):
        delta = self.width / 2.
        barVerts = [((i - delta, open),
                     (i - delta, close),
                     (i + delta, close),
                     (i + delta, open))
                    for i, open, close in zip(range(len(self.data)),
                                              self.data.open,
                                              self.data.close)
                    if open != -1 and close != -1]
        rangeSegments = [((i, low), (i, high))
                         for i, low, high in zip(range(len(self.data)),
                                                 self.data.low,
                                                 self.data.high)
                         if low != -1]
        r, g, b = colorConverter.to_rgb(self.colorup)
        colorup = r, g, b, self.alpha
        r, g, b = colorConverter.to_rgb(self.colordown)
        colordown = r, g, b, self.alpha
        colord = {
            True: colorup,
            False: colordown,
        }
        colors = [colord[open < close]
                  for open, close in zip(self.data.open, self.data.close)
                  if open != -1 and close != -1]
        assert(len(barVerts) == len(rangeSegments))
        useAA = 0,  # use tuple here
        lw = 0.5,   # and here
        r, g, b = colorConverter.to_rgb(self.lc)
        linecolor = r, g, b, self.alpha
        self.lineCollection = LineCollection(rangeSegments,
                                             colors=(linecolor,),
                                             linewidths=lw,
                                             antialiaseds=useAA,
                                             zorder=0)

        self.barCollection = PolyCollection(barVerts,
                                            facecolors=colors,
                                            edgecolors=colors,
                                            antialiaseds=useAA,
                                            linewidths=lw,
                                            zorder=1)
        ax.autoscale_view()
        # add these last
        ax.add_collection(self.barCollection)
        ax.add_collection(self.lineCollection)
        return self.lineCollection, self.barCollection

    def on_slider(self, event):
        if event.name == events.MouseMotionEvent:
            self.barCollection.set_visible(False)
        elif event.name == events.ButtonReleaseEvent:
            self.barCollection.set_visible(True)