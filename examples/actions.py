'''
Created on 24. apr. 2011

@author: klavdij
'''

from pug2d import core, actions
import sf

class Rotate(actions.Action):
    def __init__(self, angle):
        super(Rotate, self).__init__()
        self.angle = angle
    
    def update(self, game, dt):
        self.owner.object.rotate(dt*self.angle)


class Level1(core.Level):

    def __init__(self):
        super(Level1, self).__init__()
        layer = core.Layer()
        self.add_layer(layer)
        self.im0 = sf.Texture.load_from_file(b'princess.png')
        for x in range(50, 600, 50):
            for y in range(50, 400, 80):
                sprite = sf.Sprite(self.im0)
                sprite.position = (x, y)
                sprite.origin = (sprite.width//2, sprite.height//2)
                act = core.Actor(sprite)
                act.add_action(Rotate(30))
                layer.add_actor(act)


game = core.Game(800, 600)
level = Level1()
game.run(level)
