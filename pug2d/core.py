'''
Created on 24. apr. 2011

@author: klavdij
'''
import sf
from .events import EventNotifier
from .behaviors import DefaultBehavior

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
            self._total_time += 0.001*self.time_factor*self.clock.elapsed_time
        self.clock.reset()
        self._paused = value
    
    paused = property(get_paused, set_paused)
    
    @property
    def total_time(self):
        if self._paused:
            return self._total_time
        # clock.elapsed_time is milliseconds, convert to seconds
        dt = 0.001*self.clock.elapsed_time
        return self._total_time+dt*self.time_factor
    
    @property
    def elapsed_time(self):
        dt = 0.0 if self._paused else self.time_factor*self.clock.elapsed_time
        # Convert miliseconds to seconds
        dt *= 0.001
        self.clock.reset()
        self._total_time += dt
        return dt


class Level(EventNotifier):
    
    def __init__(self):
        super(Level, self).__init__()
        self.layers = []
        self.game = None
        self.update_plugins = []
        self.draw_plugins = []
    
    def add_plugin(self, plugin):
        if hasattr(plugin, 'update'):
            self.update_plugins.append(plugin)
        if hasattr(plugin, 'draw'):
            self.draw_plugins.append(plugin)
    
    def remove_plugin(self, plugin):
        if hasattr(plugin, 'update'):
            self.update_plugins.remove(plugin)
        if hasattr(plugin, 'draw'):
            self.draw_plugins.remove(plugin)
    
    def on_start(self):
        for layer in self.layers:
            layer.on_start()
    
    def on_end(self):
        for layer in self.layers:
            layer.on_end()
            layer.level = None
        self.layers = []
    
    def update(self, game, dt):
        for layer in self.layers:
            layer.update(game, dt)
        for plugin in self.update_plugins:
            plugin.update(self, game, dt)
    
    def draw(self, window):
        for layer in self.layers:
            layer.draw(window)
        for plugin in self.draw_plugins:
            plugin.draw(self, window)
    
    def add_layer(self, layer):
        self.layers.append(layer)
        layer.level = self
        if self.game:
            layer.initialize()
    
    def remove_layer(self, layer):
        self.layers.remove(layer)
        layer.on_end()
        layer.level = None
    

class Game(EventNotifier):
    shortcuts = {'ESC': True,
                 'PAUSE': True,
                 'FULLSCREEN': True,
                 'FPS': True}
    
    def __init__(self, width, height, bpp=32, title=b'Basic game',
                 framerate_limit=60, fullscreen=False):
        super(Game, self).__init__()
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
    
    def before_update(self):
        pass
    
    def after_update(self):
        pass
    
    def before_draw(self):
        pass
    
    def after_draw(self):
        pass
    
    def on_loop_begin(self):
        pass
    
    def on_loop_end(self):
        pass

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
        self.window.close()
        videomode, style = self._get_videomode()
        self.window.create(videomode, self.title, style)
    
    def get_level(self):
        return self._level

    def set_level(self, level):
        assert isinstance(level, Level)
        if self._level is not None:
            self._level.on_end()
            self._level.game = None
        self._level = level
        level.game = self
        level.on_start()
    
    level = property(get_level, set_level)
    
    def quit(self):
        self._running = False
    
    def run(self, level):
        shortcuts = self.shortcuts
        self.set_level(level)
        self._running = True
        self.window.framerate_limit = self.framerate_limit
        while self._running:
            self.on_loop_begin()
            del self.events[:]
            for event in self.window.iter_events():
                if event.type == sf.Event.CLOSED:
                    self._running = False
                if event.type == sf.Event.KEY_RELEASED:
                    if shortcuts['ESC'] and event.code == sf.Keyboard.ESCAPE:
                        self._running = False
                    if shortcuts['FULLSCREEN']:
                        if event.code == sf.Keyboard.F and event.control:
                            self.set_fullscreen(not self.fullscreen)
                    if shortcuts['FPS']:
                        if event.code == sf.Keyboard.X and event.control:
                            self.show_fps = not self.show_fps
                    if shortcuts['PAUSE']:
                        if event.code == sf.Keyboard.P and event.control:
                            self.clock.paused = not self.clock.paused
                self.raise_event(event.type, event)
                self.events.append(event)
            
            dt = self.clock.elapsed_time
            self.before_update()
            self._level.update(self, dt)
            self.after_update()
            self.window.clear(self.background_color)
            self.before_draw()
            self._level.draw(self.window)
            self.after_draw()
            if self.show_fps:
                self.window.view = self.window.default_view
                try:
                    fps = (1000.0/self.window.frame_time)
                    self.fps_text.string = '{:7.2f}'.format(fps) 
                except ZeroDivisionError:
                    pass
                self.window.draw(self.fps_text)
            self.window.display()
            self.on_loop_end()

        self._level.on_end()
        self._level.game = None
        self.window.close()
    
    def get_default_camera(self):
        return Camera(self.window.default_view)
    
    default_camera = property(get_default_camera)
    
    def get_input(self):
        return self.window.get_input()
    

