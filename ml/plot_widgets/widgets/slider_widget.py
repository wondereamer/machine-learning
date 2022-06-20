'''
Author: your name
Date: 2022-02-12 08:08:34
LastEditTime: 2022-06-06 08:52:27
LastEditors: wondereamer wells7.wong@gmail.com
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/widgets/slider_widget.py
'''

import six
import numpy as np
from ml.plot_widgets.base import BaseAxesWidget
from ml.log import wlog as log


class SliderFormatter(object):

    def __init__(self, index):
        self._index = index
        self._num_seps = 4

    def format_value(self, x):
        """ 滑块右侧的文字"""
        ind = int(round(x))
        if ind >= len(self._index) or ind < 0: return ''
        return str(ind)

    def xticks_to_display(self, valmax):
        interval = valmax / self._num_seps
        v = 0
        xticks = []
        for i in range(0, self._num_seps):
            xticks.append(v)
            v += interval
        return xticks


class TimeSliderFormatter(SliderFormatter):

    def __init__(self, index):
        SliderFormatter.__init__(self, index)
        self._delta = index[1] - index[0]
        self._value_formatter = self._compute_value_formatter(self._delta)
        self._dates = np.unique(self._index.date)

    def format_value(self, x):
        """ 滑块右侧的文字"""
        ind = int(round(x))
        if ind >= len(self._index) or ind < 0: return ''
        return self._index[ind].strftime(self._value_formatter)

    def xticks_to_display(self, valmax):
        # # 显示横坐标的间隔
        # # delta = < day = 天为单位, 计算出几天
        # # delata = day   月, 计算出几个月
        # # delata = week  年
        # # TODO 不完全准确。
        # interval = valmax / len(self._dates)
        # v = 0
        # xticks = []
        # for i in range(0, len(self._dates)):
        #     xticks.append(v)
        #     v += interval
        # return xticks
        return []

    def _compute_value_formatter(self, delta):
        """ 根据时间间隔判断周期及slider右侧时间相应的显示形式 """
        if delta.days >= 1:
            return '%Y-%m'
        else:
            return '%H:%M'




