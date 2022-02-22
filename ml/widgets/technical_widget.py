# -*- coding: utf-8 -*-
from json.tool import main
from re import S
import sys
import six
# from six.moves import range
from matplotlib.widgets import MultiCursor
import matplotlib.ticker as mticker
import numpy as np

from ml.widgets.frame_widget import SliderAxesWidget, BirdsEyeWidget
from .slider_widget import Slider, slider_strtime_format
from .base_widget import BaseFigureFrame
from .formater import TimeFormatter

class PlotterInfo(object):
    def __init__(self, plotter, ax_plot):
        self._plotter = plotter
        self._ax_plot = ax_plot
        self.zorder_switch = plotter.zorder_switch
        self.visible_switch = plotter.visible_switch

    def process_slider_state(state):
        pass


class MultiWidgetsFrame(BaseFigureFrame):
    def __init__(self, fig, name, widget_size, window_size, parent=None):
        """ 多窗口联动控件。

        Args:
            fig (Figure): matplotlib绘图容器。
        """
        BaseFigureFrame.__init__(self, fig, widget_size, window_size, name)
        self._slider = None

    @property
    def slider(self):
        return self._slider

    def add_axes(self, left, bottom, width, height, **args):
        return self._fig.add_axes([left, bottom, width, height], **args)

    def add_widget(self, widget):
        """ 添加一个能接收消息事件的控件。

        Args:
            widget (AxesWidget): 控件。

        Returns:
            AxesWidget. widget
        """
        widget.parent = self
        # for plotter in six.itervalues(widget.plotters):
        #     if plotter.twinx:
        #         plotter.ax.format_coord = self._format_coord
                # self.axes.append(plotter.ax)
        self._child_widgets.append(widget)
        if isinstance(widget, SliderAxesWidget):
            if self._slider is None:
                print("Warn: slider should be create before adding widget.")
            else:
                self._slider.add_observer(widget.on_slider)
        return widget

    def create_slider(self, slider_axes, index):
        slider = Slider(slider_axes, "slider", self.widget_size, self.window_size,
            self, '', 0, self.widget_size-1, self.widget_size-1, self.widget_size/50, "%d", index)
        self.set_slider(slider)
        return self._slider

    def set_slider(self, slider):
        self._slider = slider

    def tight_layout(self):
        # https://matplotlib.org/stable/tutorials/intermediate/tight_layout_guide.html
        self.plot.tight_layout()

    def show(self):
        self._draw_widgets()
        if self._slider:  
            # 保证canvas.draw()只被自己的on_slider调用
            self._slider.add_observer(self.on_slider)
        self._fig.canvas.draw()
        self.plot.show()

    def _draw_widgets(self):
        """ 显示控件 """
        self._init_subwidges_window_position()
        self._fig.canvas.draw()

    def _init_subwidges_window_position(self):
        self.window_left = 1
        for subwidget in self._child_widgets:
            if not isinstance(subwidget, SliderAxesWidget):
                continue
            try:
                subwidget.set_window_interval(subwidget.window_left, subwidget.window_right)
            except Exception as e:
                raise Exception("设置窗口位置失败 %s" % subwidget.name)

    def on_key_release(self, event):
        for subwidget in self._child_widgets:
            subwidget.on_key_release(event)
        self._fig.canvas.draw()
        # elif event.key == u"super+up":

    def on_slider(self, event):
        """ 滑块事件处理。 """
        event.canvas.draw()


class TechnicalFrame(MultiWidgetsFrame):
    """ 多窗口控件 """
    def __init__(self, fig, widget_size:int, window_size:int, parent=None):
        """ 多窗口联动控件。

        Args:
            fig (Figure): matplotlib绘图容器。
            data (DataFrame): [open, close, high, low]数据表。
        """
        MultiWidgetsFrame.__init__(self, fig, "TechnicalFrame", widget_size, window_size, parent)
        self._cursor = None
        self._cursor_axes_index = { }
        self._user_axes = []

    def load_data(self, data):
        print("load_data")
        self._data = data
        self.window_left = self.widget_size - self.window_size
        print("Set window to display latest data, with index: %s" % (self.window_left))

    def init_layout(self):
        """ 初始化窗口布局

        Returns:
            [ax]: axes数组
        """
        # 显示最后一个窗口的数据
        self._user_axes.append(self.plot.subplot2grid((30, 1), (0, 0), rowspan=12))
        self._user_axes.append(self.plot.subplot2grid((30, 1), (15, 0), rowspan=9))
        slider_axes = self.plot.subplot2grid((30, 1), (25, 0), rowspan=5)
        self.create_slider(slider_axes, self._data.index)
        return self._user_axes

    def plot_text(self, name, ith_ax, x, y, text, color='black', size=10, rotation=0):
        self.axes[ith_ax].text(x, y, text, color=color, fontsize=size, rotation=rotation)

    def on_leave_axes(self, event):
        event.canvas.draw()

    def _draw_widgets(self):
        """ 显示控件 """
        self._user_axes[0].grid(True)
        self._user_axes[1].set_xticklabels([])
        self._slider.ax.xaxis.set_major_formatter(TimeFormatter(self._data.index, fmt='%Y-%m-%d'))
        self._cursor = MultiCursor(self._fig.canvas,
                                    self._user_axes,
                                    color='r', lw=2, horizOn=True,
                                    vertOn=True)
        self._create_birds_eve_widget()
        self._init_subwidges_window_position()

    def _create_birds_eve_widget(self):
        slider_pos = self.slider.ax.get_position()
        bigger_picture_ax = self.add_axes(
            slider_pos.x0, slider_pos.y1, slider_pos.width, 0.4,
            zorder = 1000, frameon=False, alpha = 0.1)

        bigger_picture = BirdsEyeWidget(
            self._data, bigger_picture_ax, "bigger_picture",
            self.widget_size, self.window_size, self)
        self.add_widget(bigger_picture)


if __name__ ==  "__main__":
    print("ok")