'''
Author: your name
Date: 2022-02-13 22:00:56
LastEditTime: 2022-02-15 08:19:43
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/widgets/base_widget.py
'''

class BaseWidget(object):
    def __init__(self, name, fig, parent=None):
        self._fig = fig
        self.name = name
        self._child_widgets = { }
        self.parent = parent
        self.ax = None

    def _on_enter_axes(self, event):
        # fix matplotlib bug, it will dispatch "motion_notify_event"
        event.name = "enter_axes_event"
        self.on_enter_axes(event)
        # event.inaxes.patch.set_facecolor('yellow')

    def _on_leave_axes(self, event):
        # fix matplotlib bug, it will dispatch "motion_notify_event"
        event.name = "leave_axes_event"
        self.on_leave_axes(event)

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

    def dispatch_event(self, event, set_source=True):
        # make sure child widget won't dispatch event not belong to it.
        if not hasattr(event, "source") and self.ax is not None and event.inaxes != self.ax:
            return

        if (hasattr(event, "source") and event.source == self.name):
            # ingore event emitted by self
            return

        if (set_source):
            setattr(event, "source", self.name)

        self.handle_event(event)

        if self.parent is not None and self.name == event.source:
            self.parent.dispatch_event(event, False)
        for widget in self._child_widgets.values():
            widget.dispatch_event(event, False)
        
    def handle_event(self, event):
        if event.name == "button_press_event":
            self.on_button_press(event)
        elif event.name == "button_release_event":
            self.on_button_release(event)
        elif event.name == "motion_notify_event":
            self.on_mouse_motion(event)
        elif event.name == "key_release_event":
            self.on_key_release(event)

    def connect_event_handlers(self):
        """
        matplotlib信号连接。
        连多次就会有多次调用, 如果被slider连了, 会有额外的调用。
        """
        # only main widget connect to key events
        if self.parent is None:
            if self._fig is None:
                self.key_release = self.connect_event('key_release_event', self.dispatch_event)
            else:
                self.key_release = self._fig.canvas.mpl_connect('key_release_event', self.dispatch_event)
            return


        if self._fig is None:
            self.cidpress = self.connect_event( "button_press_event", self.dispatch_event)
            self.cidrelease = self.connect_event( "button_release_event", self.dispatch_event)
            self.cidmotion = self.connect_event( "motion_notify_event", self.dispatch_event)
            self.axes_enter = self.connect_event('axes_enter_event', self._on_enter_axes)
            self.axes_leave = self.connect_event('axes_leave_event', self._on_leave_axes)
        else:
            self.cidpress = self._fig.canvas.mpl_connect( "button_press_event", self.dispatch_event)
            self.cidrelease = self._fig.canvas.mpl_connect( "button_release_event", self.dispatch_event)
            self.cidmotion = self._fig.canvas.mpl_connect( "motion_notify_event", self.dispatch_event)
            self.axes_enter = self._fig.canvas.mpl_connect('axes_enter_event', self._on_enter_axes)
            self.axes_leave = self._fig.canvas.mpl_connect('axes_leave_event', self._on_leave_axes)


    def _disconnect(self):
        self._fig.canvas.mpl_disconnect(self.cidmotion)
        self._fig.canvas.mpl_disconnect(self.cidrelease)
        self._fig.canvas.mpl_disconnect(self.cidpress)
        self._fig.canvas.mpl_disconnect(self.axes_enter)
        self._fig.canvas.mpl_disconnect(self.axes_leave)
        self._fig.canvas.mpl_disconnect(self.key_release)
