# -*- coding: utf-8 -*-

from . import core
from .behaviors import BaseBehavior
import pymunk
import math
import ctypes

TIMESTEP = 1.0/60.0
HEIGHT = 600


P_PYOBJECT = ctypes.POINTER(ctypes.py_object)

def pyobj_to_voidp(obj):
    p_obj = P_PYOBJECT(ctypes.py_object(obj))
    return ctypes.cast(p_obj, ctypes.c_void_p)

def voidp_to_pyobj(p):
    p_obj = ctypes.cast(p, P_PYOBJECT)
    return p_obj.contents.value


class PymunkLevel(core.Level):
    
    def __init__(self, space):
        super(PymunkLevel, self).__init__()
        self.space = space
    
    def convert_coords(self, pos):
        return pos[0], HEIGHT-pos[1]
    
    def update(self, game, dt):
        if dt:
            time_step = TIMESTEP
        else:
            # Game is paused
            time_step = 0.0
        self.space.step(time_step)
        super(PymunkLevel, self).update(game, dt)


class PymunkBehavior(BaseBehavior):
    
    def __init__(self, body, shapes=None):
        super(PymunkBehavior, self).__init__()
        body._bodycontents.data = pyobj_to_voidp(self)
        self.body = body
        if shapes is None:
            self.shapes = []
        elif isinstance(shapes, pymunk.Shape):
            self.shapes = [shapes]
        else:
            self.shapes = shapes
    
    def on_start(self):
        space = self.actor.layer.level.space
        body = self.body
        if body not in space._bodies:
            space.add(body, *self.shapes)
    
    def move(self, x, y):
        self.body.velocity = (x/TIMESTEP, y/TIMESTEP)
    
    def rotate(self, a):
        self.body.angular_velocity = math.radians(a)/TIMESTEP
    
    def stop(self, movement=False, rotation=False):
        if movement:
            self.body.velocity = (0.0, 0.0)
        if rotation:
            self.body.angular_velocity = 0.0
    
    def update(self, game, dt):
        sf_obj = self.actor.object
        body = self.body
        sf_obj.position = game.level.convert_coords(body.position)
        sf_obj.rotation = math.degrees(body.angle)
        super(PymunkBehavior, self).update(game, dt)
    
    def on_end(self):
        space = self.actor.layer.level.space
        space.remove(self.body, *self.shapes)
