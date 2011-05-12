'''
Created on 24. apr. 2011

@author: klavdij
'''
import sf

class GameClock(object):
    
    def __init__(self):
        self.clock = sf.Clock()
        self._init()
    
    def _init(self):
        self._paused = False
        self._total_time = 0.0
        self.time_factor = 1.0
    
    def reset(self):
        self.clock.reset()
        self._init()
    
    def get_paused(self):
        return self._paused
    
    def set_paused(self, value):
        if self._paused == value:
            return
        if value:
            self._total_time += self.time_factor*self.clock.elapsed_time
        self.clock.reset()
        self._paused = value
    
    paused = property(get_paused, set_paused)
    
    @property
    def total_time(self):
        if self._paused:
            return self._total_time
        return self._total_time+self.time_factor*self.clock.elapsed_time
    
    @property
    def elapsed_time(self):
        dt = 0.0 if self._paused else self.time_factor*self.clock.elapsed_time
        self.clock.reset()
        self._total_time += dt
        return dt


class Level(object):
    
    def __init__(self):
        self.layers = []
    
    def on_start(self):
        pass
    
    def on_end(self):
        pass
    
    def update(self, game, dt):
        for layer in self.layers:
            layer.update(game, dt)
    
    def draw(self, window):
        for layer in self.layers:
            layer.draw(window)
    
    def add_layer(self, layer):
        self.layers.append(layer)
    
    def remove_layer(self, layer):
        self.layers.remove(layer)
        

class Game(object):
    
    def __init__(self, width, height, bpp=32, title='Basic game',
                 framerate_limit=60, fullscreen=False):
        self.width = width
        self.height = height
        self.bpp = bpp
        self.fullscreen = fullscreen
        self.show_fps = False
        self.fps_text = sf.Text('', sf.Font.DEFAULT_FONT, 24)
        self.fps_text.position = (10, 10)
        self.fps_text.color = sf.Color.BLACK
        self.title = title
        videomode, style = self._get_videomode()
        self.window = sf.RenderWindow(videomode, title, style)
        self._level = None
        self._running = False
        self.background_color = sf.Color.WHITE
        self.framerate_limit = framerate_limit
        self.clock = GameClock()
        self.events = []

    def _get_videomode(self):
        videomode = sf.VideoMode(self.width, self.height, self.bpp)
        if self.fullscreen:
            style = sf.Style.FULLSCREEN
            if not videomode.is_valid():
                videomode = sf.VideoMode.get_desktop_mode()
        else:
            style = sf.Style.RESIZE | sf.Style.CLOSE
        return videomode, style
    
    def set_fullscreen(self, fullscreen):
        self.fullscreen = fullscreen
#        self.window.close()
        videomode, style = self._get_videomode()
        self.window.create(videomode, self.title, style)
    
    def get_level(self):
        return self._level

    def set_level(self, level):
        assert isinstance(level, Level)
        if self._level is not None:
            if hasattr(self._level, 'on_end'):
                self._level.on_end()
        self._level = level
        if hasattr(level, 'on_start'):
            level.on_start()
    
    level = property(get_level, set_level)
    
    def quit(self):
        self._running = False
    
    def run(self, level):
        self.set_level(level)
        self._running = True
        self.window.framerate_limit = self.framerate_limit
        while self._running:
            del self.events[:]
            for event in self.window.iter_events():
                if event.type == sf.Event.CLOSED:
                    self._running = False
                if event.type == sf.Event.KEY_RELEASED:
                    if event.code == sf.Key.ESCAPE:
                        self._running = False
                    if event.code == sf.Key.F and event.control:
                        self.set_fullscreen(not self.fullscreen)
                    if event.code == sf.Key.X and event.control:
                        self.show_fps = not self.show_fps
                    if event.code == sf.Key.P and event.control:
                        self.clock.paused = not self.clock.paused
                self.events.append(event)
            
            dt = self.clock.elapsed_time
            self._level.update(self, dt)
            self.window.clear(self.background_color)
            self._level.draw(self.window)
            if self.show_fps:
                self.window.view = self.window.default_view
                try:
                    fps = (1.0/self.window.frame_time)
                    self.fps_text.string = '{:7.2f}'.format(fps) 
                except ZeroDivisionError:
                    pass
                self.window.draw(self.fps_text)
            self.window.display()
        self.window.close()
    
    def get_default_camera(self):
        return Camera(self.window.default_view)
    
    default_camera = property(get_default_camera)
    
    def get_input(self):
        return self.window.get_input()
    

class Layer(object):
    
    def __init__(self):
        self.actors = []
        self.cameras = []
    
    def add_camera(self, camera):
        self.cameras.append(camera)
    
    def remove_camera(self, camera):
        self.cameras.remove(camera)
    
    def z_order(self):
        pass
    
    def update(self, game, dt):
        for camera in self.cameras:
            camera.update(game, dt)
        for actor in self.actors:
            actor.update(game, dt)
        self.actors = [actor for actor in self.actors if not actor.killed]
        self.z_order()
    
    def draw(self, window):
        views = [camera.object for camera in self.cameras] or [window.view]
        for view in views:
            window.view = view
            for actor in self.actors:
                actor.draw(window)
    
    def add_actor(self, actor):
        self.actors.append(actor)
    
    def remove_actor(self, actor):
        self.actors.remove(actor)


class OffscreenLayer(Layer):
# WARNING: doesn't work on all platforms and hardware
# (Intel graphics cards on Linux, for example)
    def __init__(self, width, height):
        super(OffscreenLayer, self).__init__()
        self.window = sf.RenderImage(width, height)
        sprite = sf.Sprite()
        sprite.position = (0, 0)
        self.container = Actor(sprite)
    
    def draw(self, window):
        offscreen = self.window
        offscreen.clear(sf.Color(0, 0, 0, 0))
        super(OffscreenLayer, self).draw(offscreen)
        offscreen.display()
        container = self.container.object
        container.image = offscreen.image
        window.draw(container, self.container.shader)


class BaseActor(object):
    def __init__(self, sf_obj):
        self.object = sf_obj
        self.killed = False
        self.actions = []
        self._actions_d = {}
    
    def __getitem__(self, name):
        return self._actions_d[name]
    
    def __setitem__(self, name, action):
        self.remove_action(name)
        self.add_action(action, name)
        
    def __delitem__(self, name):
        self.remove_action(name)
    
    def update(self, game, dt):
        pass
    
    def draw(self, window):
        pass
    
    def add_action(self, action, name=''):
        self.actions.append(action)
        if name:
            self._actions_d[name] = action
            action.name = name
        action.on_assign(self)

    def remove_action(self, action):
        if isinstance(action, basestring):
            try:
                action = self._actions_d[action]
            except KeyError:
                return
        self.actions.remove(action)
        if action.name:
            del self._actions_d[action.name]
        action.on_remove(self)
    
    def replace_action(self, old_action, new_action):
        self.actions.remove(old_action)
        self.actions.append(new_action)
    
    def kill(self):
        pass
    

class Actor(BaseActor):
    def __init__(self, sf_obj, shader=None):
        super(Actor, self).__init__(sf_obj)
        self.shader = None
    
    def update(self, game, dt):            
        for action in self.actions:
            action.pause(dt == 0)
            action.do_update(self, game, dt)
        
        self.actions = [act for act in self.actions if not act.finished]
    
    def draw(self, window):
        window.draw(self.object, self.shader)
    
    def kill(self):
        self.killed = True


class Camera(BaseActor):
    pass
