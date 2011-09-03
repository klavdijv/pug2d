import sf
import bisect
from .core import GameClock
from .events import EventNotifier
from .support import InputEvent, InputHandler

class Action(EventNotifier):
    _id_ = ''
    
    def __init__(self):
        super(Action, self).__init__()
        self.started  = False
        self.finished = False
        self.name = ''
        self.owner = None
    
    def on_assign(self, actor):
        self.owner = actor
    
    def on_start(self, game):
        pass
    
    def on_end(self, game):
        pass
    
    def on_remove(self):
        self.finished = True
    
    def finish(self):
        self.finished = True
        self.raise_event('finished')

    def update(self, game, dt):
        pass
    
    def do_update(self, game, dt):
        if not self.started:
            self.on_start(game)
            self.started = True
        self.update(game, dt)
        if self.finished:
            self.on_end(game)
    
    def reset(self):
        self.finished = False
    
    def pause(self, value):
        pass
    
    @property
    def id(self):
        return self.__class__.__name__ or self._id_


class TimedAction(Action):

    def __init__(self, time):
        super(TimedAction, self).__init__()
        self.time = time
        self.clock = GameClock()
    
    def update(self, game, dt):
        if self.finished:
            return
        super(TimedAction, self).update(game, dt)
        if self.time > 0.0 and self.clock.total_time > self.time:
            self.finish()
    
    def reset(self):
        super(TimedAction, self).reset()
        self.clock.reset()
    
    def pause(self, value):
        super(TimedAction, self).pause(value)
        self.clock.paused = value


class Sequence(Action):
    
    def __init__(self, actions):
        super(Sequence, self).__init__()
        self.actions = actions[:]
        self.actions_back = actions[:]
    
    def update(self, game, dt):
        actor = self.owner
        if self.finished:
            return
        super(Sequence, self).update(game, dt)
        for action in self.actions:
            action.do_update(game, dt)
        self.actions = [act for act in self.actions if not act.finished]
        if not self.actions:
            self.finish()
    
    def reset(self):
        super(Sequence, self).reset()
        self.actions = self.actions_back[:]
        for action in self.actions:
            action.reset()
    
    def pause(self, value):
        super(Sequence, self).pause(value)
        for action in self.actions:
            action.pause(value)
    
    def on_assign(self, actor):
        super(Sequence, self).on_assign(actor)
        for action in self.actions:
            action.on_assign(actor)
    

class Chain(Action):
    
    def __init__(self, actions):
        super(Chain, self).__init__()
        self.actions = actions[:]
        self.actions_back = actions[:]
    
    def update(self, game, dt):
        actor = self.owner
        if self.finished:
            return
        super(Chain, self).update(game, dt)
        action = self.actions[0]
        action.do_update(game, dt)
        if action.finished:
            self.actions.pop(0)
            if self.actions:
                action = self.actions[0]
                action.reset()
            else:
                self.finish()
    
    def reset(self):
        super(Chain, self).reset()
        self.actions = self.actions_back[:]
        for action in self.actions:
            action.reset()

    def pause(self, value):
        super(Chain, self).pause(value)
        for action in self.actions:
            action.pause(value)

    def on_assign(self, actor):
        super(Chain, self).on_assign(actor)
        for action in self.actions:
            action.on_assign(actor)
    

class Repeat(Action):
    
    def __init__(self, action, num=0):
        super(Repeat, self).__init__()
        self.action = action
        self.num = num
        self.count = 0
    
    def update(self, game, dt):
        if self.finished:
            return
        super(Repeat, self).update(game, dt)
        self.action.do_update(game, dt)
        if self.action.finished:
            self.count += 1
            if self.num == 0 or self.num > self.count:
                self.action.reset()
            else:
                self.finish()
    
    def reset(self):
        super(Repeat, self).reset()
        self.count = 0
        self.action.reset()
    
    def pause(self, value):
        super(Repeat, self).pause(value)
        self.action.pause(value)
    
    def on_assign(self, actor):
        super(Repeat, self).on_assign(actor)
        self.action.on_assign(actor)


# Implementations

Pause = TimedAction


class Kill(Action):
    
    def update(self, game, dt):
        self.owner.kill()
        self.finish()


class Call(Action):
    def __init__(self, func, *args, **kws):
        super(Call, self).__init__()
        self.func = func
        self.args = args
        self.kws = kws
    
    def update(self, game, dt):
        actor = self.owner
        super(Call, self).update(game, dt)
        self.func(actor, *self.args, **self.kws)
        self.finish()
        

class DefferedCall(TimedAction):
    
    def __init__(self, time, func, *args, **kws):
        super(DefferedCall, self).__init__(time)
        self.func = func
        self.args = args
        self.kws = kws
    
    def update(self, game, dt):
        actor = self.owner
        super(DefferedCall, self).update(game, dt)
        if self.finished:
            self.func(actor, *self.args, **self.kws)


class Move(TimedAction):
    
    def __init__(self, time, dx, dy):
        super(Move, self).__init__(time)
        self.dx = dx/time
        self.dy = dy/time
    
    def update(self, game, dt):
        self.owner.move(dt*self.dx, dt*self.dy)
        super(Move, self).update(game, dt)
    
    def finish(self):
        super(Move, self).finish()
        self.owner.stop(movement=True)
        

