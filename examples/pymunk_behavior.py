# -*- coding: utf-8 -*-

from pug2d import core, actions, pymunk_phy
import pymunk as pm
import sf

class Level1(pymunk_phy.PymunkLevel):
    
    def __init__(self, space):
        super(Level1, self).__init__(space)
        layer = core.Layer()
        self.add_layer(layer)
        
        self.ground = ground = pm.Body(None, None)
        ground.position = (400, 25)
        ground_shape = pm.Poly(ground, [(0, 0), (800,0), (800, 50), (0, 50)])
        space.add_static(ground_shape)
        
        self.im0 = sf.Image.load_from_file(b'princess.png')
#        inert = pm.moment_for_circle(10.0, 50.0, 50.0)
        for x in range(100, 800, 200):
            sprite = sf.Sprite(self.im0)
            sprite.origin = (self.im0.width//2, self.im0.height//2)
            body = pm.Body(50.0, pm.inf)
            shape = pm.Circle(body, 50.0)
            body.position = self.convert_coords((x, 300))
            b = pymunk_phy.PymunkBehavior(body, shape)
            actor = core.Actor(sprite, behavior=b)
            layer.add_actor(actor)
        
        actors = self.layers[0].actors
        act = actions.Chain([actions.Move(10.0, 400, -50),
                             actions.Rotate(3.0, 360),
                             actions.MoveTo(2.0, 100, 300),
                             actions.MoveTo(10.0, 700, 300)])
        actors[0].add_action(act)
        actors[1].add_action(actions.Move(5.0, -400, -50))
        actors[2].add_action(actions.MoveTo(15.0, 80, 180))
        act2 = actions.Chain([actions.Pause(5.0), actions.Kill()])
        actors[3].add_action(act2)


pymunk_phy.HEIGHT = 600

game = core.Game(800, 600)
space = pm.Space()
space.gravity = (0.0, 0.0)
space.damping = 0.9
level = Level1(space)
game.run(level)
