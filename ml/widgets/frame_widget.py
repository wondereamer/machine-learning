'''
Author: your name
Date: 2022-02-12 08:05:30
LastEditTime: 2022-02-15 13:33:58
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/widgets/fame_widgets.py
'''
from lib2to3.pytree import Base
import six
from .base_widget import BaseAxesWidget


class FrameWidget(BaseAxesWidget):
    """
    蜡烛线控件。

    """
    def __init__(self, ax, name, wdlength, min_wdlength):
        BaseAxesWidget.__init__(self, ax, name, None)
        self.wdlength = wdlength
        self.min_wdlength = min_wdlength
        self.voffset = 0
        self.plotters = { }
        self.ax = ax
        self.cnt = 0
        self.observers = {}
        # self.connect_event_handlers()

    def add_plotter(self, plotter, twinx):
        """ 添加并绘制, 不允许重名的plotter """
        if plotter.name in self.plotters:
            raise
        if not self.plotters:
            twinx = False
        if twinx:
            twaxes = self.ax.twinx()
            plotter.plot(twaxes)
            plotter.ax = twaxes
            plotter.twinx = True
        else:
            plotter.plot(self.ax)
            plotter.ax = self.ax
            plotter.twinx = False
        self.plotters[plotter.name] = plotter

    def set_ylim(self, w_left, w_right):
        all_ymax = []
        all_ymin = []
        for plotter in six.itervalues(self.plotters):
            if plotter.twinx:
                continue
            ymax, ymin = plotter.y_interval(w_left, w_right)
            ## @todo move ymax, ymin 计算到plot中去。
            all_ymax.append(ymax)
            all_ymin.append(ymin)
        ymax = max(all_ymax)
        ymin = min(all_ymin)
        self._voffset = (ymax-ymin) / 10.0 # 画图显示的y轴留白。
        ymax += self._voffset
        ymin -= self._voffset
        self.ax.set_ylim((ymin, ymax))

    def on_slider(self, val, event):
        ## @TODO _set_ylim 分解到这里
        pass

    def on_button_press(self, event):
        print(self.name + " from " + event.source)
        print(event.inaxes == self.ax)
        # TODO  parent -> slider -> parent -> self
        # TODO  parent -> subwidget     source:parent