# -*- coding: utf-8 -*-

from .events import EventNotifier

class BaseBehavior(EventNotifier):
    def __init__(self):
        super(BaseBehavior, self).__init__()
        self.actor = None
    
    def initialize(self):
        pass
    
    def move(self, x, y):
        raise NotImplemented()
    
    def rotate(self, a):
        raise NotImplemented()
    
    def stop(self, movement=False, rotation=False):
        raise NotImplemented()
    
    def update(self, game, dt):
        self.actor.update(game, dt)
    
    def cleanup(self):
        pass


class DefaultBehavior(BaseBehavior):
    def move(self, x, y):
        self.actor.object.move(x, y)
    
    def rotate(self, a):
        self.actor.object.rotate(a)
    
    def update(self, game, dt):
        super(DefaultBehavior, self).update(game, dt)

    def stop(self, movement=False, rotation=False):
        pass
