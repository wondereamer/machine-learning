'''
Author: your name
Date: 2022-02-12 08:08:34
LastEditTime: 2022-02-15 07:02:03
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/widgets/slider_widget.py
'''

import six
from matplotlib.widgets import AxesWidget
from .base_widget import BaseWidget



def slider_strtime_format(delta):
    """ 根据时间间隔判断周期及slider上相应的显示形式 """
    if delta.days >= 1:
        return '%Y-%m'
    elif delta.seconds == 60:
        return '%H:%M'
    else:
        # 日内其它分钟
        return '%H:%M'


class Slider(AxesWidget, BaseWidget):
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

    def __init__(self, fig, ax, name, parent, label, valmin, valmax, valinit=0.5, width=1, valfmt='%1.2f',
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
        BaseWidget.__init__(self, name, fig, parent)
        AxesWidget.__init__(self, ax)
        self.label = ax.text(-0.02, 0.5, label, transform=ax.transAxes,
                             verticalalignment='center',
                             horizontalalignment='right')
        self.valtext = None
        self.poly = None
        self.reinit(valmin, valmax, valinit, width, valfmt, time_index, **kwargs)

        self.name = name
        self.cnt = 0
        self.closedmin = closedmin
        self.closedmax = closedmax
        self.slidermin = slidermin
        self.slidermax = slidermax
        self.drag_active = False
        self.drag_enabled = drag_enabled
        self.observers = {}
        ax.set_yticks([])
        self.connect_event_handlers()

        #ax.set_xticks([]) # disable ticks
        ax.set_navigate(False)

    def _xticks_to_display(self, valmax):
        interval = valmax / 5
        v = 0
        xticks = []
        for i in range(0, 6):
            xticks.append(v)
            v += interval
        return xticks


    def _value_format(self, x):
        """docstring for timess"""
        ind = int(round(x))
        if ind>=len(self._index) or ind<0: return ''
        return self._index[ind].strftime(self._fmt)


    def reinit(self, valmin, valmax, valinit=0.5, width=1, valfmt='%1.2f',
            time_index = None, **kwargs):
        """ [valmin, valmax] """
        self.ax.set_xticks(self._xticks_to_display(valmax))
        self._index = time_index
        self.valmin = valmin
        self.valmax = valmax
        self.val = valinit
        self.valinit = valinit
        self.width = width
        self.valfmt = valfmt
        self._fmt = slider_strtime_format(time_index[1] - time_index[0])
        self.ax.set_xlim((valmin, valmax))
        self._data_length = valmax

        if self.valtext:
            self.valtext.remove()
        if self.poly:
            self.poly.remove()
        # 滑动条的形状
        self.poly = self.ax.axvspan(valmax-self.width/2,valmax+self.width/2, 0, 1, **kwargs)
        #axhspan
        #self.vline = ax.axvline(valinit, 0, 1, color='r', lw=1)

        #self.valtext = ax.text(1.02, 0.5, valfmt % valinit,
        self.valtext = self.ax.text(1.005, 0.5,self._value_format(valinit),
                               transform=self.ax.transAxes,
                               verticalalignment='center',
                               horizontalalignment='left')

    def add_observer(self, obj):
        """
        When the slider value is changed, call *func* with the new
        slider position

        A connection id is returned which can be used to disconnect
        """
        self.observers[obj.name] = obj

    def remove_observer(self, cid):
        """remove the observer with connection id *cid*"""
        try:
            del self.observers[cid]
        except KeyError:
            pass

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
        setattr(event, "update_observer", True)
        self._update_observer(event)

    def on_button_release(self, event):
        if event.button != 1 or not self.drag_active:
            return
        if  event.inaxes == self.ax:
            self.drag_active = False
            event.canvas.release_mouse(self.ax)
            self._update_observer(event)

    def on_button_press(self, event):
        print(self.name + ".get.." + event.source)
        print(event.inaxes == self.ax)
        if event.button != 1:
            return
        if event.inaxes == self.ax:
            self.drag_active = True
            event.canvas.grab_mouse(self.ax)
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
        self._set_val(val)


    def _set_val(self, val):
        xy = self.poly.xy
        xy[2] = val, 1
        xy[3] = val, 0
        self.val = val
        self.poly.remove()
        self.poly = self.ax.axvspan(val-self.width/2, val+self.width/2, 0, 1)
        #self.poly.xy = xy
        #self.valtext.set_text(self.valfmt % val)
        self.valtext.set_text(self._value_format(val))
        self.val = val
        if not self.eventson:
            return

    def _update_observer(self, event):
        """ 通知相关窗口更新数据 """
        for name, obj in six.iteritems(self.observers):
            try:
                obj.on_slider(self.val, event)
            except Exception as e:
                six.print_(e)