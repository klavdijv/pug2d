# -*- coding: utf-8 -*-

from pug2d import core, actions
from pug2d.box2d import Box2DLevel, Updater, can_see
from Box2D import b2
import sf


class Level1(Box2DLevel):
    PPM = 20
    
    def __init__(self, world):
        super(Level1, self).__init__(world)
        layer = core.Layer()
        self.add_layer(layer)
        
        self.ground = world.CreateStaticBody(
                                             position=(0, -2),
                                             shapes=b2.polygonShape(box=(50, 5))
                                             )
        
        self.im0 = sf.Image.load_from_file('princess.png')
        for x in range(100, 800, 300):
            sprite = sf.Sprite(self.im0)
            sprite.origin = (self.im0.width//2, self.im0.height//2)
            sprite.position = (x, 300)
            actor = core.Actor(sprite)
            body = world.CreateDynamicBody()
            body.CreateCircleFixture(radius=2.5, density=1.0, friction=0.3)
            actor.add_action(Updater(body), name='box2d')
            layer.add_actor(actor)
        actors = self.layers[0].actors
        actors[1].obstacle = True
        actors[0].add_action(actions.DefferedCall(1.0, self.test_los))
    
    def test_los(self, actor):
        max_dist = 800.0/self.PPM
        actor2 = self.layers[0].actors[2]
        print can_see(actor, actor2, max_dist, 45.0)
        self.layers[0].actors[1].obstacle = False
        print can_see(actor, actor2, max_dist, 45.0)


game = core.Game(800, 600)
level = Level1(b2.world(gravity=(0, 0)))
game.run(level)
