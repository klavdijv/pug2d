# -*- coding: utf-8 -*-

import sf

class AttrDict(dict):
    '''A dictionary with attribute access to its items'''
    
    def __getattr__(self, name):
        return self.__getitem__(name)
    
    def __setattr__(self, name, value):
        super(AttrDict, self).__setattr__(name, value)
        self.__setitem__(name ,value)
    
    def __delattr__(self, name):
        self.__delitem__(name)


def joy_move(axis, dir):
    if dir == -1:
        return sf.Joystick.get_axis_position(axis) < 0
    if dir == 1:
        return sf.Joystick.get_axis_position(axis) > 0
    return False

_event_map = {'key': sf.Keyboard.is_key_pressed,
              'mouse_button': sf.Mouse.is_button_pressed,
              'joy_button': sf.Joystick.is_button_pressed,
              'joy_move': joy_move}


class SingleEvent(object):
    def __init__(self, event_name, *args):
        self.event_func = _event_map[event_name]
        self.args = args
    
    def __call__(self):
        return self.event_func(*self.args)


class InputEvent(object):
    def __init__(self, mode, *event_defs):
        if mode == 'all':
            self.mode = all
        elif mode == 'any':
            self.mode = any
        elif mode == '' or mode == 'single':
            self.mode = None
        else:
            msg = 'mode: expected "single", "all" or "any", got {0}'.format(mode)
            raise ValueError(msg)
        self.events = []
        for event_def in event_defs:
            if isinstance(event_def, InputEvent):
                self.events.append(event_def)
            else:
                ev_name = event_def[0]
                args = event_def[1:]
                self.events.append(SingleEvent(ev_name, *args))
        if self.mode is None:
            self.events = self.events[0]
    
    def __call__(self):
        if self.mode:
            return self.mode(event() for event in self.events)
        return self.events()


class InputEventHandler(object):
    def __init__(self, name, input_event):
        self.name = name
        self.input_event = input_event
    
    def __call__(self):
        return self.name if self.input_event() else None


class InputHandler(object):
    def __init__(self):
        self.input_event_handlers = []
    
    def add(self, name, input_event):
        self.input_event_handlers.append(InputEventHandler(name, input_event))
    
    def __call__(self):
        res = []
        for event_handler in self.input_event_handlers:
            event_name = event_handler()
            if event_name:
                res.append(event_name)
        return res
