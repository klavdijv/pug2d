import sf
import bisect
from .core import GameClock

class Action(object):
    
    def __init__(self):
        self.finished = False
        
    def finish(self):
        self.finished = True

    def update(self, actor, game, dt):
        pass
    
    def reset(self):
        self.finished = False
    
    def pause(self, value):
        pass


class TimedAction(Action):

    def __init__(self, time):
        super(TimedAction, self).__init__()
        self.time = time
        self.clock = GameClock()
    
    def update(self, actor, game, dt):
        if self.finished:
            return
        super(TimedAction, self).update(actor, game, dt)
        if self.clock.total_time > self.time:
            self.finished = True
    
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
    
    def update(self, actor, game, dt):
        if self.finished:
            return
        super(Sequence, self).update(actor, game, dt)
        for action in self.actions:
            action.update(actor, game, dt)
        self.actions = [act for act in self.actions if not act.finished]
        if not self.actions:
            self.finished = True
    
    def reset(self):
        super(Sequence, self).reset()
        self.actions = self.actions_back[:]
        for action in self.actions:
            action.reset()
    
    def pause(self, value):
        super(Sequence, self).pause(value)
        for action in self.actions:
            action.pause(value)


class Chain(Action):
    
    def __init__(self, actions):
        super(Chain, self).__init__()
        self.actions = actions[:]
        self.actions_back = actions[:]
    
    def update(self, actor, game, dt):
        if self.finished:
            return
        super(Chain, self).update(actor, game, dt)
        action = self.actions[0]
        action.update(actor, game, dt)
        if action.finished:
            self.actions.pop(0)
            if self.actions:
                action = self.actions[0]
                action.reset()
            else:
                self.finished = True
    
    def reset(self):
        super(Chain, self).reset()
        self.actions = self.actions_back[:]
        for action in self.actions:
            action.reset()

    def pause(self, value):
        super(Chain, self).pause(value)
        for action in self.actions:
            action.pause(value)


class Repeat(Action):
    
    def __init__(self, action, num=0):
        super(Repeat, self).__init__()
        self.action = action
        self.num = num
        self.count = 0
    
    def update(self, actor, game, dt):
        if self.finished:
            return
        super(Repeat, self).update(actor, game, dt)
        self.action.update(actor, game, dt)
        if self.action.finished:
            self.count += 1
            if self.num == 0 or self.num > self.count:
                self.action.reset()
            else:
                self.finished = True
    
    def reset(self):
        super(Repeat, self).reset()
        self.count = 0
        self.action.reset()
    
    def pause(self, value):
        super(Repeat, self).pause(value)
        self.action.pause(value)


# Implementations

Pause = TimedAction


class Kill(Action):
    
    def update(self, actor, game, dt):
        actor.kill()
        self.finished = True


class DefferedCall(TimedAction):
    
    def __init__(self, time, func, *args, **kws):
        super(DefferedCall, self).__init__(time)
        self.func = func
        self.args = args
        self.kws = kws
    
    def update(self, actor, game, dt):
        super(DefferedCall, self).update(actor, game, dt)
        if self.finished:
            self.func(actor, *self.args, **self.kws)


class Move(TimedAction):
    
    def __init__(self, time, dx, dy):
        super(Move, self).__init__(time)
        self.dx = dx/time
        self.dy = dy/time
    
    def update(self, actor, game, dt):
        actor.object.move(dt*self.dx, dt*self.dy)
        super(Move, self).update(actor, game, dt)


class MoveTo(TimedAction):
    
    def __init__(self, time, x, y):
        super(MoveTo, self).__init__(time)
        self.dx = x
        self.dy = y
        self.started = False
    
    def update(self, actor, game, dt):
        if not self.started:
            self.dx = (self.dx - actor.object.x)/self.time
            self.dy = (self.dy - actor.object.y)/self.time
            self.started = True
        actor.object.move(dt*self.dx, dt*self.dy)
        super(MoveTo, self).update(actor, game, dt)


class Rotate(TimedAction):
    
    def __init__(self, time, alpha):
        super(Rotate, self).__init__(time)
        self.alpha = alpha/time
    
    def update(self, actor, game, dt):
        actor.object.rotate(dt*self.alpha)
        super(Rotate, self).update(actor, game, dt)

class RotateTo(TimedAction):
    
    def __init__(self, time, alpha):
        super(RotateTo, self).__init__(time)
        self.alpha = alpha
        self.started = False
    
    def update(self, actor, game, dt):
        if not self.started:
            self.alpha = (self.alpha-actor.object.rotation)/self.time
            self.started = True
        actor.object.rotate(dt*self.alpha)
        super(RotateTo, self).update(actor, game, dt)


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
    
    def update(self, actor, game, dt):
        sprite = actor.object
        if self.frame_width is None:
            self.frame_width = sprite.image.width//self.num_cols
            self.frame_height = sprite.image.height//self.num_rows
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