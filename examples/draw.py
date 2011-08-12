'''
Created on 24. apr. 2011

@author: klavdij
'''

from pug2d import core, draw
import sf

class Actor1(core.Actor):
    def __init__(self, im, x, y):
        super(Actor1, self).__init__(None)
        self.object = sf.Sprite(im)
        self.object.origin = (im.width//2, im.height//2)
        self.object.position = (x, y)
    
    def update(self, game, dt):
        self.object.rotate(30.0*dt)


class Canvas(draw.Canvas):
    def __init__(self):
        super(Canvas, self).__init__()
        self.add_circle(name='c1', x=100, y=100,
                        radius=50, color=sf.Color.GREEN, z=10)
        self.add_line(name='l1', p1x=10.0, p1y=10.0,
                      p2x=210.0, p2y=210.0, thickness=2.0)
        self.add_text(name='txt1', x=400.0, y=45.0, string='Test', size=36)
        self.t = 0.0
    
    def update(self, parent, game, dt):
        self.t += dt
        txt = 'Test'+str(int(0.1*self.t))
        self['txt1'].string = txt
        self['c1'].x += 0.1
        if 5.0 < self.t < 15.0:
            self.set_visible('l1', False)
        else:
            self.set_visible('l1', True)
        
        
class Level1(core.Level):

    def __init__(self):
        super(Level1, self).__init__()
        canvas = Canvas()
        layer = core.Layer()
        layer.add_plugin(canvas)
        self.add_layer(layer)
        self.im0 = sf.Image.load_from_file('princess.png')
        for x in range(50, 600, 50):
            for y in range(50, 400, 80):
                act = Actor1(self.im0, x, y)
                layer.add_actor(act)

game = core.Game(800, 600)
level = Level1()
game.run(level)
