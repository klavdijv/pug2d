'''
Created on 28. jul. 2011

@author: klavdij
'''

import sf

class CanvasItem(object):
    def __init__(self, canvas, shape, z=0):
        self.canvas = canvas
        self.shape = shape
        self.visible = True
        self.z = z
    
    def __getattr__(self, name):
        if 'shape' in self.__dict__:
            return getattr(self.shape, name)
    
    def __setattr__(self, name, value):
        if hasattr(self, 'shape') and hasattr(self.shape, name):
            setattr(self.shape, name, value)
        else:
            super(CanvasItem, self).__setattr__(name, value)


class Canvas(object):
    def __init__(self):
        self.items = {}
        self._counter = 0
    
    def __getitem__(self, key):
        return self.items[key]
    
    def __delitem__(self, key):
        del self.items[key]
    
    def __contains__(self, key):
        return key in self.items
    
    def clear(self):
        self.items.clear()
   
    def add_shape(self, shape, name=None, z=0):
        self._counter += 1
        if not name:
            name = '%item_'+str(self._counter)
        item = CanvasItem(self, shape, z=z)
        self.items[name] = item
    
    def add_rectangle(self, name=None, left=0, top=0, width=100, height=100,
                      color=sf.Color.BLACK, outline=0.0, outline_color=None,
                      z=0):
        shape = sf.Shape.rectangle(left, top, width, height, color,
                                   outline, outline_color)
        self.add_shape(shape, name=name, z=z)
    
    def add_line(self, name=None, p1x=0.0, p1y=0.0, p2x=100.0, p2y=100.0,
                 thickness=1.0, color=sf.Color.BLACK, outline=0.0,
                 outline_color=None, z=0):
        shape = sf.Shape.line(p1x, p1y, p2x, p2y, thickness, color,
                              outline, outline_color)
        self.add_shape(shape, name=name, z=z)
    
    def add_circle(self, name=None, x=0.0, y=0.0, radius=100.0,
                   color=sf.Color.BLACK, outline=0.0, outline_color=None, z=0):
        shape = sf.Shape.circle(x, y, radius, color, outline, outline_color)
        self.add_shape(shape, name=name, z=z)
    
    def add_polygon(self, name=None, points=None, color=sf.Color.BLACK,
                    outline=0.0, outline_color=None, z=0):
        shape = sf.Shape()
        if points:
            for (x, y) in points:
                shape.add_point(x, y, color, outline_color)
        if outline:
            shape.outline_enabled = True
            shape.outline_thickness = outline
        else:
            shape.outline_enabled = False
        self.add_shape(shape, name=name, z=z)
    
    def add_text(self, name=None, x=0.0, y=0.0, string='',
                 font=sf.Font.DEFAULT_FONT, size=12,
                 color=sf.Color.BLACK, z=0):
        shape = sf.Text(string, font, size)
        shape.position = (x, y)
        shape.color = color
        self.add_shape(shape, name=name, z=z)
    
    def set_visible(self, key, visible=True):
        self.items[key].visible = visible
    
    def update(self, parent, game, dt):
        pass
    
    def draw(self, parent, window):
        items = list(self.items.values())
        items.sort(key=lambda obj: obj.z)
        self._sorted = True
        for item in items:
            if item.visible:
                window.draw(item.shape)
