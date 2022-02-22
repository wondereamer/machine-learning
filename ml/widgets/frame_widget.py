'''
Author: your name
Date: 2022-02-12 08:05:30
LastEditTime: 2022-02-26 09:35:00
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/widgets/fame_widgets.py
'''
from lib2to3.pytree import Base
import six
import matplotlib.pyplot as plt
from matplotlib.widgets import MultiCursor
from .mplots import Candles
from .base_widget import BaseAxesWidget
from .formater import TimeFormatter
from .slider_widget import slider_strtime_format

class AxesWidget(BaseAxesWidget):
    """
    """
    def __init__(self, ax, name, widget_size=None, window_size=None, parent=None):
        BaseAxesWidget.__init__(self, ax, name, widget_size, window_size, parent)
        self.plotters = { }
        self.ax = ax

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

    def add_plot(self, plot, name):
        self.plotters[name] = plot

    def on_button_press(self, event):
        pass

    def show(self):
        plt.show()


class SliderAxesWidget(AxesWidget):
    """ 带滑动事件响应支持的AxesWidget

    Args:
        AxesWidget (AxesWidget): Axes窗口
    """

    def __init__(self, ax, name, widget_size, window_size, parent=None):
        AxesWidget.__init__(self, ax, name, widget_size, window_size, parent)

    def on_slider(self, event):
        self._update_window(event.position)

    def set_window_interval(self, w_left, w_right):
        all_ymax = []
        all_ymin = []
        w_left = int(w_left)
        w_right = int(w_right)
        for plotter in six.itervalues(self.plotters):
            # TODO what?
            # if plotter.twinx:
            #     continue
            assert w_right > w_left
            ymax, ymin = plotter.y_interval(w_left, w_right)
            ## @todo move ymax, ymin 计算到plot中去。
            all_ymax.append(ymax)
            all_ymin.append(ymin)
        if len(self.plotters) == 0:
            print("warning: 没有绘图")
            return
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

    def on_key_release(self, event):
        if event.key == u"down":
            middle = (self.window_left + self.window_right) / 2
            self.window_left =  max(1, int(middle - self.window_size))
            self.window_size = min(self.widget_size, self._window_size * 2)
            self.set_window_interval(self.window_left, self.window_right)

            middle = (self.window_left + self.window_right) / 2
            print((self.window_left, middle, self.window_right, self.window_size))

        elif event.key == u"up" :
            middle = (self.window_left + self.window_right) / 2
            self.window_size = min(self.widget_size, int(self._window_size / 2))
            self.window_left =  max(1, int(middle - self.window_size/2))
            self.set_window_interval(self.window_left, self.window_right)

            print("window: ")
            middle = (self.window_left + self.window_right) / 2
            print((self.window_left, middle, self.window_right, self.window_size))


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
        self._plot_candle()

    def _plot_candle(self):
        candles = Candles(self._data, 'candles')
        self.add_plotter(candles, False)
        delta = (self._data.index[1] - self._data.index[0])
        self.ax.xaxis.set_major_formatter(TimeFormatter(self._data.index, delta))
        self.ax.set_xticks(self._xticks_to_display(0, len(self._data), delta));
        self.ax.format_coord = self._format_coord

    def plot_line(self, data):
        self.ax.plot(data, "black", lw=2)

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