class Slider(BaseAxesWidget):
    """
    A slider representing a floating point range

    The following attributes are defined
      *ax*        : the slider :class:`matplotlib.axes.Axes` instance

      *val*       : the current slider value

      *vline*     : a :class:`matplotlib.lines.Line2D` instance
                     representing the initial value of the slider

      *poly*      : A :class:`matplotlib.patches.Polygon` instance
                     which is the slider knob

      *valfmt*    : the format string for formatting the slider text

      *label*     : a :class:`matplotlib.text.Text` instance
                     for the slider label

      *closedmin* : whether the slider is closed on the minimum

      *closedmax* : whether the slider is closed on the maximum

      *slidermin* : another slider - if not *None*, this slider must be
                     greater than *slidermin*

      *slidermax* : another slider - if not *None*, this slider must be
                     less than *slidermax*

      *drag_enabled*  : allow for mouse dragging on slider

    Call :meth:`add_observer` to connect to the slider event
    """

    def __init__(self, ax, name, widget_size, window_size, parent, label, valmin, valmax, formatter, valinit=0.5, width=1, valfmt='%1.2f',
                 time_index = None, closedmin=True, closedmax=True, slidermin=None,
                 slidermax=None, drag_enabled=True, **kwargs):
        """
        Create a slider from *valmin* to *valmax* in axes *ax*

        *valinit*
            The slider initial position

        *label*
            The slider label

        *valfmt*
            Used to format the slider value

        *closedmin* and *closedmax*
            Indicate whether the slider interval is closed

        *slidermin* and *slidermax*
            Used to constrain the value of this slider to the values
            of other sliders.

        additional kwargs are passed on to ``self.poly`` which is the
        :class:`matplotlib.patches.Rectangle` which draws the slider
        knob.  See the :class:`matplotlib.patches.Rectangle` documentation
        valid property names (e.g., *facecolor*, *edgecolor*, *alpha*, ...)
        """
        BaseAxesWidget.__init__(self, ax, name, widget_size, window_size, parent)
        self.label = ax.text(-0.02, 0.5, label, transform=ax.transAxes,
                             verticalalignment='center',
                             horizontalalignment='right')
        self._formatter = formatter
        self.valtext = None
        self.poly = None
        self.reinit(valmin, valmax, valinit, width, valfmt, time_index, **kwargs)

        self.cnt = 0
        self.closedmin = closedmin
        self.closedmax = closedmax
        self.slidermin = slidermin
        self.slidermax = slidermax
        self.drag_active = False
        self.drag_enabled = drag_enabled
        self.moved_handlers = []
        ax.set_yticks([])
        self.connect_event_handlers()

        #ax.set_xticks([]) # disable ticks
        ax.set_navigate(False)

    def reinit(self, valmin, valmax, valinit=0.5, width=1, valfmt='%1.2f',
            time_index = None, **kwargs):
        """ [valmin, valmax] """
        self.ax.set_xticks(self._formatter.xticks_to_display(valmax))
        self._index = time_index
        self.valmin = valmin
        self.valmax = valmax
        self.val = valinit
        self.valinit = valinit
        self.width = width
        self.valfmt = valfmt
        self.ax.set_xlim((valmin, valmax))
        self._data_length = valmax

        if self.valtext:
            self.valtext.remove()
        if self.poly:
            self.poly.remove()
        # 滑动条的形状
        self.poly = self.ax.axvspan(valinit-self.width/2, valinit+self.width/2, 0, 1, **kwargs)
        #axhspan
        #self.vline = ax.axvline(valinit, 0, 1, color='r', lw=1)

        #self.valtext = ax.text(1.02, 0.5, valfmt % valinit,
        self.valtext = self.ax.text(1.005, 0.5,self._formatter.format_value(valinit),
                               transform=self.ax.transAxes,
                               verticalalignment='center',
                               horizontalalignment='left')

    def add_observer(self, handler):
        """
        When the slider value is changed, call *func* with the new
        slider position

        A connection id is returned which can be used to disconnect
        """
        self.moved_handlers.append(handler)

    def remove_observer(self, cid):
        """remove the observer with connection id *cid*"""
        self.moved_handlers.remove(cid)

    def reset(self):
        """reset the slider to the initial value if needed"""
        if (self.val != self.valinit):
            self._set_val(self.valinit)

    def on_mouse_motion(self, event):
        if not self.drag_enabled:
            return
        if event.button != 1 or not self.drag_active:
            return
        self._update(event.xdata)
        setattr(event, "position", self.val)
        self._notify_observer(event)

    def on_button_release(self, event):
        if event.button != 1 or not self.drag_active:
            return
        if  event.inaxes == self.ax:
            self.drag_active = False
            event.canvas.release_mouse(self.ax)
            setattr(event, "position", self.val)
            self._notify_observer(event)

    def on_button_press(self, event):
        if event.button != 1:
            return
        if event.inaxes == self.ax:
            self.drag_active = True
            event.canvas.grab_mouse(self.ax)
            setattr(event, "position", self.val)
            self._notify_observer(event)
        else:
            self.drag_active = False
            event.canvas.release_mouse(self.ax)

    def _update(self, val, width=None):
        if val <= self.valmin:
            if not self.closedmin:
                return
            val = self.valmin
        elif val >= self.valmax:
            if not self.closedmax:
                return
            val = self.valmax

        if self.slidermin is not None and val <= self.slidermin.val:
            if not self.closedmin:
                return
            val = self.slidermin.val

        if self.slidermax is not None and val >= self.slidermax.val:
            if not self.closedmax:
                return
            val = self.slidermax.val
        if width:
            self.width = width

        xy = self.poly.xy
        xy[2] = val, 1
        xy[3] = val, 0
        self.val = val
        self.poly.remove()  # 删除滑块
        self.poly = self.ax.axvspan(val-self.width/2, val+self.width/2, 0, 1)  # 重建滑块
        self.valtext.set_text(self._formatter.format_value(val))
        self.val = val

    def _notify_observer(self, event):
        """ 通知相关窗口更新数据 """
        for handler in self.moved_handlers:
            handler(event)