# -*- coding: utf-8 -*-

from pug2d import core, actions
from pug2d.box2d import Box2DLevel, Updater
from Box2D import b2
import sf
import random

class Move(actions.TimedAction):
    def __init__(self, time):
        super(Move, self).__init__(time)
        self.fv = b2.vec2(random.randrange(-15, 15), random.randrange(-15, 15))
    
    def update(self, actor, game, dt):
        if self.finished:
            new_act = actions.Chain([actions.Pause(random.randrange(15, 20)),
                                     Move(0.1*random.randrange(10, 30))
                                     ])
            actor.add_action(new_act)
        else:
            body = actor['box2d'].body
            v = body.GetLinearVelocityFromLocalPoint((0, 0))
            v.Normalize()
            body.ApplyForce(self.fv-10*v, body.position)


class Colorize(actions.TimedAction):
    def __init__(self, time, color):
        super(Colorize, self).__init__(time)
        self.color = color
    
    def on_assign(self, actor):
        actor.object.color = self.color
    
    def update(self, actor, game, dt):
        super(Colorize, self).update(actor, game, dt)
        if self.finished:
            actor.object.color = sf.Color.WHITE
        

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
        for y in range(0, 500, 120):
            for x in range(200, 700, 120):
                x0, y0 = x/self.PPM, y/self.PPM+5.0
                sprite = sf.Sprite(self.im0)
                sprite.origin = (self.im0.width//2, self.im0.height//2)
                actor = core.Actor(sprite)
                body = world.CreateDynamicBody(position=(x0, y0),
                                               angularDamping=0.1)
                body.CreateCircleFixture(radius=2.5, density=1.0, friction=0.3)
                actor.add_action(Updater(body), name='box2d')
                act2 = Move(0.1*random.randrange(5, 20))
                actor.add_action(act2)
                layer.add_actor(actor)
    
    def on_collision(self, actor_a, actor_b, points, normal):
        if actor_a:
            actor_a.add_action(Colorize(1.0, sf.Color.RED), name='mark_col')
        if actor_b:
            actor_b.add_action(Colorize(1.0, sf.Color.BLUE), name='mark_col')


game = core.Game(800, 600)
level = Level1(b2.world(gravity=(0, 0)))
game.run(level)
