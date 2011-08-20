# -*- coding: utf-8 -*-

from pug2d import core, actions, box2d
from pug2d.box2d import Box2DLevel, Updater
from Box2D import b2
import sf
import random

box2d.PPM = 20

class Move(actions.TimedAction):
    def __init__(self, time):
        super(Move, self).__init__(time)
        self.fv = b2.vec2(random.randrange(-45, 45), random.randrange(-45, 45))
    
    def update(self, game, dt):
        actor = self.owner
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
        super(Colorize, self).on_assign(actor)
        actor.object.color = self.color
    
    def update(self, game, dt):
        super(Colorize, self).update(game, dt)
        if self.finished:
            self.owner.object.color = sf.Color.WHITE


class Level1(Box2DLevel):
    def __init__(self, world):
        super(Level1, self).__init__(world)
        layer = core.Layer()
        self.add_layer(layer)
        
        self.ground = world.CreateStaticBody(
                                             position=(0, -2),
                                             shapes=b2.polygonShape(box=(50, 5))
                                             )
        
        self.im0 = sf.Texture.load_from_file(b'princess.png')
        for y in range(0, 500, 120):
            for x in range(200, 700, 120):
                sprite = sf.Sprite(self.im0)
                sprite.origin = (self.im0.width//2, self.im0.height//2)
                sprite.position = (x, y)
                actor = core.Actor(sprite)
                body = world.CreateDynamicBody(linearDamping=0.25,
                                               angularDamping=0.1)
                body.CreateCircleFixture(radius=2.5, density=1.0, friction=0.3)
                actor.add_action(Updater(body), name='box2d')
                act2 = Move(0.1*random.randrange(5, 20))
                actor.add_action(act2)
                layer.add_actor(actor)
    
    def on_collision(self, fixture_a, fixture_b, points, normal):
        actor_a = fixture_a.body.userData
        actor_b = fixture_b.body.userData
        if actor_a:
            actor_a.add_action(Colorize(1.0, sf.Color.RED), name='mark_col')
        if actor_b:
            actor_b.add_action(Colorize(1.0, sf.Color.BLUE), name='mark_col')


game = core.Game(800, 600)
level = Level1(b2.world(gravity=(0, 0)))
game.run(level)
