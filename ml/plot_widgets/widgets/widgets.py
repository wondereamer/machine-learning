'''
Author: your name
Date: 2022-02-12 08:05:30
LastEditTime: 2022-06-25 10:41:22
LastEditors: wondereamer wells7.wong@gmail.com
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/widgets/fame_widgets.py
'''
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.collections import LineCollection
from matplotlib.widgets import MultiCursor

from typing import List, Dict
from ml.plot_widgets.plotters.plotter import Candles, SliderPlotter
from ml.plot_widgets.base import BaseAxesWidget
from ml.plot_widgets.formater import TimeFormatter
from ml.plot_widgets.events import MouseMotionEvent, ButtonPressEvent
from ml.finance.datastruct import TradeSide, Signal, Deal
from ml.log import wlog as log


def cursor_strtime_format(delta):
    """ 根据时间间隔判断周期及slider右侧时间相应的显示形式 """
    if delta.days >= 1:
        if delta.days == 1:
            return '%Y-%m-%d'
        return '%Y-%m'
    else:
        return '%H:%M'

class PlotterWidget(BaseAxesWidget):
    """
    """
    def __init__(self, ax, name, widget_size=None, window_size=None, parent=None):
        BaseAxesWidget.__init__(self, ax, name, widget_size, window_size, parent)
        self.plotters = { }
        self.twinx_plotters = set()

    def add_plotter(self, plotter, twinx):
        """ 添加并绘制, 不允许重名的plotter """
        if plotter.name in self.plotters:
            raise
        if twinx:
            self.twinx_plotters.add(plotter)
        else:
            self.plotters[plotter.name] = plotter

    def on_button_press(self, event):
        pass

    def show(self):
        plt.show()


#  widget -- axes  --- n plotters
#   widget计算所有的 plotters的y_max, y_min, 然后再调整axes, 这里有重复计算的问题。
#  widget.events --> plotter.events
#  twinx plotters --> 计算窗口


class Widget(PlotterWidget):
    """ 带滑动事件响应支持的PlotterWidget, 但本身不带滑块控件

    """

    def __init__(self, ax, name, widget_size, window_size, parent=None):
        PlotterWidget.__init__(self, ax, name, widget_size, window_size, parent)
        self.window_left = widget_size - window_size
        self.update_plotter_xylim(self.window_left, widget_size)

    def on_slider(self, event):
        for plotter in self.plotters.values():
            plotter.on_slider(event)
        if event.name in [ MouseMotionEvent, ButtonPressEvent ]:
            self.update_window_position(event.position)

    def update_window_postion(self, left):
        super().update_window_position(left)
        self.update_plotter_xylim(self.window_left, self.window_right)

    def update_plotter_xylim(self, w_left, w_right):
        all_ymax = []
        all_ymin = []
        w_left = int(w_left)
        w_right = int(w_right)
        for plotter in self.plotters.values():
            assert w_right > w_left
            if plotter in self.twinx_plotters:
                log.info("Inore intervals of window: " + plotter.name)
                # continue
            ymax, ymin = plotter.y_interval(w_left, w_right)
            ## @todo move ymax, ymin 计算到plot中去。
            all_ymax.append(ymax)
            all_ymin.append(ymin)
        if len(self.plotters) == 0:
            return
        ymax = max(all_ymax)
        ymin = min(all_ymin)
        self._voffset = (ymax-ymin) / 10.0 # 画图显示的y轴留白。
        ymax += self._voffset
        ymin -= self._voffset
        self.ax.set_ylim((ymin, ymax))
        self.ax.set_xlim(w_left, w_right)

    def on_key_release(self, event):
        log.debug("Key pressed event: %s" % event.key)
        if event.key == u"down":
            middle = (self.window_left + self.window_right) / 2
            self.window_left =  max(1, int(middle - self.window_size))
            self.window_size = min(self.widget_size, self._window_size * 2)
            self.update_plotter_xylim(self.window_left, self.window_right)

            middle = (self.window_left + self.window_right) / 2
            log.debug("window: ")
            log.debug((self.window_left, middle, self.window_right, self.window_size))

        elif event.key == u"up" :
            middle = (self.window_left + self.window_right) / 2
            self.window_size = min(self.widget_size, int(self._window_size / 2))
            self.window_left =  max(1, int(middle - self.window_size/2))
            self.update_plotter_xylim(self.window_left, self.window_right)

            log.debug("window: ")
            middle = (self.window_left + self.window_right) / 2
            log.debug((self.window_left, middle, self.window_right, self.window_size))


