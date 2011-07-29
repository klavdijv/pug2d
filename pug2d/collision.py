'''
Created on 26. jul. 2011

@author: klavdij
'''

import Box2D as B2D
import math

RAYCAST_FIND_FIRST = 0
RAYCAST_FIND_ALL = 1

def _collide_poly_circle(m, actor1, actor2):
    B2D.b2CollidePolygonAndCircle(m, actor1.shape, actor1.transform,
                                  actor2.shape, actor2.transform)

def _collide_circle_poly(m, actor1, actor2):
    _collide_poly_circle(m, actor2, actor1)

def _collide_circle(m, actor1, actor2):
    B2D.b2CollideCircles(m, actor1.shape, actor1.transform,
                         actor2.shape, actor2.transform)

def _collide_poly(m, actor1, actor2):
    B2D.b2CollidePolygons(m, actor1.shape, actor1.transform,
                          actor2.shape, actor2.transform)


class Distance(object):
    def __init__(self, p1, p2, dist, iters):
        self.p1 = p1
        self.p2 = p2
        self.dist = dist
        self.iters = iters


class CollMixin(object):
    def __init__(self, shape=None):
        self._basic_shape = shape
        self.transform = B2D.b2Transform()
        self.transform.SetIdentity()
        if isinstance(shape, B2D.b2PolygonShape):
            self._poly_collide = _collide_poly
            self._circle_collide = _collide_poly_circle
        elif isinstance(shape, B2D.b2CircleShape):
            self._poly_collide = _collide_circle_poly
            self._circle_collide = _collide_circle
        else:
            msg = 'Expected b2PolygonShape or b2CircleShape, got %s'
            raise TypeError(msg % type(shape).__name__)
        self._old_scale = (1.0, 1.0)
        self.rescaled_shape = None
    
    def set_transform(self):
        t = self.transform
        sf_obj = self.object
        t.position = sf_obj.position
        t.angle = math.radians(sf_obj.rotation)
    
    def collide(self, other):
        m = B2D.b2Manifold()
        if isinstance(other._basic_shape, B2D.b2PolygonShape):
            self._poly_collide(m, self, other)
        else:
            self._circle_collide(m, self, other)
        return m
    
    def collides_with(self, other):
        m = self.collide(other)
        return bool(m.pointCount)
    
    def rescale_shape(self):
        scale = self.object.scale
        bs = self._basic_shape
        if scale != self._old_scale:
            self._old_scale = scale
            if isinstance(bs, B2D.b2PolygonShape):
                vertices = []
                c = bs.centroid
                for v in bs.vertices:
                    dv = c-B2D.b2Vec2(*v)
                    dv.x *= scale[0]
                    dv.y *= scale[1]
                    vertices.append((c+dv).tuple)
                self.rescaled_shape = B2D.b2PolygonShape(vertices=vertices)
            else:
                c_scale = max(scale[0], scale[1])
                self.rescaled_shape = B2D.b2CircleShape(pos=bs.pos,
                                                      radius=c_scale*bs.radius)
        return self.rescaled_shape
    
    def update(self, game, dt):
        super(CollMixin, self).update(game, dt)
        self.set_transform()
    
    def overlaps(self, other):
        return B2D.b2TestOverlap(self.aabb, other.aabb)
    
    def distance(self, other):
        dr = B2D.b2Distance(shapeA=self.shape,
                            shapeB=other.shape,
                            transformA=self.transform,
                            transformB=other.transform)
        return Distance(*dr)
    
    @property
    def shape(self):
        if self.object.scale != (1.0, 1.0):
            return self.rescale_shape()
        return self._basic_shape
    
    @property
    def aabb(self):
        return self.shape.getAABB(self.transform, 0)
    
    @classmethod
    def create_collision_class(cls, base_cls, name):
        def __init__(self, *args, **kws):
            shape = kws.pop('shape')
            base_cls.__init__(self, *args, **kws)
            cls.__init__(self, shape)
        
        new_cls = type(name, (cls, base_cls), {})
        new_cls.__init__ = __init__
        return new_cls


class CollisionGroup(object):
    def __init__(self, *args):
        self.actors = []
        self.pairs = []
        self._world_pairs = []
        self._recalc_world_pairs = True
    
    def add_actor(self, actor):
        self.actors.append(actor)
    
    def remove_actor(self, actor):
        self.actors.remove(actor)
    
    def update(self, level, game, dt):
        self.actors = a = [actor for actor in self.actors if not actor.killed]
        l = len(a)
        self.pairs = []
        for i in range(l-1):
            for j in range(i+1, l):
                actor1 = a[i]
                actor2 = a[j]
                m = actor1.collide(actor2)
                if m.pointCount:
                    self.pairs.append((actor1, actor2, m))
        self._recalc_world_pairs = True
    
    def raycast(self, p1, p2, mode=RAYCAST_FIND_FIRST):
        return raycast(p1, p2, self.actors, mode)
    
    @property
    def world_pairs(self):
        if self._recalc_world_pairs:
            pairs = self._world_pairs = []
            for (a1, a2, m) in self.pairs:
                wm = B2D.b2WorldManifold()
                wm.Initialize(m, a1.transform, a1.shape.radius,
                              a2.transform, a2.shape.radius)
                pairs.append((a1, a2, wm))
            self._recalc_world_pairs = False
        return self._world_pairs


def raycast(p1, p2, actors, mode=RAYCAST_FIND_FIRST):
    ri = B2D.b2RayCastInput(p1=p1, p2=p2, maxFraction=1.0)
    ro = B2D.b2RayCastOutput()
    found = []
    for actor in actors:
        if actor.shape.RayCast(ro, ri, actor.transform, 0):
            if mode == RAYCAST_FIND_FIRST:
                ri.maxFraction = ro.fraction
            found.append(actor)
    if mode == RAYCAST_FIND_FIRST:
        return found[-1] if found else None
    return found
