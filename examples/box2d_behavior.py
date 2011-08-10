# -*- coding: utf-8 -*-

from pug2d import core, actions, box2d
from Box2D import b2
import sf

class Level1(box2d.Box2DLevel):
    
    def __init__(self, world):
        super(Level1, self).__init__(world)
        layer = core.Layer()
        self.add_layer(layer)
        
        self.ground = world.CreateStaticBody(
                                             position=(0, -2),
                                             shapes=b2.polygonShape(box=(50, 5))
                                             )
        
        self.im0 = sf.Image.load_from_file('princess.png')
        for x in range(100, 800, 200):
            sprite = sf.Sprite(self.im0)
            sprite.origin = (self.im0.width//2, self.im0.height//2)
#            sprite.position = (x, 300)
            body = world.CreateDynamicBody()
            body.linearDamping = 10.0
            body.CreateCircleFixture(radius=2.5, density=10.0, friction=0.3)
            body.position = self.convert_coords_to_b2((x, 300))
            body.fixedRotation = True
            actor = core.Actor(sprite, behavior=box2d.Box2DBehavior(body))
            layer.add_actor(actor)
        actors = self.layers[0].actors
        act = actions.Chain([actions.Move(10.0, 400, -50),
                             actions.Rotate(3.0, 360),
                             actions.MoveTo(2.0, 100, 300),
                             actions.MoveTo(10.0, 700, 300)])
        actors[0].add_action(act)
        actors[1].add_action(actions.Move(5.0, -400, -50))
        actors[2].add_action(actions.MoveTo(15.0, 10, 180))


box2d.PPM = 20.0
box2d.HEIGHT = 600

game = core.Game(800, 600)
level = Level1(b2.world(gravity=(0, 0)))
game.run(level)
