'''
Author: your name
Date: 2022-02-13 22:00:56
LastEditTime: 2022-02-22 21:14:17
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/widgets/base_widget.py
'''

from matplotlib.axes import Axes
from matplotlib.widgets import AxesWidget
import matplotlib.pyplot as plt


class BaseWidgetMixin(object):
    def __init__(self, name, widget_size, window_size, parent=None):
        self.name = name
        self.parent = parent
        # start from 1, end with data length
        self._window_left = 1
        self._window_size = window_size
        self._widget_size = widget_size
        self._child_widgets = []
        self.plot = plt
        print("Create Window: {0}[widget size: {1}, window size: {2}]".format(
            self.name, self._widget_size, self._window_size))

    def _on_enter_axes(self, event):
        # fix matplotlib bug, it will dispatch "motion_notify_event"
        event.name = "enter_axes_event"
        self.on_enter_axes(event)
        # event.inaxes.patch.set_facecolor('yellow')

    def _on_leave_axes(self, event):
        # fix matplotlib bug, it will dispatch "motion_notify_event"
        event.name = "leave_axes_event"
        self.on_leave_axes(event)

    @property
    def window_right(self):
        return min(self.window_left + self.window_size, self.widget_size)

    @property
    def window_left(self):
        return self._window_left

    @window_left.setter
    def window_left(self, pos):
        self._window_left = pos

    @property
    def window_size(self):
        return self._window_size

    @window_size.setter
    def window_size(self, size):
        self._window_size = size

    @property
    def widget_size(self):
        return self._widget_size

    @widget_size.setter
    def widget_size(self, size):
        self._widget_size = size

    def on_enter_axes(self, event):
        pass

    def on_leave_axes(self, event):
        pass

    def on_key_release(self, event):
        pass
    
    def on_button_press(self, event):
        pass

    def on_button_release(self, event):
        pass

    def on_mouse_motion(self, event):
        pass

    def connect_event_handlers(self):
        raise NotImplementedError

    def update_window_position(self, position):
        self.window_left = int(position)
        if self.window_right >= self._widget_size:
            self.window_left = int(self.window_right - self._window_size)


class BaseFigureFrame(BaseWidgetMixin):
    def __init__(self, fig, widget_size, window_size, name):
        BaseWidgetMixin.__init__(self, name, widget_size, window_size, None)
        self._fig = fig
        self.connect_event_handlers()

    def connect_event_handlers(self):
        self._fig.canvas.mpl_connect('key_release_event', self.on_key_release)

class BaseAxesWidget(AxesWidget, BaseWidgetMixin):
    def __init__(self, ax, name, widget_size, window_size, parent):
        AxesWidget.__init__(self, ax)
        BaseWidgetMixin.__init__(self, name, widget_size, window_size, parent)
        self.ax = ax
        self.connect_event_handlers()

    def connect_event_handlers(self):
        """
        matplotlib信号连接。
        连多次就会有多次调用, 如果被slider连了, 会有额外的调用。
        """
        # only main widget connect to key events
        self.cidmotion = self.connect_event( "motion_notify_event", self.on_mouse_motion)
        self.connect_event( "button_press_event", self.on_button_press)
        self.connect_event( "button_release_event", self.on_button_release)
        self.connect_event('axes_enter_event', self._on_enter_axes)
        self.connect_event('axes_leave_event', self._on_leave_axes)

    # def _disconnect(self):
    #     self._fig.canvas.mpl_disconnect(self.cidmotion)
