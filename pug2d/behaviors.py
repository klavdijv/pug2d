# -*- coding: utf-8 -*-

class BaseBehavior(object):
    def __init__(self):
        self.actor = None
    
    def move(self, x, y):
        raise NotImplemented()
    
    def rotate(self, a):
        raise NotImplemented()
    
    def update(self, game):
        raise NotImplemented()


class DefaultBehavior(BaseBehavior):
    def move(self, x, y):
        self.actor.object.move(x, y)
    
    def rotate(self, a):
        self.actor.object.rotate(a)
    
    def update(self, game):
        pass
