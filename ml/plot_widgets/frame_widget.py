'''
Author: your name
Date: 2022-02-12 08:05:30
LastEditTime: 2022-03-06 16:11:41
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/widgets/fame_widgets.py
'''
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.widgets import MultiCursor

from ml.plot_widgets.plotter import Candles
from ml.plot_widgets.base_widget import BaseAxesWidget
from ml.plot_widgets.formater import TimeFormatter
from ml.plot_widgets.slider_widget import slider_strtime_format
from ml.plot_widgets.events import MouseMotionEvent, ButtonPressEvent
from ml.finance.datastruct import TradeSide
from ml.log import wlog as log

class AxesWidget(BaseAxesWidget):
    """
    """
    def __init__(self, ax, name, widget_size=None, window_size=None, parent=None):
        BaseAxesWidget.__init__(self, ax, name, widget_size, window_size, parent)
        self.plotters = { }
        self.ax = ax
        self.twinx_plotters = set()

    def add_plotter(self, plotter, twinx):
        """ 添加并绘制, 不允许重名的plotter """
        if plotter.name in self.plotters:
            raise
        self.plotters[plotter.name] = plotter
        if twinx:
            self.twinx_plotters.add(plotter)

    def add_plot(self, plot, name):
        self.plotters[name] = plot

    def on_button_press(self, event):
        pass

    def show(self):
        plt.show()


#  widget -- axes  --- n plotters
#   widget计算所有的 plotters的y_max, y_min, 然后再调整axes, 这里有重复计算的问题。
#  widget.events --> plotter.events
#  twinx plotters --> 计算窗口


class SliderAxesWidget(AxesWidget):
    """ 带滑动事件响应支持的AxesWidget, 但本身不带滑块控件

    Args:
        AxesWidget (AxesWidget): Axes窗口
    """

    def __init__(self, ax, name, widget_size, window_size, parent=None):
        AxesWidget.__init__(self, ax, name, widget_size, window_size, parent)
        self.window_left = widget_size - window_size
        self.set_window_interval(self.window_left, widget_size)

    def on_slider(self, event):
        for plotter in self.plotters.values():
            plotter.on_slider(event)
        if event.name in [ MouseMotionEvent, ButtonPressEvent ]:
            self._update_window(event.position)

    def set_window_postion(self, middle):
        """ 设置窗口的中间位置

        Args:
            middle (int): 中间位置坐标
        """
        self.window_left = middle - self.window_size / 2
        self._update_window(self._window_left)

    def _update_window(self, left):
        self.update_window_position(left)
        self.set_window_interval(self.window_left, self.window_right)
        log.debug("window_left: {0}, window_right: {1}, slider_pos: {2}".format(
            self.window_left, self.window_right, left
        ))

    def set_window_interval(self, w_left, w_right):
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
        if event.key == u"down":
            middle = (self.window_left + self.window_right) / 2
            self.window_left =  max(1, int(middle - self.window_size))
            self.window_size = min(self.widget_size, self._window_size * 2)
            self.set_window_interval(self.window_left, self.window_right)

            middle = (self.window_left + self.window_right) / 2
            log.debug("window: ")
            log.debug((self.window_left, middle, self.window_right, self.window_size))

        elif event.key == u"up" :
            middle = (self.window_left + self.window_right) / 2
            self.window_size = min(self.widget_size, int(self._window_size / 2))
            self.window_left =  max(1, int(middle - self.window_size/2))
            self.set_window_interval(self.window_left, self.window_right)

            log.debug("window: ")
            middle = (self.window_left + self.window_right) / 2
            log.debug((self.window_left, middle, self.window_right, self.window_size))


class BirdsEyeWidget(SliderAxesWidget):

    def __init__(self, price_data, ax, name, widget_size, window_size, parent=None):
        SliderAxesWidget.__init__(self, ax, name, widget_size, window_size, parent)
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


class CandleWidget(SliderAxesWidget):

    def __init__(self, price_data, ax, name, widget_size, window_size, parent=None):
        SliderAxesWidget.__init__(self, ax, name, widget_size, window_size, parent)
        self._data = price_data
        self._data['row'] = [i for i in range(0, len(self._data))]

    def plot_candle(self):
        candles = Candles(self._data, 'candles')
        candles.plot(self.ax)
        self.add_plotter(candles, False)

        delta = (self._data.index[1] - self._data.index[0])
        self.ax.xaxis.set_major_formatter(TimeFormatter(self._data.index, delta))
        self.ax.set_xticks(self._xticks_to_display(0, len(self._data), delta));
        self.ax.format_coord = self._format_coord

    def plot_line(self, data, *args, **kwargs):
        # 默认共用axes, 绕过了窗口设置
        return self.ax.plot(data, *args, **kwargs)

    def plot_signals(self, deals):
        signals = []
        for deal in deals:
            signals.append((deal.open_time, self._data.open[deal.open_time], TradeSide.Open))
            if deal.close_time is not None:
                signals.append((deal.close_time, self._data.open[deal.close_time], TradeSide.Close))
        signal_x = []
        signal_y = []
        colors = []
        for signal in signals:
            signal_x.append(self._data.row[signal[0]] - 0.5)
            signal_y.append(signal[1])
            if signal[2] == TradeSide.Open:
                colors.append("r")
            else:
                colors.append("g")
        return self.ax.scatter(signal_x, signal_y, c=colors, marker=">")

    def plot_deals(self, deals):
        data = []
        colors = []
        for deal in deals:
            # deal.open_price可能偏移出当前窗口，无法显示。及有可能是价格的问题。
            # 可以做冗余显示，把价格也标出来。只标成交价容易忽视问题。 
            # ((x0, y0), (x1, y1))
            p = ((self._data.row[deal.open_time], self._data.open[deal.open_time]),
                 (self._data.row[deal.close_time], self._data.open[deal.close_time]))
            data.append(p)
            colors.append("r" if deal.profit > 0 else "g")
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
        fmt = slider_strtime_format(delta)
        ## @note 字符串太长会引起闪烁
        index = int(index) - 1
        return "[dt=%s o=%.2f c=%.2f h=%.2f l=%.2f]" % (
                self._data.index[index].strftime(fmt),
                self._data['open'][index],
                self._data['close'][index],
                self._data['high'][index],
                self._data['low'][index])