'''
Created on 24. apr. 2011

@author: klavdij
'''

from pug2d import core, actions
import sf

class Rotate(actions.TimedAction):
    def __init__(self, time, angle):
        super(Rotate, self).__init__(time)
        self.angle = angle
    
    def update(self, actor, game, dt):
        actor.object.rotate(dt*self.angle)
        super(Rotate, self).update(actor, game, dt)

class Move(actions.TimedAction):
    def __init__(self, time, dx, dy):
        super(Move, self).__init__(time)
        self.dx = dx
        self.dy = dy
    
    def update(self, actor, game, dt):
        actor.object.move(dt*self.dx, dt*self.dy)
        super(Move, self).update(actor, game, dt)
        

class Level1(core.Level):

    def __init__(self):
        super(Level1, self).__init__()
        layer = core.Layer()
        self.add_layer(layer)
        self.im0 = sf.Image.load_from_file('princess.png')
        for x in xrange(50, 600, 50):
            for y in xrange(50, 400, 80):
                sprite = sf.Sprite(self.im0)
                sprite.position = (x, y)
                sprite.origin = (sprite.width//2, sprite.height//2)
                act = core.Actor(sprite)
                action = actions.Sequence([Move(2.0, 50, 10),
                                           Rotate(12.0, 30)])
                act.add_action(action)
                layer.add_actor(act)


game = core.Game(800, 600)
level = Level1()
game.run(level)
