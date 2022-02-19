# -*- coding: utf-8 -*-
from re import S
import sys
import six
# from six.moves import range
from matplotlib.widgets import AxesWidget
from matplotlib.widgets import MultiCursor
from matplotlib.ticker import Formatter
import matplotlib.ticker as mticker
import numpy as np
from .frame_widget import FrameWidget
from .slider_widget import Slider, slider_strtime_format
from .base_widget import BaseFigureWidget

class PlotterInfo(object):
    def __init__(self, plotter, ax_plot):
        self._plotter = plotter
        self._ax_plot = ax_plot
        self.zorder_switch = plotter.zorder_switch
        self.visible_switch = plotter.visible_switch

    def process_slider_state(state):
        pass


class TechnicalWidget(BaseFigureWidget):
    """ 多窗口控件 """
    def __init__(self, fig, data, left=0.1, bottom=0.05, width=0.85, height=0.9,
            parent=None):
        """ 多窗口联动控件。

        Args:
            fig (Figure): matplotlib绘图容器。
            data (DataFrame): [open, close, high, low]数据表。
        """
        BaseFigureWidget.__init__(self, fig, len(data), 0, "TechnicalWidget")
        self._cursor = None
        self._cursor_axes_index = { }
        self._hoffset = 1
        self._left, self._width = left, width
        self._bottom, self._height  = bottom, height
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
        return self._axes

    def plot_text(self, name, ith_ax, x, y, text, color='black', size=10, rotation=0):
        self.axes[ith_ax].text(x, y, text, color=color, fontsize=size, rotation=rotation)

    def _init_subwidges_window_position(self):
        self.window_left = self._data_length - self.window_size
        for subwidget in six.itervalues(self._child_widgets):
            subwidget.set_window_interval(self.window_left, self.window_right)

    def add_widget(self, ith_subwidget, widget):
        """ 添加一个能接收消息事件的控件。

        Args:
            ith_subwidget (int.): 子窗口序号。
            widget (AxesWidget): 控件。

        Returns:
            AxesWidget. widget
        """
        widget.window_size = self.window_size
        widget.window_left = self.window_left
        widget.parent = self
        for plotter in six.itervalues(widget.plotters):
            if plotter.twinx:
                plotter.ax.format_coord = self._format_coord
                self.axes.append(plotter.ax)
        self._child_widgets[ith_subwidget] = widget
        return widget


    def on_slider(self, event):
        """ 滑块事件处理。 """
        val = event.position
        def on_press_event():
            self._bigger_picture.set_zorder(1000)
            self._slider_cursor = MultiCursor(self._fig.canvas,
                                    [self._slider_ax, self._bigger_picture], color='y',
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


    def on_key_release(self, event):
        for subwidget in six.itervalues(self._child_widgets):
            subwidget.on_key_release(event)
        self._fig.canvas.draw()
        # elif event.key == u"super+up":

    def on_leave_axes(self, event):
        event.canvas.draw()

    def draw_widgets(self):
        """ 显示控件 """
        self._draw_bigger_picture()
        self._cursor = MultiCursor(self._fig.canvas,
                                    list(self._cursor_axes.values()),
                                    color='r', lw=2, horizOn=True,
                                    vertOn=True)
        self._init_subwidges_window_position()
        self._fig.canvas.draw()

    def _draw_bigger_picture(self):
        self._bigger_picture_plot = self._bigger_picture.plot(self._data['close'].values, 'b')
        self._bigger_picture.set_ylim((min(self._data['low']), max(self._data['high'])))
        self._bigger_picture.set_xlim((0, len(self._data['close'])))

    def init_layout(self, w_width, *args):
        # 布局参数
        self.window_size = w_width
        self.window_left = self._data_length - self.window_size
        print("window_left: %s" % (self.window_left))
        print("window_size: %s" % (self._data_length))

        self.add_slider_bigger_picture();
        self.add_user_axes(*args)

        return self.axes


    def add_slider_bigger_picture(self):
        self._slidder_lower = self._bottom
        self._slidder_upper = self._bottom + self._slider_height
        self._bigger_picture_lower = self._slidder_upper
        self._slider_ax = self._fig.add_axes([self._left, self._slidder_lower, self._width,
                                             self._slider_height])
        self._bigger_picture = self._fig.add_axes([self._left, self._bigger_picture_lower,
                                                    self._width, self._bigger_picture_height],
                                                zorder = 0, frameon=False,
                                                #sharex=self._slider_ax,
                                                alpha = 0.1 )
        self._bigger_picture.set_xticklabels([]);
        self._bigger_picture.set_xticks([])
        self._bigger_picture.set_yticks([])
        self._slider_ax.xaxis.set_major_formatter(TimeFormatter(self._data.index, fmt='%Y-%m-%d'))
        self._all_axes = [self._slider_ax, self._bigger_picture]

        self._slider = Slider(self._fig, self._slider_ax, "slider", self._data_length, self._window_size, self, '', 0, self._data_length-1,
                                    self._data_length-1, self._data_length/50, "%d",
                                    self._data.index)


    def add_user_axes(self, *args):
        args = list(reversed(args))
        # 默认子窗口数量为1
        if len(args) ==  0:
            args = (1,)

        total_units = sum(args)
        unit = (self._bottom + self._height - self._slidder_upper) / total_units
        bottom = self._slidder_upper
        user_axes = []
        first_user_axes = None
        for i, ratio in enumerate(args):
            rect = [self._left, bottom, self._width, unit * ratio]
            if i > 0:
                # 共享x轴
                ax = self._fig.add_axes(rect, sharex=first_user_axes)  #facecolor=axescolor)
                self._all_axes.append(ax)
            else:
                first_user_axes = self._fig.add_axes(rect)
                self._all_axes.append(first_user_axes)
            user_axes = self._all_axes[2:]  #self._bigger_picture
            bottom += unit * ratio
        self._axes = list(reversed(user_axes))
        map(lambda x: x.grid(True), self._axes)
        map(lambda x: x.set_xticklabels([]), self._axes[1:])
        for ax in self.axes:
            ax.get_yaxis().get_major_formatter().set_useOffset(False)
            # ax.get_yaxis().get_major_formatter().set_scientific(False)
        for i, ax in enumerate(self.axes):
            ax.format_coord = self._format_coord
            self._cursor_axes[i] = ax
        delta = (self._data.index[1] - self._data.index[0])
        self.axes[0].xaxis.set_major_formatter(TimeFormatter(self._data.index, delta))
        self.axes[0].set_xticks(self._xticks_to_display(0, self._data_length, delta));
        for ax in self.axes[0:-1]:
            [label.set_visible(False) for label in ax.get_xticklabels()]
        for i in range(0, len(self.axes)):
            self._cursor_axes_index[i] = i
        pass

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
        return str(index)

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

class TimeFormatter(Formatter):
    # 分类 －－format
    def __init__(self, dates, delta=None, fmt='%Y-%m-%d %H:%M'):
        self.dates = dates
        self.fmt = self._strtime_format(delta) if delta else fmt

    def __call__(self, x, pos=0):
        'Return the label for time x at position pos'
        ind = int(round(x))
        if ind>=len(self.dates) or ind<0: return ''
        return self.dates[ind].strftime(self.fmt)

    def _strtime_format(self, delta):
        if delta.days >= 1:
            return '%Y-%m'
        elif delta.seconds == 60:
            return '%m-%d %H:%M'
        else:
            # 日内其它分钟
            return '%m-%d'
