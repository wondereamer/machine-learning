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
from .base_widget import BaseWidget

class PlotterInfo(object):
    def __init__(self, plotter, ax_plot):
        self._plotter = plotter
        self._ax_plot = ax_plot
        self.zorder_switch = plotter.zorder_switch
        self.visible_switch = plotter.visible_switch

    def process_slider_state(state):
        pass


class TechnicalWidget(BaseWidget):
    """ 多窗口控件 """
    def __init__(self, fig, data, left=0.1, bottom=0.05, width=0.85, height=0.9,
            parent=None):
        """ 多窗口联动控件。

        Args:
            fig (Figure): matplotlib绘图容器。
            data (DataFrame): [open, close, high, low]数据表。
        """
        super().__init__("TechnicalWidget", fig)
        self._cursor = None
        self._cursor_axes_index = { }
        self._hoffset = 1
        self._left, self._width = left, width
        self._bottom, self._height  = bottom, height
        self._slider_height = 0.1
        self._bigger_picture_height = 0.3    # 鸟瞰图高度
        self._all_axes = []
        self.load_data(data)
        self._cursor_axes = { }

    def init_layout(self, w_width, *args):
        # 布局参数
        self._w_width_min = 50
        self._w_width = w_width
        self._init_widgets(*args)
        self.connect_event_handlers()
        return self.axes

    def load_data(self, data):
        self._data = data
        self._data_length = len(self._data)

    @property
    def axes(self):
        return self._axes

    def plot_text(self, name, ith_ax, x, y, text, color='black', size=10, rotation=0):
        self.axes[ith_ax].text(x, y, text, color=color, fontsize=size, rotation=rotation)

    def draw_widgets(self):
        """ 显示控件 """
        self._window_left = self._data_length - self._w_width
        self._window_right = self._data_length
        # create cursor after all subwidgets added
        self._cursor = MultiCursor(self._fig.canvas,
                                    list(self._cursor_axes.values()),
                                    color='r', lw=2, horizOn=True,
                                    vertOn=True)
        self._update_widgets()

    def add_widget(self, ith_subwidget, widget, ymain=False, connect_slider=False):
        """ 添加一个能接收消息事件的控件。

        Args:
            ith_subwidget (int.): 子窗口序号。
            widget (AxesWidget): 控件。

        Returns:
            AxesWidget. widget
        """
        # 对新创建的Axes做相应的处理
        # 并且调整Cursor
        for plotter in six.itervalues(widget.plotters):
            if plotter.twinx:
                plotter.ax.format_coord = self._format_coord
                self.axes.append(plotter.ax)
        self._child_widgets[ith_subwidget] = widget
        widget.parent = self
        if connect_slider:
            self._slider.add_observer(widget)
        return widget

    def on_slider(self, val, event):
        """ 滑块事件处理。 """
        def update_window():
            self._window_left = int(val)
            self._window_right = self._window_left+self._w_width
            if self._window_right >= self._data_length:
                self._window_right = self._data_length - 1 + self._hoffset
                self._window_left = self._window_right - self._w_width
        def on_press_event():
            self._bigger_picture.set_zorder(1000)
            self._cursor = None
        def on_release_event():
            self._bigger_picture.set_zorder(0)
            self._cursor = MultiCursor(self._fig.canvas,
                                        list(self._cursor_axes.values()),
                                        color='r', lw=2, horizOn=True,
                                        vertOn=True)

        if event.name == "button_press_event":
            on_press_event()
        elif event.name == "button_release_event":
            on_release_event()
        elif event.name == "motion_notify_event":
            pass
        update_window()
        self._update_widgets()

    def on_key_release(self, event):
        def update_window():
            middle = (self._window_left+self._window_right)/2
            self._window_left =  int(middle - self._w_width/2)
            self._window_right = int(middle + self._w_width/2)
            self._window_left = max(0, self._window_left)
            self._window_right = min(self._data_length, self._window_right)

        if event.key == u"down":
            self._w_width += self._w_width/2
            self._w_width = min(self._data_length, self._w_width)
            update_window()
            self._update_widgets()
        elif event.key == u"up" :
            self._w_width -= self._w_width/2
            self._w_width= max(self._w_width, self._w_width_min)
            update_window()
            self._update_widgets()
        elif event.key == u"super+up":
            six.print_(event.key, "**", type(event.key) )
        elif event.key == u"super+down":
            six.print_(event.key, "**", type(event.key) )
            # @TODO page upper down

    def on_leave_axes(self, event):
        event.canvas.draw()


    def _init_widgets(self, *args):

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
        self._all_axes = [self._slider_ax, self._bigger_picture]
        self._slider = None
        self._bigger_picture_plot = None

        self._slider = Slider(self._fig, self._slider_ax, "slider", self, '', 0, self._data_length-1,
                                    self._data_length-1, self._data_length/50, "%d",
                                    self._data.index)
        self._slider.add_observer(self)

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


    def _update_widgets(self):
        """ 改变可视区域， 在坐标移动后被调用。"""
        self.axes[0].set_xlim((int(self._window_left), int(self._window_right)))
        for subwidget in six.itervalues(self._child_widgets):
            subwidget.set_ylim(self._window_left, self._window_right)
        self._fig.canvas.draw()

    def _set_ylim(self, w_left, w_right):
        """ 设置当前显示窗口的y轴范围。
        """

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

    def dispatch_event(self, event, set_source=True):
        if (hasattr(event, "source") and event.source == self.name):
            # ingore event emitted by self
            return

        if (set_source):
            setattr(event, "source", self.name)

        self.handle_event(event)

        if self.parent is not None:
            self.parent.dispatch_event(event, False)

        self._slider.dispatch_event(event, False)

        for widget in self._child_widgets.values():
            widget.dispatch_event(event, False)


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
