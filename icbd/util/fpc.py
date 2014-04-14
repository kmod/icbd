import _ast
import collections
import heapq
import functools
import random
import traceback

import ast_utils
from cfa import cfa

class FifoQueue(object):
    """
    fifo queue; good guaranteed runtime for analyses with monotonic state
    """
    def __init__(self):
        self._in_queue = set()
        self.queue = collections.deque()

    def add(self, e):
        if not e in self._in_queue:
            self.queue.append(e)
            self._in_queue.add(e)

    def get_next(self):
        if not self.queue:
            return None
        r = self.queue.popleft()
        self._in_queue.remove(r)
        return r

class RandomizedQueue(object):
    """
    random queue (picks a random element each time).  probably the most likely to work, but not necessarily very efficiently
    """
    def __init__(self):
        self.queue = []
        self._r = random.Random(127)

    def add(self, e):
        self._in_queue = set()
        if not e in self._in_queue:
            self.queue.append(e)
            self._in_queue.add(e)

    def get_next(self):
        if not self.queue:
            return None
        x = self._r.choice(self.queue)
        self.queue.remove(x)
        return x

class MinQueue(object):
    """
    priority queue (picks the smallest element each time).  More likely to converge than the FIFO queue, but has worst-case exponential efficiency
    especially good for function-local analyses, since nodes are nearly topologically sorted.
    """
    def __init__(self):
        self._in_queue = set()
        self.queue = []

    def add(self, e):
        if not e in self._in_queue:
            heapq.heappush(self.queue, e)
            self._in_queue.add(e)

    def get_next(self):
        if not self.queue:
            return None
        r = heapq.heappop(self.queue)
        self._in_queue.remove(r)
        return r


class Scope(object):
    def __init__(self):
        self.__listeners = {} # name -> set of listeners on that name

    def add_listener(self, name, l):
        assert isinstance(name, str)
        assert callable(l)
        self.__listeners.setdefault(name, set()).add(l)

    def fire_listeners(self, name):
        for l in self.__listeners.get(name, []):
            l()

class ModuleScope(Scope):
    def __init__(self):
        super(ModuleScope, self).__init__()
        self.names = {}

    def get_name(self, name, listener, global_=False, skip=False):
        if skip:
            return None

        self.add_listener(name, listener)
        return self.names.get(name)

    def set_name(self, name, value, global_=False):
        changed = (value != self.names.get(name))
        self.names[name] = value
        if changed:
            self.fire_listeners(name)

class ClassScope(Scope):
    def __init__(self, parent):
        super(ClassScope, self).__init__()
        self.parent = parent
        self.names = {}
        self.global_names = set()

    def get_name(self, name, listener, global_=False, skip=False):
        is_global = global_ or (name in self.global_names)
        if skip or is_global:
            return self.parent.get_name(name, listener, is_global, False)

        self.add_listener(name, listener)
        if name in self.names:
            return self.names[name]

        return self.parent.get_name(name, listener, False, False)

    def set_name(self, name, value, global_=False):
        if global_ or name in self.global_names:
            self.parent.set_name(name, value, global_)
        else:
            changed = (value != self.names.get(name))
            self.names[name] = value
            if changed:
                self.fire_listeners(name)

    def _set_global(self, n):
        assert n not in self.names
        assert n not in self._Scope__listeners
        self.global_names.add(n)

class FunctionScope(Scope):
    def __init__(self, parent):
        super(FunctionScope, self).__init__()
        while isinstance(parent, ClassScope):
            parent = parent.parent

        self.parent = parent
        assert parent is not None
        self.names = {}
        self.global_names = set()

    def get_name(self, name, listener, global_=False, skip=False):
        is_global = global_ or (name in self.global_names)
        if skip or is_global:
            return self.parent.get_name(name, listener, is_global, False)

        self.add_listener(name, listener)
        if name in self.names:
            return self.names[name]

        return self.parent.get_name(name, listener, False, False)

    def set_name(self, name, value, global_=False):
        if global_ or name in self.global_names:
            self.parent.set_name(name, value, global_)
        else:
            changed = (value != self.names.get(name))
            self.names[name] = value
            if changed:
                self.fire_listeners(name)

    def _set_global(self, n):
        assert n not in self.names
        assert n not in self._Scope__listeners
        self.global_names.add(n)

