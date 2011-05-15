# -*- coding: utf-8 -*-

import core, actions
import math
import Box2D

class DefaultContactListener(Box2D.b2ContactListener):
    def __init__(self, level):
        super(DefaultContactListener, self).__init__()
        self.level = level
    
    def BeginContact(self, contact):
        self.level.begin_contact(contact)
    
    def EndContact(self, contact):
        self.level.end_contact(contact)
    
    def PreSolve(self, contact, old_manifold):
        self.level.pre_solve(contact, old_manifold)
    
    def PostSolve(self, contact, impulse):
        self.level.post_solve(contact, impulse)


class Box2DLevel(core.Level):
    TIMESTEP = 1.0/60.0
    VEL_ITERS = 8
    POS_ITERS = 3
    PPM = 100.0 # Pixels per meter
    
    def __init__(self, world):
        super(Box2DLevel, self).__init__()
        self.world = world
#        self.world.contactListener = DefaultContactListener(self)
        self.contacts = []
    
    def update(self, game, dt):
        world = self.world
        if dt:
            time_step = self.TIMESTEP
        else:
            # Game is paused
            time_step = 0.0
        self.contacts = []
        world.Step(time_step, self.VEL_ITERS, self.POS_ITERS)
        world.ClearForces()
        
        super(Box2DLevel, self).update(game, dt)
        
        for contact in world.contacts:
            actor_a = contact.fixtureA.body.userData
            actor_b = contact.fixtureB.body.userData
            world_manifold = contact.worldManifold
            self.on_collision(actor_a, actor_b,
                              world_manifold.points,
                              world_manifold.normal)
    
    def on_collision(self, actor_a, actor_b, points, normal):
        pass
    
    # ContactListener callbacks
    
    def begin_contact(self, contact):
        pass
    
    def end_contact(self, contact):
        pass
    
    def pre_solve(self, contact, old_manifold):
        manifold = contact.manifold
        if manifold.pointCount == 0:
            return
        
        state1, state2 = Box2D.b2GetPointStates(old_manifold, manifold)
        if not state2:
            return
        world_manifold = contact.worldManifold
        for i, point in enumerate(state2):
            self.contacts.append({'actorA': contact.fixtureA.body.userData,
                                  'actorB': contact.fixtureB.body.userData,
                                  'position': world_manifold.points[i],
                                  'normal': world_manifold.normal,
                                  'state': state2[i]})
    
    def post_solve(self, contact, impulse):
        pass


class Updater(actions.Action):
    
    def __init__(self, body):
        super(Updater, self).__init__()
        self.body = body
    
    def on_assign(self, actor):
        self.body.userData = actor
    
    def on_start(self, actor, game):
        self.update(actor, game, 0.0)
    
    def convert_coords(self, game, pos):
        PPM = game.level.PPM
        x0 = PPM*pos[0]
#        y0 = PPM*pos[1]
        y0 = game.window.height-(PPM*pos[1])
        return x0, y0
    
    def update(self, actor, game, dt):
        if actor.killed:
            if self.body.userData:
                self.body.userData = None
                self.on_remove(actor, game)
            return
        sf_obj = actor.object
        body = self.body
        sf_obj.position = self.convert_coords(game, body.position)
        sf_obj.rotation = math.degrees(body.angle)
    
    def on_remove(self, actor, game):
        game.world.DestroyBody(self.body)
