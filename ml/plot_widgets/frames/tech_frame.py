# -*- coding: utf-8 -*-
from re import S
from enum import Enum
from matplotlib.widgets import MultiCursor
from matplotlib.widgets import RadioButtons
import matplotlib.pyplot as plt

from ml.plot_widgets.widgets.widgets import CandleWidget, BirdsEyeWidget
from ml.plot_widgets.formater import TimeFormatter
from ml.plot_widgets.frames.frames import MultiWidgetsFrame
from ml.log import wlog as log


class JumpUnit(Enum):
    Period = 1
    Signal = 2
    Day = 3



class MoveUnit(object):
    def __init__(self, tech_frame):
        self._tech_frame = tech_frame
        self._jump_unit = JumpUnit.Period
        self._signal_index = 0
        self._next_ndata = 10

    def _next_signal_x(self, signals, window_size):
        self._signal_index = min(len(signals)-1, self._signal_index+1)
        pos = signals[self._signal_index] - window_size / 2
        log.debug("next_signal: %s" % signals[self._signal_index])
        return pos

    def _previous_signal_x(self, signals, window_size):
        self._signal_index = max(self._signal_index-1, 0)
        pos = signals[self._signal_index] - window_size / 2
        log.debug("previous_signal: %s" % signals[self._signal_index])
        return pos

    def get_window_position(self, window_left, key):
        candle = self._tech_frame.get_candle_widget()
        window_size = candle.window_size
        widget_size = candle.widget_size
        pos = None
        if key == 'left':
            if self._jump_unit == JumpUnit.Period:
                pos =  max(window_left - self._next_ndata, 0)
            elif self._jump_unit == JumpUnit.Signal:
                pos = self._previous_signal_x(candle.signal_x, window_size)
            else:
                raise Exception("error")
        elif key == 'right':
            if self._jump_unit == JumpUnit.Period:
                pos = min(window_left + self._next_ndata, widget_size)
            elif self._jump_unit == JumpUnit.Signal:
                pos = self._next_signal_x(candle.signal_x, window_size)
            else:
                raise Exception("error")
        return pos

    def create_jump_widget(self, slider_pos):
        axcolor = 'lightgoldenrodyellow'
        width = 0.1
        span = 0.01
        rax = plt.axes([slider_pos.x0-width-span, slider_pos.y0, width, slider_pos.y1 - slider_pos.y0], facecolor=axcolor)
        self._radio = RadioButtons(rax, (JumpUnit.Period.name, JumpUnit.Signal.name))
        def set_jum_unit(unit):
            if unit == JumpUnit.Period.name:
                self._jump_unit = JumpUnit.Period
            elif unit == JumpUnit.Signal.name:
                self._jump_unit = JumpUnit.Signal
        self._radio.on_clicked(set_jum_unit)


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
        self._cursor_axes = []
        self._move_unit = MoveUnit(self)

    def set_data(self, data):
        log.info("Load data with size: {0}".format(len(data)))
        self._data = data
        self.window_left = self.widget_size - self.window_size
        log.info("Set window to display latest data, with index: %s" % (self.window_left))

    def get_candle_widget(self):
        for widget in self._child_widgets:
            if isinstance(widget, CandleWidget):
                return widget

    def set_layout(self):
        """ 设置窗口布局

        Returns:
            [ax]: axes数组
        """
        # 显示最后一个窗口的数据
        self._cursor_axes.append(self.plot.subplot2grid((30, 1), (0, 0), rowspan=15))  # 0 -> 14
        self._cursor_axes.append(self.plot.subplot2grid((30, 1), (15, 0), rowspan=4))  # 15 -> 19
        self._cursor_axes.append(self.plot.subplot2grid((30, 1), (19, 0), rowspan=4))  # 20 -> 24
        slider_axes = self.plot.subplot2grid((30, 1), (23, 0), rowspan=2) # 25 -> 30
        self.create_slider(slider_axes, self._data.index)
        return self._cursor_axes

    def on_key_release(self, event):
        log.debug("key pressed event: '%s'" % event.key)
        if event.key in [u"down", u"up"]:
            super().on_key_release(event)

        if event.key in ['left', 'right']:
            signal_pos = self._move_unit.get_window_position(self.window_left, event.key)
            self.update_window_position(signal_pos)
            self._fig.canvas.draw()

    def plot_text(self, ith_ax, x, y, text, color='black', size=10, rotation=0):
        self.axes[ith_ax].text(x, y, text, color=color, fontsize=size, rotation=rotation)

    def on_leave_axes(self, event):
        event.canvas.draw()

    def add_cursor_axes(self, axes):
        self._cursor_axes.append(axes)

    def _draw_widgets(self):
        """ 显示控件 """
        self._cursor_axes[0].grid(True)
        self._cursor_axes[1].set_xticklabels([])
        self._cursor_axes[2].grid(True)
        self._cursor_axes[2].set_xticklabels([])
        self._slider.ax.xaxis.set_major_formatter(TimeFormatter(self._data.index, fmt='%Y-%m-%d'))
        self._cursor = MultiCursor(self._fig.canvas,
                                    self._cursor_axes,
                                    color='r', lw=2, horizOn=True,
                                    vertOn=True)
        self._create_birds_eve_widget()
        self._move_unit.create_jump_widget(self.slider.ax.get_position())
        self._init_subwidges_window_position()

    def _create_birds_eve_widget(self):
        slider_pos = self.slider.ax.get_position()
        # bigger_picture_ax = self.add_axes(
        #     slider_pos.x0, slider_pos.y1, slider_pos.width, 0.4,
        #     zorder = 1000, frameon=False, alpha = 0.1)

        # self.bigger_picture = BirdsEyeWidget(
        #     self._data, bigger_picture_ax, "bigger_picture",
        #     self.widget_size, self.window_size, self)