'''
Created on 24. apr. 2011

@author: klavdij
'''

from pug2d import core
import sf

class Actor1(core.Actor):
    def __init__(self, im, x, y):
        super(Actor1, self).__init__(None)
        self.object = sf.Sprite(im)
        self.object.origin = (im.width//2, im.height//2)
        self.object.position = (x, y)
    
    def update(self, game, dt):
        self.object.rotate(30.0*dt)
        

class Level1(core.Level):

    def __init__(self):
        super(Level1, self).__init__()
        layer = core.Layer()
        self.add_layer(layer)
        self.im0 = sf.Texture.load_from_file(b'princess.png')
        for x in range(50, 600, 50):
            for y in range(50, 400, 80):
                act = Actor1(self.im0, x, y)
                layer.add_actor(act)
        game.add_event_handler(sf.Event.KEY_RELEASED, self.handle_key_up)
    
    def handle_key_up(self, event):
        if event.code == sf.Keyboard.UP:
            game.remove_event_handler(sf.Event.KEY_RELEASED,
                                      self.handle_key_up)
            game.set_level(Level2())


class Level2(core.Level):
    def __init__(self):
        super(Level2, self).__init__()
        layer = core.Layer()
        self.add_layer(layer)
        text = sf.Text('PySFML', sf.Font.DEFAULT_FONT, 32)
        text.color = sf.Color.BLACK
        layer.add_actor(core.Actor(text))
        game.add_event_handler(sf.Event.KEY_RELEASED, self.handle_key_up)
        
    def handle_key_up(self, event):
        if event.code == sf.Keyboard.Q:
            game.quit()


game = core.Game(800, 600)
level = Level1()
game.run(level)
