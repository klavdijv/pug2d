# -*- coding: utf-8 -*-

class EventNotifier(object):
    def __init__(self):
        self.event_handlers = {}
    
    def add_event_handler(self, event_name, handler):
        self.event_handlers.setdefault(event_name, []).append(handler)
    
    def remove_event_handler(self, event_name, handler):
        self.event_handlers.get(event_name, []).remove(handler)
    
    def raise_event(self, event_name, *args, **kws):
        for handler in self.event_handlers.get(event_name, []):
            handler(*args, **kws)


class EventHandler(object):
    def filter(self, *args, **kws):
        return True
    
    def handle(self, *args, **kws):
        pass
    
    def __call__(self, *args, **kws):
        if self.filter(*args, **kws):
            self.handle(*args, **kws)
