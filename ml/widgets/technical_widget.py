# -*- coding: utf-8 -*-
from json.tool import main
from re import S
import sys
import six
# from six.moves import range
import matplotlib.pyplot as plt
from matplotlib.widgets import AxesWidget
from matplotlib.widgets import MultiCursor
import matplotlib.ticker as mticker
import numpy as np
from .frame_widget import FrameWidget
from .slider_widget import Slider, slider_strtime_format
from .base_widget import BaseFigureWidget
from .formater import TimeFormatter

class PlotterInfo(object):
    def __init__(self, plotter, ax_plot):
        self._plotter = plotter
        self._ax_plot = ax_plot
        self.zorder_switch = plotter.zorder_switch
        self.visible_switch = plotter.visible_switch

    def process_slider_state(state):
        pass


class MultiWidgets(BaseFigureWidget):
    def __init__(self, fig, plot, axes, name, widget_size, parent=None):
        """ 多窗口联动控件。

        Args:
            fig (Figure): matplotlib绘图容器。
        """
        BaseFigureWidget.__init__(self, fig, widget_size, 0, name)
        self._all_axes = axes
        self.plot = plot  # todo move to base widget
        self.connect_event_handlers()

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
        return widget

    def draw_widgets(self):
        """ 显示控件 """
        self._fig.canvas.draw()

    def tight_layout(self):
        # https://matplotlib.org/stable/tutorials/intermediate/tight_layout_guide.html
        self.plot.tight_layout()

    def show(self):
        self.draw_widgets()
        self.plot.show()

    def draw_widgets(self):
        """ 显示控件 """
        self._init_subwidges_window_position()
        self._fig.canvas.draw()

    def _init_subwidges_window_position(self):
        self.window_left = 1
        for subwidget in self._child_widgets:
            if subwidget.name == "slider":
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


