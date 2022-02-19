'''
Author: your name
Date: 2022-02-12 08:05:30
LastEditTime: 2022-02-19 12:42:47
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
    def __init__(self, ax, name, widget_size, window_size):
        BaseAxesWidget.__init__(self, ax, name, widget_size, window_size, None)
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

    def on_slider(self, event):
        self._update_window(event.position)

    def set_window_interval(self, w_left, w_right):
        all_ymax = []
        all_ymin = []
        w_left = int(w_left)
        w_right = int(w_right)
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
        self.ax.set_xlim(w_left, w_right)

    def _update_window(self, position):
        self.update_window_position(position)
        self.set_window_interval(self.window_left, self.window_right)

    def on_button_press(self, event):
        # TODO  parent -> slider -> parent -> self
        # TODO  parent -> subwidget     source:parent
        pass

    def on_key_release(self, event):
        if event.key == u"down":
            middle = (self.window_left + self.window_right) / 2
            self.window_left =  max(1, int(middle - self.window_size))
            self.window_size = min(self.widget_size, self._window_size * 2)
            self.set_window_interval(self.window_left, self.window_right)

            middle = (self.window_left + self.window_right) / 2
            print("window: ")
            print((self.window_left, middle, self.window_right, self.window_size))

        elif event.key == u"up" :
            middle = (self.window_left + self.window_right) / 2
            self.window_size = min(self.widget_size, int(self._window_size / 2))
            self.window_left =  max(1, int(middle - self.window_size/2))
            self.set_window_interval(self.window_left, self.window_right)

            print("window: ")
            middle = (self.window_left + self.window_right) / 2
            print((self.window_left, middle, self.window_right, self.window_size))