class Layer(EventNotifier):
    
    def __init__(self):
        super(Layer, self).__init__()
        self.actors = []
        self.cameras = []
        self.update_plugins = []
        self.draw_plugins = []
        self.level = None
    
    def on_start(self):
        for camera in self.cameras:
            camera.on_start()
        for actor in self.actors:
            actor.on_start()
    
    def on_end(self):
        for camera in self.cameras:
            camera.on_end()
            camera.layer = None
        for actor in self.actors:
            actor.on_end()
            actor.layer = None
    
    def add_camera(self, camera):
        self.cameras.append(camera)
        camera.layer = self
        if self.level.game:
            camera.on_start()
    
    def remove_camera(self, camera):
        self.cameras.remove(camera)
        camera.on_end()
        camera.layer = None
    
    def add_plugin(self, plugin):
        if hasattr(plugin, 'update'):
            self.update_plugins.append(plugin)
        if hasattr(plugin, 'draw'):
            self.draw_plugins.append(plugin)
    
    def remove_plugin(self, plugin):
        if hasattr(plugin, 'update'):
            self.update_plugins.remove(plugin)
        if hasattr(plugin, 'draw'):
            self.draw_plugins.remove(plugin)
    
    def z_order(self):
        pass
    
    def update(self, game, dt):
        for camera in self.cameras:
            camera.behavior.update(game, dt)

        for actor in self.actors:
            actor.behavior.update(game, dt)
        
        actors = self.actors    
        for i in range(len(self.actors)-1, -1, -1):
            actor = actors[i]
            if actor.killed:
                actor.on_end()
                del actors[i]

        self.z_order()
        
        for plugin in self.update_plugins:
            plugin.update(self, game, dt)
    
    def draw(self, window):
        views = [camera.object for camera in self.cameras] or [window.view]
        for view in views:
            window.view = view
            for actor in self.actors:
                actor.draw(window)
            for plugin in self.draw_plugins:
                plugin.draw(self, window)
    
    def add_actor(self, actor):
        self.actors.append(actor)
        actor.layer = self
        if self.level.game:
            actor.on_start()
    
    def remove_actor(self, actor):
        self.actors.remove(actor)
        actor.on_end()
        actor.layer = None


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


class BaseActor(EventNotifier):
    def __init__(self, sf_obj, behavior=None):
        super(BaseActor, self).__init__()
        self.object = sf_obj
        self.killed = False
        self.actions = []
        self._actions_d = {}
        self.action_ids = []
        self.layer = None
        if behavior is None:
            self.behavior = DefaultBehavior()
        else:
            self.behavior = behavior
        self.behavior.actor = self

    
    def __getitem__(self, name):
        return self._actions_d[name]
    
    def __setitem__(self, name, action):
        self.remove_action(name)
        self.add_action(action, name)
        
    def __delitem__(self, name):
        self.remove_action(name)
    
    def _do_action(self, action, game, dt):
        action.pause(dt == 0)
        action.do_update(game, dt)
    
    def on_start(self):
        self.behavior.on_start()
    
    def on_end(self):
        self.behavior.on_end()
        self.behavior.actor = None

    def update(self, game, dt):
        for action in self.actions:
            self._do_action(action, game, dt)
        
        self.actions = [act for act in self.actions if not act.finished]
    
    def draw(self, window):
        pass
    
    def add_action(self, action, name=''):
        self.actions.append(action)
        if name:
            self._actions_d[name] = action
            action.name = name
        self.action_ids.append(action.id)
        action.on_assign(self)

    def remove_action(self, action):
        if isinstance(action, str):
            try:
                action = self._actions_d[action]
            except KeyError:
                return
        self.actions.remove(action)
        if action.name:
            del self._actions_d[action.name]
        self.action_ids.remove(action.id)
        action.on_remove()
    
    def remove_all_actions(self):
        for action in self.actions:
            action.on_remove()
        self.action_ids = []
        self._actions_d = {}
        self.actions = []
    
    def replace_action(self, old_action, new_action):
        self.actions.remove(old_action)
        self.actions.append(new_action)
    
    def kill(self):
        pass
    
    def has_action(self, action_id):
        return action_id in self.action_ids
    
    def move(self, x, y):
        self.behavior.move(x, y)
    
    def rotate(self, a):
        self.behavior.rotate(a)
    
    def stop(self, movement=False, rotation=False):
        self.behavior.stop(movement, rotation)
    

class Actor(BaseActor):
    def __init__(self, sf_obj, shader=None, behavior=None):
        super(Actor, self).__init__(sf_obj, behavior=behavior)
        self.shader = None
    
    def draw(self, window):
        window.draw(self.object, self.shader)
    
    def kill(self):
        self.killed = True


class Camera(BaseActor):
    pass
