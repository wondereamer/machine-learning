'''
Author: your name
Date: 2022-02-13 22:00:56
LastEditTime: 2022-02-14 12:48:56
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
        if (hasattr(event, "source") and event.source == self.name):
            # ingore event emitted by self
            return

        if (set_source):
            setattr(event, "source", self.name)

        self.handle_event(event)

        if self.parent is not None:
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