class FixedPointComputator(object):
    def __init__(self, backwards=False, queue=None, fn=None):
        self.backwards = backwards

        self.cfgs = {}
        self.scopes = {} # node -> scope
        self.errors = {} # (node, block_id) -> ((row, start) -> message)
        self.input_states = {} # (node, block_id) -> state
        self.output_states = {} # (node, block_id) -> state
        self.cur_key = None
        self.listeners = {} # (node, block_id) -> listener to mark that as changed
        self.fn = fn

        if queue is None:
            queue = FifoQueue()
        self._queue = queue

    def my_listener(self):
        k = self.cur_key
        if k not in self.listeners:
            self.listeners[k] = functools.partial(self.mark_changed, k)
        return self.listeners[k]

    def do_error(self, lineno, col_offset, error):
        assert self.cur_key is not None
        assert isinstance(lineno, int)
        assert isinstance(col_offset, int)
        assert isinstance(error, str)
        err_key = (lineno, col_offset)
        self.errors[self.cur_key][err_key] = error

    def mark_changed(self, k):
        self._queue.add(k)

    def first_block(self, cfg):
        if self.backwards:
            return cfg.end
        else:
            return cfg.start

    def last_block(self, cfg):
        if self.backwards:
            return cfg.start
        else:
            return cfg.end

    def queue_scope(self, node, state, parent_scope):
        assert (node in self.cfgs) == (node in self.scopes)

        if node in self.cfgs:
            assert state == self.input_states[(node, self.first_block(self.cfgs[node]))]
        else:
            if isinstance(node, _ast.FunctionDef):
                if ast_utils.has_yields(node):
                    body = node.body
                else:
                    body = node.body + [_ast.Return(_ast.Name("None", _ast.Load(), not_real=True), not_real=True)]
                self.scopes[node] = FunctionScope(parent_scope)
            elif isinstance(node, _ast.Lambda):
                body = [_ast.Return(node.body, lineno=node.lineno, col_offset=node.col_offset, not_real=True)]
                self.scopes[node] = FunctionScope(parent_scope)
            elif isinstance(node, _ast.Module):
                body = node.body
                assert parent_scope is None
                self.scopes[node] = ModuleScope()
            elif isinstance(node, _ast.ClassDef):
                body = node.body
                self.scopes[node] = ClassScope(parent_scope)
            else:
                raise Exception(node)

            cfg = cfa(node, body)
            # cfg.show()

            self.cfgs[node] = cfg
            self.input_states[(node, self.first_block(cfg))] = state
            self.mark_changed((node, self.first_block(cfg)))

            if isinstance(node, (_ast.FunctionDef, _ast.ClassDef)):
                scope = self.scopes[node]
                for n in ast_utils.find_global_vars(node):
                    scope._set_global(n)
        return self.scopes[node]

    def compute(self, bb_analyzer, aggregator):
        while True:
            k = self._queue.get_next()
            if k is None:
                break
            node, nid = k

            start = self.input_states[k]

            cfg = self.cfgs[node]
            if nid == self.last_block(cfg):
                self.output_states[k] = dict(start)
                continue

            self.errors[k] = {}
            self.cur_key = k
            end = bb_analyzer(self, self.scopes[node], cfg.blocks[nid], start)
            assert self.cur_key == k
            self.cur_key = None

            self.output_states[k] = end
            # print
            # print "finished", nid
            # print "started at", start
            # print "ended at", end


            if self.backwards:
                to_, from_ = cfg.connects_from, cfg.connects_to
            else:
                to_, from_ = cfg.connects_to, cfg.connects_from

            for next_id in to_.get(nid, []):
                # print "looking at", next_id
                d = dict([(pid, self.output_states.get((node, pid), None)) for pid in from_[next_id]])
                new_input = aggregator(d, next_id, self.input_states.get((node, next_id), None))
                if new_input is not None:
                    self.input_states[(node, next_id)] = new_input
                    self.mark_changed((node, next_id))

        return self.input_states, self.output_states



