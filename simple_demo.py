'''
Author: your name
Date: 2022-02-19 20:32:30
LastEditTime: 2022-02-26 09:35:29
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/simple_demo.py
'''
from json.tool import main
import six
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter
from ml.widgets import mplots
from ml.widgets.technical_widget import TechnicalFrame, MultiWidgetsFrame
from ml.widgets.slider_widget import Slider, slider_strtime_format
from ml.widgets.frame_widget import AxesWidget, SliderAxesWidget, CandleWidget
from ml.widgets.plotter import Line, LineWithX, Volume
import pandas as pd


price_data = pd.read_csv("./test.csv", index_col=0, parse_dates=True)

class TimeFormatter(Formatter):
    # def __init__(self, dates, fmt='%Y-%m-%d'):
    # 分类 －－format
    def __init__(self, dates, fmt='%Y-%m-%d %H:%M'):
        self.dates = dates
        self.fmt = fmt

    def __call__(self, x, pos=0):
        'Return the label for time x at position pos'
        ind = int(round(x))
        if ind >= len(self.dates) or ind < 0:
            return ''
        return self.dates[ind].strftime(self.fmt)


class MyAxesWidget(AxesWidget):

    def __init__(self, ax, name):
        AxesWidget.__init__(self, ax, name)

    def on_button_press(self, event):
        print("my test pressed")


def axes_widget_demo():
    ax = plt.axes()
    widget = MyAxesWidget(ax, "test")
    price_plot = ax.plot(price_data)
    widget.add_plot(price_plot, "price")
    widget.show()


def slider_widget_demo():
    fig = plt.figure()
    axes = []
    axes.append(plt.subplot2grid((5, 1), (0, 0), rowspan=4))
    axes.append(plt.subplot2grid((5, 1), (4, 0)))
    widget_size = len(price_data)
    window_size = 50

    candle_widget = CandleWidget(price_data, axes[0], "test", widget_size, window_size)
    candle_widget.plot_line(price_data.close.values)

    mainwindow = MultiWidgetsFrame(fig, "multi", widget_size, window_size)
    mainwindow.create_slider(axes[1], price_data.index)
    mainwindow.add_widget(candle_widget)


    slider_pos = mainwindow.slider.ax.get_position()
    bigger_picture_ax = mainwindow.add_axes(
        slider_pos.x0, slider_pos.y1, slider_pos.width, 0.4,
        zorder = 1000, frameon=False, alpha = 1)
    bigger_picture_ax.plot(price_data.close.values)
    bigger_picture = AxesWidget(bigger_picture_ax, "bigger_picture")                                        

    mainwindow.add_widget(bigger_picture)

    mainwindow.show()


def technical_widget_demo():
    fig = plt.figure()
    window_size = 50
    widget_size = len(price_data)

    frame = TechnicalFrame(fig, widget_size, window_size)
    frame.load_data(price_data)
    axes = frame.init_layout()

    subwidget1 = CandleWidget(price_data, axes[0], "subwidget1", widget_size, window_size)
    subwidget2 = SliderAxesWidget(axes[1], "subwidget2", widget_size, window_size)

    # 绘制第一个窗口
    # line = Line(price_data.open.values)
    # line.zorder_switch = True
    # subwidget1.add_plotter(line, False)
    subwidget1.plot_line(price_data.close.values)
    # 绘制第2个窗口
    volume_plotter = Volume(price_data.open, price_data.close, price_data.volume)
    subwidget2.add_plotter(volume_plotter, False)

    frame.add_widget(subwidget1)
    frame.add_widget(subwidget2)



    frame.show()


#axes_widget_demo()
#slider_widget_demo()
technical_widget_demo()