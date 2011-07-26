'''
Created on 26. jul. 2011

@author: klavdij
'''

import Box2D as B2D
import math

class ColMixin:
    def __init__(self, shape=None):
        self._basic_shape = shape
        self.transform = B2D.b2Transform()
        self.transform.SetIdentity()
    
    def set_transform(self):
        t = self.transform
        sf_obj = self.object
        t.position = sf_obj.position
        t.angle = math.radians(sf_obj.rotation)
    
    def collide(self, other):
        m = B2D.b2Manifold()
        B2D.b2CollidePolygons(m, self.shape, self.transform,
                              other.shape, other.transf)
        return m
    
    def collides_with(self, other):
        m = self.collide(other)
        return bool(m.pointCount)
    
    def rescaled_shape(self):
        vertices = []
        c = self._basic_shape.centroid
        for v in self._basic_shape.vertices:
            vv = B2D.b2Vec2(*v)
            vertices.append((c+self.object.scale*(c-vv)).tuple)
        return B2D.b2PolygonShape(vertices)
    
    @property
    def shape(self):
        if self.object.scale != 1.0:
            return self.rescaled_shape()
        return self._basic_shape
    
    @classmethod
    def create_collision_class(cls, base_cls, name):
        def __init__(self, *args, **kws):
            shape = kws.pop('shape')
            base_cls.__init__(self, *args, **kws)
            cls.__init__(self, shape)
        
        new_cls = type(name, (cls, base_cls), {})
        new_cls.__init__ = __init__
        return new_cls

        

        
