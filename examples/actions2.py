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
        self.im0 = sf.Texture.load_from_file(b'princess.png')
        for x in range(50, 600, 50):
            for y in range(50, 400, 80):
                sprite = sf.Sprite(self.im0)
                sprite.position = (x, y)
                sprite.origin = (sprite.width//2, sprite.height//2)
                act = core.Actor(sprite)
                act_list = [actions.Move(3.0, 150, 25),
                            actions.Pause(2.5),
                            actions.Rotate(4.0, 360),
                            actions.Pause(1.5)]
                act_list2 = [actions.Repeat(actions.Chain(act_list),
                                        num=3),
                             actions.MoveTo(10.0, sprite.x, sprite.y)]
                action = actions.Repeat(actions.Chain(act_list2))
                act.add_action(action)
                layer.add_actor(act)


game = core.Game(800, 600, title=b'Actions')
level = Level1()
game.run(level)