class BirdsEyeWidget(Widget):

    def __init__(self, price_data, ax, name, widget_size, window_size, parent=None):
        Widget.__init__(self, ax, name, widget_size, window_size, parent)
        self._data = price_data
        self._plot_candle()
        self._slider_cursor = None

    def _plot_candle(self):
        self.ax.plot(self._data.close.values)
        self.ax.set_ylim((min(self._data['low']), max(self._data['high'])))
        self.ax.set_xlim(0, len(self._data))
        self.ax.set_xticklabels([]);
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_visible(False)

    def on_slider(self, event):
        """ 滑块事件处理。 """
        if event.name == "button_press_event":
            self.ax.set_visible(True)
            self._slider_cursor = MultiCursor(event.canvas, [self.ax],
                color='y', lw=2, horizOn=False, vertOn=True)

        elif event.name == "button_release_event":
            self.ax.set_visible(False)
            del self._slider_cursor


class CandleWidget(Widget):

    def __init__(self, price_data, ax, name, widget_size, window_size, parent=None):
        Widget.__init__(self, ax, name, widget_size, window_size, parent)
        self._data = price_data
        self._data['row'] = [i for i in range(0, len(self._data))]
        self.signal_x = []
        self._indicators = {}

    def plot_candle(self):
        # only plot candle use plotter, avoid other plot invoking y_interval
        candles = Candles(self._data, 'candles')
        candles.plot(self.ax)
        self.add_plotter(candles, False)
        delta = (self._data.index[1] - self._data.index[0])
        self.ax.xaxis.set_major_formatter(TimeFormatter(self._data.index, delta))
        self.ax.set_xticks(self._xticks_to_display(0, len(self._data), delta));
        self.ax.format_coord = self._format_coord

    def plot_line(self, name, data, *args, **kwargs):
        # 默认共用axes, 绕过了窗口设置
        ax = self.ax
        line = SliderPlotter(ax, name, data, data)
        plot = line.ax.twinx().plot(data, *args, **kwargs)
        self.add_plotter(line, True)
        return plot

    def plot_indicators(self, indicators: List[Dict]):
        for i, indic in enumerate(indicators):
            series: pd.Series = indic["values"]
            y = series.values.tolist()
            # TODO 优化，计算出初始偏移
            x = [self._data.row[t] for t in series.index]
            self.ax.plot(x, y)
            self._indicators[indic["name"]] = series

    def _plot_signals(self, signals: pd.Series, color: str, marker: str, offset: float=-0.5):
        x = [self._data.row[time]+offset for time in signals.index]
        return self.ax.scatter(x, signals.values, color=color, marker=marker)

    def plot_signals(self, signals):
        colors = []
        for k, s in signals.items():
            signals[k] = self._data.open[k]
            color = 'r' if s == 1 else 'g'
            colors.append(color)
            pos = self._data.index.searchsorted(k)
            assert self._data.index[pos] == k
            self.signal_x.append(pos)
        return self._plot_signals(signals, colors, ">")

    def plot_trades(self, trades):
        data = []
        colors = []
        for trade in trades:
            # trade.open_price可能偏移出当前窗口，无法显示。及有可能是价格的问题。
            # 可以做冗余显示，把价格也标出来。只标成交价容易忽视问题。 
            # ((x0, y0), (x1, y1))
            p = ((self._data.row[trade.entry_time], self._data.open[trade.entry_time]),
                 (self._data.row[trade.exit_time], self._data.open[trade.exit_time]))
            data.append(p)
            colors.append("r" if trade.profit > 0 else "g")
        use_tuple = 0
        lines = LineCollection(data, colors=colors, linewidths=1, antialiaseds=use_tuple)
        return self.ax.add_collection(lines)

    def draw_widget(self):
        pass

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

    def _format_coord(self, x, y):
        """ 状态栏信息显示 """
        index = x
        f = x % 1
        index = x-f if f < 0.5 else min(x-f+1, len(self._data['open']) - 1)
        delta = (self._data.index[1] - self._data.index[0])
        fmt = cursor_strtime_format(delta)
        ## @note 字符串太长会引起闪烁
        index = int(index)
        time = self._data.index[index]
        return "[index=%s, dt=%s, o=%.2f, c=%.2f, h=%.2f, l=%.2f]" % (
                index,
                self._data.index[index].strftime(fmt),
                self._data['open'][index],
                self._data['close'][index],
                self._data['high'][index],
                self._data['low'][index],
                )