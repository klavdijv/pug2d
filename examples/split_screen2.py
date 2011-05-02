'''
Created on 28. apr. 2011

@author: klavdij
'''

from pug2d import core, utils
import sf

class Level1(core.Level):
    def __init__(self):
        super(Level1, self).__init__()
        layer = core.Layer()
        view_up, view_down = utils.split_view(game.default_camera,
                                              utils.VERTICAL)
        view_up_l, view_up_r = utils.split_view(view_up, utils.HORIZONTAL)
        layer.add_camera(view_up_l)
        layer.add_camera(view_down)
        self.add_layer(layer)
        self.speed_x = 100.0
        self.speed_y = 50.0
        
        self.im0 = sf.Image.load_from_file('princess.png')
        for y in range(0, 500, 100):
            for x in range(0, 800, 100):
                sprite = sf.Sprite(self.im0)
                sprite.position = (x, y)
                layer.add_actor(core.Actor(sprite))
    
        layer2 = core.Layer()
        view_up_rt, view_up_rb = utils.split_view(view_up_r,
                                                  utils.VERTICAL,
                                                  ratio=0.8)
        layer2.add_camera(view_up_rt)
        layer2.add_camera(view_up_rb)
        text = sf.Text('PySFML', sf.Font.DEFAULT_FONT, 32)
        text.color = sf.Color.BLACK
        layer2.add_actor(core.Actor(text))
        self.add_layer(layer2)
        
    def update(self, dt):
        view = self.layers[0].cameras[0].object
        x, y = view.center
        
        if x < 0 or x > 800:
            self.speed_x *= -1.0
        if y < 0 or y > 500:
            self.speed_y *= -1.0
            
        x += self.speed_x*dt
        y += self.speed_y*dt
        view.center = (x, y)
#        view.rotate(15*dt)
        super(Level1, self).update(dt)
                

game = core.Game(800, 600)
game.run(Level1())
