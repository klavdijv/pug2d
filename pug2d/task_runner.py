'''
Created on 21. maj. 2011

@author: klavdij
'''

import types

class Task(object):
    def is_finished(self):
        return False
    
    def __call__(self):
        pass

class ActorTask(Task):
    def __init__(self, actor):
        self.actor = actor
    
    def is_finished(self):
        return self.actor.killed
    
    def __call__(self):
        self.actor.task()


class ActorsMethodTask(Task):
    def __init__(self, method, *args, **kws):
        self.method = method
        self.args = args
        self.kws = kws
        self.actor = method.__self__
        self._cached_params = []
        self._cached_results = []
        self._wrap_method()
    
    def is_finished(self):
        return self.actor.killed
    
    def _store_result(self, args, kws, result):
        params = (args, kws)
        try:
            indx = self._cached_params.index(params)
        except ValueError:
            self._cached_params.append(params)
            self._cached_results.append(result)
        else:
            self._cached_results[indx] = result
    
    def _wrap_method(self):
        def _inner(actor, *args, **kws):
            try:
                indx = _inner.wrapper._cached_params.index((args, kws))
            except ValueError:
                return _inner.wrapper.method(*args, **kws)
            return _inner.wrapper._cached_results[indx]
        
        func = self.method.__func__
        if not hasattr(func, 'wrapper'):
            name = func.__name__
            _inner.__name__ = name
            _inner.__doc__ = func.__doc__
            _inner.wrapper = self
            setattr(self.actor, name, types.MethodType(_inner, self.actor))
    
    def __call__(self):
        func = self.method.__func__
        wrapper = getattr(func, 'wrapper', self)
        result = wrapper.method(*self.args, **self.kws)
        wrapper._store_result(self.args, self.kws, result)
        return result


class TaskRunner(object):
    def __init__(self, tasks=None, tasks_per_iter=1):
        self.tasks = tasks or []
        self.tasks_per_iter = tasks_per_iter
        self.task_iter = self.run_tasks()
    
    def task_gen(self):
        finished_tasks = []
        for task in self.tasks:
            if task.is_finished():
                finished_tasks.append(task)
            else:
                yield task()
        for task in finished_tasks:
            self.tasks.remove(task)
    
    def _runner(self):
        while True:
            for task in self.task_gen():
                yield task
    
    def run_tasks(self):
        gen = self._runner()
        while True:
            num_repeats = min(self.tasks_per_iter, len(self.tasks))
            yield [next(gen) for i in range(num_repeats)]
    
    def __iter__(self):
        return self.task_iter
    
    def add_task(self, task):
        self.tasks.append(task)


class TaskManager(object):
    def __init__(self):
        self.task_runners = {}
        self.tr_iter = self.tr_gen()
    
    def __getitem__(self, name):
        return self.task_runners[name]
    
    def __setitem__(self, name, tr):
        self.task_runners[name] = tr
    
    def __delitem__(self, name):
        del self.task_runners[name]
    
    def tr_gen(self):
        while True:
            yield [next(tr.task_iter) for tr in list(self.task_runners.values())]
    
    def __iter__(self):
        return self.tr_iter
    
    def update(self):
        next(self.tr_iter)


if __name__ == '__main__':
    
    class TestActor(object):
        def __init__(self, name):
            self.name = name
            self.counter = 0
            self.killed = False
        
        def task(self):
            self.counter += 1
            print(self.name, self.counter)
        
        def calc(self, x):
            r = sum(i for i in range(x))
            print('calc called %d' % r)
            return r

    actors = [TestActor('name %d' % i) for i in range(10)]
    tasks = [ActorTask(actor) for actor in actors]
    tm = TaskManager()
    tm['tr0'] = TaskRunner(tasks, 3)
    
    for i in range(15):
        tm.update()
    
    actors[2].killed = True
    actors[5].killed = True
    del actors[2], actors[5]
    
    for i in range(15):
        tm.update()
    
    task = ActorTask(TestActor('new name'))
    tm['tr0'].add_task(task)
    for i in range(15):
        tm.update()
        print('-'*80)
    
    tm['tr1'] = TaskRunner()
    for i in range(50, 1500, 10):
        task = ActorsMethodTask(actors[0].calc, i)
        tm['tr1'].add_task(task)
    print(actors[0].calc(50))
    print('*'*80)
    for i in range(25):
        tm.update()
        print('-'*80)
    del tm['tr0']
    print('.'*80)
    for i in range(250):
        tm.update()
    for i in range(50, 1510, 10):
        print(actors[0].calc(i))
        
    actors[0].killed = True
    print('This should be the last line.')
    for i in range(20):
        tm.update()
        print('-'*80)
    
