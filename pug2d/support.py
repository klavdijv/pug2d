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


class InputEvent(object):
    def __init__(self, event_name, *args):
        self.event_func = _event_map[event_name]
        self.args = args
    
    def __call__(self):
        return self.event_func(*self.args)


class InputEventList(object):
    def __init__(self, mode, *events):
        if mode == 'all':
            self.mode = all
        elif mode == 'any':
            self.mode = any
        else:
            msg = 'mode: expected "all" or "any", got {0}'.format(mode)
            raise ValueError(msg)
        self.events = events
    
    def __call__(self):
        return self.mode(event() for event in self.events)


class InputEventHandler(object):
    def __init__(self, input_event, callback, *callb_args, **callb_kws):
        self.input_event = input_event
        self.callback = callback
        self.callb_args = callb_args
        self.callb_kws = callb_kws
    
    def __call__(self):
        if self.input_event():
            self.callback(*self.callb_args, **self.callb_kws)
            return True
        return False


class InputHandler(object):
    def __init__(self, *input_event_handlers):
        self.input_event_handlers = input_event_handlers
    
    def __call__(self):
        for event_handler in self.input_event_handlers:
            event_handler()
