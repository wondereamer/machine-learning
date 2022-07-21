# -*- coding: utf-8 -*-
from re import S

from ml.plot_widgets.base import BaseFigureFrame
from ml.plot_widgets.widgets.widgets import CandleWidget, Widget, BirdsEyeWidget
from ml.plot_widgets.widgets.slider_widget import Slider, TimeSliderFormatter
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
        if isinstance(widget, Widget):
            if self._slider is None:
                log.warn("Slider should be create before adding widget.")
            else:
                self._slider.add_observer(widget.on_slider)
        return widget

    def create_slider(self, slider_axes, index):
        formatter = TimeSliderFormatter(index)
        slider = Slider(slider_axes, "slider", self.widget_size, self.window_size,
            self, '', 0, self.widget_size-1, formatter, self.widget_size-1, self.widget_size/50, "%d", index)
        self._slider = slider
        self._slider.add_observer(self.on_slider)
        return self._slider

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
            if not isinstance(subwidget, Widget):
                continue
            try:
                subwidget.update_plotter_xylim(subwidget.window_left, subwidget.window_right)
            except Exception as e:
                raise Exception("设置窗口位置失败 %s" % subwidget.name)

    def on_key_release(self, event):
        log.debug("key pressed event: '%s'" % event.key)
        for subwidget in self._child_widgets:
            subwidget.on_key_release(event)
        log.debug("canvas.draw")
        self._fig.canvas.draw()
        # elif event.key == u"super+up":

        if event.key == u"down":
            middle = (self.window_left + self.window_right) / 2
            self.window_left =  max(1, int(middle - self.window_size))
            self.window_size = min(self.widget_size, self._window_size * 2)

        elif event.key == u"up" :
            middle = (self.window_left + self.window_right) / 2
            self.window_size = min(self.widget_size, int(self._window_size / 2))
            self.window_left =  max(1, int(middle - self.window_size/2))

    def on_slider(self, event):
        self.update_window_position(event.position)
        event.canvas.draw()


    def update_window_position(self, window_left_position):
        super().update_window_position(window_left_position)
        for subwidget in self._child_widgets:
            subwidget.update_window_postion(window_left_position)