class MoveTo(TimedAction):
    
    def __init__(self, time, x, y):
        super(MoveTo, self).__init__(time)
        self.dx = x
        self.dy = y
    
    def on_start(self, game):
        actor = self.owner
        self.dx = (self.dx - actor.object.x)/self.time
        self.dy = (self.dy - actor.object.y)/self.time
    
    def update(self, game, dt):
        actor = self.owner
        actor.move(dt*self.dx, dt*self.dy)
        super(MoveTo, self).update(game, dt)

    def finish(self):
        super(MoveTo, self).finish()
        self.owner.stop(movement=True)
        

class Rotate(TimedAction):
    
    def __init__(self, time, alpha):
        super(Rotate, self).__init__(time)
        self.alpha = alpha/time
    
    def update(self, game, dt):
        actor = self.owner
        actor.rotate(dt*self.alpha)
        super(Rotate, self).update(game, dt)

    def finish(self):
        super(Rotate, self).finish()
        self.owner.stop(rotation=True)
        

class RotateTo(TimedAction):
    
    def __init__(self, time, alpha):
        super(RotateTo, self).__init__(time)
        self.alpha = alpha
    
    def on_start(self, game):
        actor = self.owner
        self.alpha = (self.alpha-actor.object.rotation)/self.time
    
    def update(self, game, dt):
        actor = self.owner
        actor.rotate(dt*self.alpha)
        super(RotateTo, self).update(game, dt)

    def finish(self):
        super(RotateTo, self).finish()
        self.owner.stop(rotation=True)
        

class Animate(TimedAction):
    
    def _pack_frame(self, frame):
        return self.num_cols*frame[0]+frame[1]
    
    def _unpack_frame(self, frame_num):
        return divmod(frame_num, self.num_cols)
    
    def __init__(self, time, num_rows, num_cols,
                 start=None, stop=None, repeats=1):
        if start is None:
            start = (0, 0)
        if stop is None:
            stop = (num_rows-1, num_cols-1)
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.start = self._pack_frame(start)
        self.repeats = repeats
        self.count = 0
        self.num_frames = self._pack_frame(stop)-self._pack_frame(start)
        self.frame_width = self.frame_height = None
        if isinstance(time, (tuple, list)):
            frame_times = time[:]
            time = sum(time)
        else:
            frame_times = [(1.0*time)/self.num_frames]*self.num_frames
        c_time = 0.0
        self.frame_times = [0.0]
        for ft in frame_times:
            c_time += ft
            self.frame_times.append(c_time)
        super(Animate, self).__init__(time)
        self.old_time_factor = self.clock.time_factor
    
    def on_assign(self, actor):
        super(Animate, self).on_assign(actor)
        tex = actor.object.texture
        self.frame_width = tex.width//self.num_cols
        self.frame_height = tex.height//self.num_rows
    
    def update(self, game, dt):
        sprite = self.owner.object
        time0 = self.clock.total_time
        if time0 > self.time:
            self.count += 1
            if self.repeats !=0 and self.repeats > self.count:
                self.finished = True
                return
            else:
                time0 = time0 % self.time
        frame_indx = bisect.bisect(self.frame_times, time0)-1
        row, col = self._unpack_frame(self.start+frame_indx)
        sprite.sub_rect = sf.IntRect(col*self.frame_width,
                                     row*self.frame_height,
                                     self.frame_width, self.frame_height)

    def stop(self):
        self.old_time_factor = self.clock.time_factor
        self.clock.time_factor = 0.0
    
    def resume(self):
        self.clock.time_factor = self.old_time_factor


class EightDirMovement(Action):
    def __init__(self, vx=100, vy=100):
        super(EightDirMovement, self).__init__()
        self.vx = vx
        self.vy = vy
        self.dx = self.dy = 0
        self.dt = 0.0
        self.input_handler = handler = InputHandler()
        handler['left'] = InputEvent('single', ('key', sf.Keyboard.LEFT))
        handler['right'] = InputEvent('single', ('key', sf.Keyboard.RIGHT))
        handler['up'] = InputEvent('single', ('key', sf.Keyboard.UP))
        handler['down'] = InputEvent('single', ('key', sf.Keyboard.DOWN))
    
    def update(self, game, dt):
        behavior = self.owner.behavior
        self.dt = dt
        self.dx = self.dy = 0
        ev_names = self.input_handler()
        for ev_name in ev_names:
            if ev_name == 'left':
                self.dx += -self.dt*self.vx
            elif ev_name == 'right':
                self.dx += self.dt*self.vx
            elif ev_name == 'up':
                self.dy += -self.dt*self.vy
            elif ev_name == 'down':
                self.dy += self.dt*self.vy
        behavior.move(self.dx, self.dy)


# Camera actions

class CameraFollow(Action):
    
    def __init__(self, target, follow_rotation):
        super(CameraFollow, self).__init__()
        self.target = target
        self.follow_rotation = follow_rotation
    
    def update(self, game, dt):
        camera = self.owner.object
        sprite = self.target.object
        camera.center = sprite.position
        if self.follow_rotation:
            camera.rotation = sprite.rotation
