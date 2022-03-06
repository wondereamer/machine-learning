# -*- coding: utf-8 -*-
from json.tool import main
from re import S
from enum import Enum
from matplotlib.widgets import MultiCursor
from matplotlib.widgets import RadioButtons
import matplotlib.pyplot as plt
import numpy as np

from ml.plot_widgets.base_widget import BaseFigureFrame
from ml.plot_widgets.frame_widget import CandleWidget, SliderAxesWidget, BirdsEyeWidget
from ml.plot_widgets.slider_widget import Slider, TimeSliderFormatter
from ml.plot_widgets.formater import TimeFormatter
from ml.log import wlog as log

class PlotterInfo(object):
    def __init__(self, plotter, ax_plot):
        self._plotter = plotter
        self._ax_plot = ax_plot
        self.zorder_switch = plotter.zorder_switch
        self.visible_switch = plotter.visible_switch

    def process_slider_state(state):
        pass


class JumpUnit(Enum):
    Period = 1
    Signal = 2
    Day = 3

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
                log.warn("Slider should be create before adding widget.")
            else:
                self._slider.add_observer(widget.on_slider)
        return widget

    def create_slider(self, slider_axes, index):
        formatter = TimeSliderFormatter(index)
        slider = Slider(slider_axes, "slider", self.widget_size, self.window_size,
            self, '', 0, self.widget_size-1, formatter, self.widget_size-1, self.widget_size/50, "%d", index)
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
        log.debug("key pressed event: '%s'" % event.key)
        for subwidget in self._child_widgets:
            subwidget.on_key_release(event)
        log.debug("canvas.draw")
        self._fig.canvas.draw()
        # elif event.key == u"super+up":

    def on_slider(self, event):
        """ 滑块事件处理。 """
        event.canvas.draw()



class MoveUnit(object):
    def __init__(self, tech_frame):
        self._tech_frame = tech_frame
        self._jump_unit = JumpUnit.Period
        self._signal_index = 0
        self._next_ndata = 10

    def _next_signal_x(self, signals, window_size):
        log.debug(signals)
        log.debug("next_signal")
        self._signal_index = min(len(signals), self._signal_index + 1)
        pos = signals[0] - window_size / 2
        return pos

    def _previous_signal_x(self, signals, window_size):
        log.debug("previous_signal")
        self._signal_index = max(0, self._signal_index - 1)
        pos = signals[0] - window_size / 2
        return pos

    def change_window_position(self, subwidget, key):
        candle = self._tech_frame.get_candle_widget()
        pos = None
        if key == 'left':
            if self._jump_unit == JumpUnit.Period:
                pos =  max(subwidget.window_left - self._next_ndata, 0)
            elif self._jump_unit == JumpUnit.Signal:
                pos = self._next_signal_x(candle.signal_x, candle.window_size)
            else:
                raise Exception("error")
        else:
            if self._jump_unit == JumpUnit.Period:
                pos = min(subwidget.window_left + self._next_ndata, subwidget.widget_size)
            elif self._jump_unit == JumpUnit.Signal:
                pos = self._previous_signal_x(candle.signal_x, candle.window_size)
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
        self._user_axes = []
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
        self._move_unit.create_jump_widget(self.slider.ax.get_position())
        self._init_subwidges_window_position()

    def on_key_release(self, event):
        log.debug("key pressed event: '%s'" % event.key)
        if event.key in [u"down", u"up"]:
            MultiWidgetsFrame.on_key_release(self, event)
            return

        if event.key == 'left':
            for subwidget in self._child_widgets:
                subwidget.set_window_postion(
                    self._move_unit.change_window_position(subwidget, 'left')
                )
            self._fig.canvas.draw()
        elif event.key == 'right':
            for subwidget in self._child_widgets:
                subwidget.set_window_postion(
                    self._move_unit.change_window_position(subwidget, 'right')
                )
            self._fig.canvas.draw()

    def _create_birds_eve_widget(self):
        slider_pos = self.slider.ax.get_position()
        bigger_picture_ax = self.add_axes(
            slider_pos.x0, slider_pos.y1, slider_pos.width, 0.4,
            zorder = 1000, frameon=False, alpha = 0.1)

        self.bigger_picture = BirdsEyeWidget(
            self._data, bigger_picture_ax, "bigger_picture",
            self.widget_size, self.window_size, self)