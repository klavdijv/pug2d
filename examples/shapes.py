# -*- coding: utf-8 -*-

from pug2d import core, actors
import sf

class Level1(core.Level):
    def __init__(self):
        super(Level1, self).__init__()
        layer = core.Layer()
        self.add_layer(layer)
        
        line = actors.Shape.line(0, 0, 800, 600, 5.0, sf.Color.GREEN,
                                 outline=0.0, outline_color=sf.Color.BLACK)
        layer.add_actor(line)
        
        rect = actors.Shape.rectangle(0, 0, 300, 200, sf.Color.BLUE,
                                      outline=1.0, outline_color=sf.Color.BLACK)
        rect.object.position = (500, 450)
        layer.add_actor(rect)
        
        circle = actors.Shape.circle(50, 50, 50, sf.Color.RED,
                                     outline=0.0, outline_color=sf.Color.BLACK)
        circle.object.position = (600, 100)
        layer.add_actor(circle)

        p_list = []
        for (x, y) in [(0, 0), (50, 0), (0, 50)]:
            p_list.append(actors.ShapePoint(x, y,
                                            color=sf.Color.CYAN,
                                            outline_color=None))
        poly = actors.Shape(p_list)
        poly.object.position = (300, 250)
        layer.add_actor(poly)
        

game = core.Game(800, 600)
game.run(Level1())
