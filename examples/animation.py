'''
Created on 24. apr. 2011

@author: klavdij
'''

from pug2d import core, actions
import sf
import random

class SwitchAnimation(actions.TimedAction):
    def __init__(self):
        super(SwitchAnimation, self).__init__(0.0)
        self.next_check = 1.0+0.1*random.randrange(25)

    def update(self, actor, game, dt):
        if self.clock.total_time > self.next_check:
            r = random.random()
            if r < 0.2:
                actor['walk'].stop()
            elif r > 0.5:
                actor['walk'].resume()
            self.next_check = self.clock.total_time+1.0+random.random()
        

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
                act['walk'] = anim
                act.add_action(SwitchAnimation())
                layer.add_actor(act)
                num += 1


game = core.Game(800, 600)
level = Level1()
game.run(level)