class TechnicalWidget(MultiWidgets):
    """ 多窗口控件 """
    def __init__(self, fig, data, parent=None):
        """ 多窗口联动控件。

        Args:
            fig (Figure): matplotlib绘图容器。
            data (DataFrame): [open, close, high, low]数据表。
        """
        MultiWidgets.__init__(self, fig, plt, len(data), 0, "TechnicalWidget")
        self._cursor = None
        self._cursor_axes_index = { }
        self._hoffset = 1
        self._slider_height = 0.1
        self._bigger_picture_height = 0.3    # 鸟瞰图高度
        self._all_axes = []
        self._cursor_axes = { }
        self.load_data(data)
        self.connect_event_handlers()

    def load_data(self, data):
        self._data = data
        self._data_length = len(self._data)

    @property
    def axes(self):
        return self._user_axes

    def plot_text(self, name, ith_ax, x, y, text, color='black', size=10, rotation=0):
        self.axes[ith_ax].text(x, y, text, color=color, fontsize=size, rotation=rotation)

    def on_slider(self, event):
        """ 滑块事件处理。 """
        val = event.position
        def on_press_event():
            self._bigger_picture.set_zorder(1000)
            self._slider_cursor = MultiCursor(self._fig.canvas,
                                    [self._bigger_picture], color='y',
                                    lw=2, horizOn=False, vertOn=True)
        def on_release_event():
            self._bigger_picture.set_zorder(0)
            del self._slider_cursor
        if event.name == "button_press_event":
            on_press_event()
        elif event.name == "button_release_event":
            on_release_event()
        # self._fig.canvas.draw() 一样的，canvas属于fig
        event.canvas.draw()


    def on_leave_axes(self, event):
        event.canvas.draw()

    def show(self):
        self.draw_widgets()
        self.plot.show()

    def draw_widgets(self):
        """ 显示控件 """
        self._user_axes = self._all_axes[:-1]
        self._cursor = MultiCursor(self._fig.canvas,
                                    self._user_axes,
                                    color='r', lw=2, horizOn=True,
                                    vertOn=True)
        self._update_axes()
        self.add_slider_bigger_picture()
        self._draw_bigger_picture()
        self._init_subwidges_window_position()
        self._fig.canvas.draw()

    def _init_subwidges_window_position(self):
        self.window_left = self._data_length - self.window_size
        for subwidget in self._child_widgets:
            if subwidget.name == "slider":
                continue
            try:
                subwidget.set_window_interval(self.window_left, self.window_right)
            except Exception as e:
                raise Exception("设置窗口位置失败 %s" % subwidget.name)


    def _draw_bigger_picture(self):
        self._bigger_picture_plot = self._bigger_picture.plot(self._data['close'].values, 'b')
        self._bigger_picture.set_ylim((min(self._data['low']), max(self._data['high'])))
        self._bigger_picture.set_xlim((0, len(self._data['close'])))

    def init_layout(self, w_width):
        # 布局参数
        self.window_size = w_width
        self.window_left = self._data_length - self.window_size
        self.widget_size = self._data_length
        print("window_left: %s" % (self.window_left))
        print("window_size: %s" % (self._data_length))
        print("widget_size: %s" % (self.widget_size))

        self._all_axes.append(plt.subplot2grid((30, 1), (0, 0), rowspan=15))
        self._all_axes.append(plt.subplot2grid((30, 1), (15, 0), rowspan=10))
        self._all_axes.append(plt.subplot2grid((30, 1), (25, 0), rowspan=5))
        return self._all_axes

    def add_slider_bigger_picture(self):
        self._bigger_picture_lower = 0.3
        # self._slider_ax = self._fig.add_axes([0.1, self._slidder_lower, self._width,
        #                                      0.3])
        self._bigger_picture = self._fig.add_axes([0.1, 0.2,
                                                    0.5, 0.4],
                                                zorder = 0, frameon=False,
                                                #sharex=self._slider_ax,
                                                alpha = 0.1 )
        self._bigger_picture.set_xticklabels([]);
        self._bigger_picture.set_xticks([])
        self._bigger_picture.set_yticks([])

    def _format_coord(self, x, y):
        """ 状态栏信息显示 """
        index = x
        f = x % 1
        index = x-f if f < 0.5 else min(x-f+1, len(self._data['open']) - 1)
        delta = (self._data.index[1] - self._data.index[0])
        fmt = slider_strtime_format(delta)
        ## @note 字符串太长会引起闪烁
        index = int(index) - 1
        return "[dt=%s o=%.2f c=%.2f h=%.2f l=%.2f]" % (
                self._data.index[index].strftime(fmt),
                self._data['open'][index],
                self._data['close'][index],
                self._data['high'][index],
                self._data['low'][index])

    def _update_axes(self):
        map(lambda x: x.grid(True), self._user_axes)
        map(lambda x: x.set_xticklabels([]), self._user_axes[1:])
        for ax in self._user_axes:
            ax.get_yaxis().get_major_formatter().set_useOffset(False)
            # ax.get_yaxis().get_major_formatter().set_scientific(False)
        for i, ax in enumerate(self._user_axes):
            ax.format_coord = self._format_coord
            self._cursor_axes[i] = ax
        delta = (self._data.index[1] - self._data.index[0])
        self._user_axes[0].xaxis.set_major_formatter(TimeFormatter(self._data.index, delta))
        self._user_axes[0].set_xticks(self._xticks_to_display(0, self._data_length, delta));
        for ax in self._user_axes[0:-1]:
            [label.set_visible(False) for label in ax.get_xticklabels()]

    def _xticks_to_display(self, start, end, delta):
        xticks = []
        for i in range(start, end):
            if i >= 1:
                if delta.days >= 1:
                    if self._data.index[i].month != self._data.index[i-1].month:
                        xticks.append(i)
                elif delta.seconds == 60:
                    # 一分钟的以小时为显示单位
                    if self._data.index[i].hour != self._data.index[i-1].hour and \
                       self._data.index[i].day == self._data.index[i-1].day:
                        xticks.append(i)
                else:
                    if self._data.index[i].day != self._data.index[i-1].day:
                        # 其它日内以天为显示单位
                        xticks.append(i)
            else:
                xticks.append(0)
        return xticks


if __name__ ==  "__main__":
    print("ok")