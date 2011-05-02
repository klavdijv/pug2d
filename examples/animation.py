'''
Created on 24. apr. 2011

@author: klavdij
'''

from pug2d import core, actions
import sf

class Level1(core.Level):

    def __init__(self):
        super(Level1, self).__init__()
        layer = core.Layer()
        self.add_layer(layer)
        self.im0 = sf.Image.load_from_file('rpg_sprite_walk.png')
        num = 0
        for x in xrange(50, 600, 50):
            for y in xrange(50, 400, 80):
                sprite = sf.Sprite(self.im0)
                sprite.position = (x, y)
                act = core.Actor(sprite)
                anim = actions.Animate(1.0, 4, 8,
                                       start=(num % 4, 0),
                                       stop=(num % 4, 7),
                                       repeats=0)
                act.add_action(anim)
                layer.add_actor(act)
                num += 1


game = core.Game(800, 600)
level = Level1()
game.run(level)
