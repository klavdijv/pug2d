# -*- coding: utf-8 -*-

import sf
from .core import Actor


class ShapePoint(object):
    
    def __init__(self, x, y, color=None, outline_color=None):
        self.x = x
        self.y = y
        self.color = color
        self.outline_color = outline_color
        


class Shape(Actor):
    

    def append(self, p0):
        self.object.add_point(p0.x, p0.y, p0.color, p0.outline_color)
    
    
    def __init__(self, p_list=None):
        super(Shape, self).__init__(sf.Shape())
        if p_list is not None:
            for p0 in p_list:
                self.append(p0)
    
    def __getitem__(self, index):
        xy = self.object.get_point_position(index)
        color = self.object.get_point_color(index)
        outline_color = self.object.get_point_outline_color(index)
        return ShapePoint(xy[0], xy[1], color, outline_color)
    
    def __setitem__(self, index, p0):
        o = self.object
        o.set_point_position(index, p0.x, p0.y)
        if p0.color:
            o.set_point_color(index, p0.color)
        if p0.outline_color:
            o.set_point_outline_color(index, p0.outline_color)
    
    def __len__(self):
        return self.object.points_count
    
    @classmethod
    def line(cls, p1x, p1y, p2x, p2y, thickness, color,
             outline=0.0, outline_color=None):
        shape = cls()
        shape.object = sf.Shape.line(p1x, p1y, p2x, p2y, thickness, color,
                                     outline, outline_color)
        return shape
    
    @classmethod
    def rectangle(cls, left, top, width, height, color,
                  outline=0.0, outline_color=None):
        shape = cls()
        shape.object = sf.Shape.rectangle(left, top, width, height, color,
                                          outline, outline_color)
        return shape

    
    @classmethod
    def circle(cls, x, y, radius, color, outline=0.0, outline_color=None):
        shape = cls()
        shape.object = sf.Shape.circle(x, y, radius, color,
                                       outline, outline_color)
        return shape
