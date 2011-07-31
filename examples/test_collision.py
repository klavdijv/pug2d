'''
Created on 24. apr. 2011

@author: klavdij
'''

from pug2d import core, draw, collision
import sf
from Box2D import b2PolygonShape

CollActor = collision.CollMixin.create_collision_class(core.Actor, 'CollActor')

class Actor1(CollActor):
    def __init__(self, im, x, y):
        im_w2 = im.width//2
        im_h2 = im.height//2
        coll_shape = b2PolygonShape(box=(im_w2, im_h2))
        super(Actor1, self).__init__(sf.Sprite(im), shape=coll_shape)
        self.object.origin = (im_w2, im_h2)
        self.object.position = (x, y)
    
    def update(self, game, dt):
        self.object.rotate(30.0*dt)
        super(Actor1, self).update(game, dt)


class Canvas(draw.Canvas):
    def __init__(self):
        super(Canvas, self).__init__()
        self.add_rectangle(name='o1', left=0, top=0, width=10, height=10,
                           color=sf.Color.WHITE, outline=3.0,
                           outline_color=sf.Color.YELLOW)
        self.add_rectangle(name='o2', left=0, top=0, width=10, height=10,
                           color=sf.Color.WHITE, outline=3.0,
                           outline_color=sf.Color.YELLOW)
        self.add_rectangle(name='p1', left=0, top=0, width=10, height=10,
                           color=sf.Color.GREEN, z=1)
        self.add_rectangle(name='p2', left=0, top=0, width=10, height=10,
                           color=sf.Color.GREEN, z=1)
        self.add_rectangle(name='n', left=0, top=0, width=10, height=10,
                           color=sf.Color.BLUE, z=2)
        self['o1'].shape.fill_enabled = self['o2'].shape.fill_enabled = False
        self.set_visible('p1', False)
        self.set_visible('p2', False)
        self.set_visible('n', False)
    
    def update(self, layer, game, dt):
        coll_group = layer.update_plugins[0]
        w_pairs = coll_group.world_pairs
        act1, act2 = layer.actors
        for (i, v) in enumerate(act1.shape.vertices):
            (x0, y0) = (act1.transform*v).tuple
            self['o1'].set_point_position(i, x0, y0)
        for (i, v) in enumerate(act2.shape.vertices):
            (x0, y0) = (act2.transform*v).tuple
            self['o2'].set_point_position(i, x0, y0)
        if w_pairs:
            (act1, act2, wm) = w_pairs[0]
            self.set_visible('p1', True)
            self.set_visible('p2', True)
            self.set_visible('n', True)
            self['p1'].position = wm.points[0]
            self['p2'].position = wm.points[1]
            (x0, y0) = wm.points[0]
            (x1, y1) = wm.points[1]
            nx0 = x0+(x1-x0)/2.0+100.0*wm.normal.x
            ny0 = y0+(y1-y0)/2.0+100.0*wm.normal.y
            self['n'].position = (nx0, ny0)
        else:
            self.set_visible('p1', False)
            self.set_visible('p2', False)
            self.set_visible('n', False)


class Level1(core.Level):
    def __init__(self):
        super(Level1, self).__init__()
        layer = core.Layer()
        coll_group = collision.CollisionGroup()
        layer.add_plugin(coll_group)
        layer.add_plugin(Canvas())
        self.add_layer(layer)
        self.im0 = sf.Image.load_from_file('princess.png')
        for x in (100, 220):
            act = Actor1(self.im0, x, 200)
            layer.add_actor(act)
            coll_group.add_actor(act)
        coll_group.add_event_handler('collision', self.on_collision)
    
    def on_collision(self, actor1, actor2, manifold):
        print 'Collision happened'


def main():
    game = core.Game(800, 600)
    level = Level1()
    game.run(level)


if __name__ == '__main__':
    main()
