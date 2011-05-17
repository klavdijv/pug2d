# -*- coding: utf-8 -*-

import core, actions
import math
import Box2D

class ContactListener(Box2D.b2ContactListener):
    def __init__(self, level):
        super(ContactListener, self).__init__()
        self.level = level
    
    def PreSolve(self, contact, old_manifold):
        self.level.pre_solve(contact, old_manifold)
    
    def PostSolve(self, contact, impulse):
        self.level.post_solve(contact, impulse)
    
    def BeginContact(self, contact):
        self.level.begin_contact(contact)
    
    def EndContact(self, contact):
        self.level.end_contact(contact)

class Box2DLevel(core.Level):
    TIMESTEP = 1.0/60.0
    VEL_ITERS = 8
    POS_ITERS = 3
    PPM = 100.0 # Pixels per meter
    
    def __init__(self, world, use_listener=False):
        super(Box2DLevel, self).__init__()
        self.world = world
        self.use_listener = use_listener
        if use_listener:
            world.contactListener = ContactListener()
        self.contacts = []
    
    def update(self, game, dt):
        world = self.world
        self.contacts = []
        if dt:
            time_step = self.TIMESTEP
        else:
            # Game is paused
            time_step = 0.0
        world.Step(time_step, self.VEL_ITERS, self.POS_ITERS)
        world.ClearForces()
        
        super(Box2DLevel, self).update(game, dt)
        
        for contact in self.contacts if self.use_listener else world.contacts:
            world_manifold = contact.worldManifold
            self.on_collision(contact.fixtureA,
                              contact.fixtureB,
                              world_manifold.points,
                              world_manifold.normal)
    
    def on_collision(self, fixture_a, fixture_b, points, normal):
        pass
    
    # Contact callbacks (active if self.use_listener == True)
    
    def pre_solve(self, contact, old_manifold):
        pass
    
    def post_solve(self, contact, impulse):
        pass
    
    def begin_contact(self, contact):
        pass
    
    def end_contact(self, contact):
        pass


class Updater(actions.Action):
    
    def __init__(self, body):
        super(Updater, self).__init__()
        self.body = body
    
    def on_assign(self, actor):
        self.body.userData = actor
    
    def on_start(self, actor, game):
        body = self.body
        sf_obj = actor.object
        body.position = self.convert_coords_to_b2(game, sf_obj.position)
        body.angle = math.radians(sf_obj.rotation)
    
    def convert_coords_to_sf(self, game, pos):
        PPM = game.level.PPM
        x0 = PPM*pos[0]
        y0 = game.window.height-(PPM*pos[1])
        return x0, y0
    
    def convert_coords_to_b2(self, game, pos):
        PPM = game.level.PPM
        x0 = pos[0]/PPM
        y0 = (game.window.height-pos[1])/PPM
        return x0, y0
    
    def update(self, actor, game, dt):
        if actor.killed:
            if self.body.userData:
                self.body.userData = None
                self.on_remove(actor, game)
            return
        
        sf_obj = actor.object
        body = self.body
        sf_obj.position = self.convert_coords_to_sf(game, body.position)
        sf_obj.rotation = math.degrees(body.angle)
    
    def on_remove(self, actor, game):
        game.world.DestroyBody(self.body)
