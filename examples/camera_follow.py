'''
Created on 5. maj. 2011

@author: klavdij
'''

import sf
from pug2d import core, actions

def rotate(vect, angle):
    m = sf.Matrix3.transformation((0, 0), (0, 0), angle, (1, 1))
    return m.transform(vect)

class Mover(actions.Action):
    def __init__(self, speed):
        super(Mover, self).__init__()
        self.speed = speed
        
    def update(self, game, dt):
        actor = self.owner
        sprite = actor.object
        if sf.Keyboard.is_key_pressed(sf.Keyboard.LEFT):
            sprite.rotate(-90.0*dt)
        elif sf.Keyboard.is_key_pressed(sf.Keyboard.RIGHT):
            sprite.rotate(90.0*dt)
        if sf.Keyboard.is_key_pressed(sf.Keyboard.UP):
            dx, dy = rotate(dt*self.speed, actor.object.rotation)
        elif sf.Keyboard.is_key_pressed(sf.Keyboard.DOWN):
            dx, dy = rotate(-dt*self.speed, actor.object.rotation)
        else:
            dx, dy = (0.0, 0.0)
        sprite.x += dx
        sprite.y += dy


class Level1(core.Level):
    def __init__(self):
        super(Level1, self).__init__()
        layer = core.Layer()
        self.add_layer(layer)
        
        self.im0 = sf.Image.load_from_file(b'princess.png')
        for y in range(0, 501, 100):
            for x in range(0, 701, 100):
                s0 = sf.Sprite(self.im0)
                s0.position = (x, y)
                layer.add_actor(core.Actor(s0))
        
        sprite = sf.Sprite(self.im0)
        sprite.position = 400, 300
        sprite.origin = self.im0.width//2, self.im0.height//2
        actor = core.Actor(sprite)
        actor.add_action(Mover(sf.Vector2f(0, -200)))
        layer.add_actor(actor)
        camera = game.default_camera
        camera.add_action(actions.CameraFollow(actor, True))
        layer.add_camera(camera)


game = core.Game(800, 600)
game.run(Level1())
