'''
Created on 28. apr. 2011

@author: klavdij
'''

from pug2d import core, utils, actions
import sf

class Level1(core.Level):
    def __init__(self):
        super(Level1, self).__init__()
        layer = core.Layer()
        view_up, view_down = utils.split_view(game.default_camera, utils.VERTICAL)
        action_h = actions.Repeat(actions.Chain([actions.Move(5.0, 500, 0),
                                                 actions.Move(5.0, -500, 0)]))
        action_v = actions.Repeat(actions.Chain([actions.Move(8.0, 0, 450),
                                                 actions.Move(8.0, 0, -450)]))
        view_up.add_action(action_h)
        view_up.add_action(action_v)
        layer.add_camera(view_up)
        layer.add_camera(view_down)
        self.add_layer(layer)
        
        self.im0 = sf.Image.load_from_file(b'princess.png')
        for y in range(0, 500, 100):
            for x in range(0, 800, 100):
                sprite = sf.Sprite(self.im0)
                sprite.position = (x, y)
                layer.add_actor(core.Actor(sprite))
    

game = core.Game(800, 600)
game.run(Level1())
