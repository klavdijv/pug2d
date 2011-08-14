# -*- coding: utf-8 -*-

from pug2d import core
from pug2d.box2d import Box2DLevel, Updater
from pug2d import box2d
from Box2D import b2
import sf


box2d.PPM = 20

class Level1(Box2DLevel):
    
    def __init__(self, world):
        super(Level1, self).__init__(world)
        layer = core.Layer()
        self.add_layer(layer)
        
        self.ground = world.CreateStaticBody(
                                             position=(0, -2),
                                             shapes=b2.polygonShape(box=(50, 5))
                                             )
        
        self.im0 = sf.Image.load_from_file(b'princess.png')
        for y in range(0, 500, 120):
            for x in range(200, 700, 120):
                sprite = sf.Sprite(self.im0)
                sprite.origin = (self.im0.width//2, self.im0.height//2)
                sprite.position = (x, y)
                actor = core.Actor(sprite)
                body = world.CreateDynamicBody()
                body.CreateCircleFixture(radius=2.5, density=1.0, friction=0.3)
                actor.add_action(Updater(body), name='box2d')
                layer.add_actor(actor)


game = core.Game(800, 600)
level = Level1(b2.world())
game.run(level)
