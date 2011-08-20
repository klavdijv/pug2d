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
        layer = core.OffscreenLayer(800, 600)
        layer.container.object.position = (100, 100)
        
        shader = sf.Shader.load_from_file(b'edge.sfx')
        shader.set_texture(b'texture', layer.window.texture)
        layer.container.shader = shader

        self.add_layer(layer)
        self.im0 = sf.Texture.load_from_file(b'princess.png')
        for x in range(50, 600, 50):
            for y in range(50, 400, 80):
                act = Actor1(self.im0, x, y)
                layer.add_actor(act)


game = core.Game(800, 600)
level = Level1()
game.run(level)
