import _ast
import collections
import sys

import ast_utils

def pos(node):
    return {'lineno':node.lineno, 'col_offset':node.col_offset}

class Jump(_ast.AST):
    def __init__(self):
        self.block_id = None

    def set_dest(self, block_id):
        assert isinstance(block_id, int)
        self.block_id = block_id

class Branch(_ast.AST):
    def __init__(self, test, lineno=None, col_offset=None):
        assert isinstance(test, _ast.AST)
        self.test = test
        self.true_block = None
        self.false_block = None

        if lineno:
            self.lineno = lineno
            self.col_offset = 0

    def set_true(self, bid):
        assert isinstance(bid, int)
        self.true_block = bid

    def set_false(self, bid):
        assert isinstance(bid, int)
        self.false_block = bid

# TODO: this really should be a builtin function rather than a distinct type of ast node
class HasNext(_ast.AST):
    def __init__(self, iter, lineno=None, col_offset=None):
        assert isinstance(iter, _ast.AST)
        self.iter = iter
        if lineno:
            self.lineno = lineno
        if col_offset:
            self.col_offset = col_offset

class CFG(object):
    def __init__(self):
        self.blocks = {}
        self.connects_to = {}
        self.connects_from = {}
        self.start = None
        self.end = None

    def show(self):
        print "Starts at %s, ends at %s" % (self.start, self.end)
        print "Goes-to map:"
        for i, s in sorted(self.connects_to.items()):
            print '%s: %s' % (i, sorted(s))
        print "Comes-from map:"
        for i, s in sorted(self.connects_from.items()):
            print '%s: %s' % (i, sorted(s))
        for bid, blocks in self.blocks.iteritems():
            print bid, map(ast_utils.format_node, blocks)


class CFAState(object):
    def __init__(self):
        self.cfg = CFG()
        self.returns = []

        self._ends_in_break = []
        self._ends_in_continue = []

    def push_loop(self):
        self._ends_in_break.append([])
        self._ends_in_continue.append([])

    def pop_loop(self):
        self._ends_in_break.pop()
        self._ends_in_continue.pop()

    def add_continue(self, c):
        assert callable(c)
        self._ends_in_continue[-1].append(c)

    def add_break(self, c):
        assert callable(c)
        self._ends_in_break[-1].append(c)

    def get_continues(self):
        return list(self._ends_in_continue[-1])

    def get_breaks(self):
        return list(self._ends_in_break[-1])

    def connect(self, from_ids, to_ids):
        for f in from_ids:
            for t in to_ids:
                self.cfg.connects_to.setdefault(f, set()).add(t)
                self.cfg.connects_from.setdefault(t, set()).add(f)

    def analyze(self, analyzer):
        input_props = {}
        input_props[self.cfg.start] = analyzer.start_prop
        output_props = {}
        queue = collections.deque([self.cfg.start])

        while queue:
            # print
            # print "queue is", queue
            # print input_props
            # print output_props
            # print

            bid = queue.popleft()
            # print "processing", bid
            # print

            if bid == self.cfg.end:
                continue

            input_ = input_props[bid]
            output = analyzer.update_func(self, bid, input_)
            assert output is not input_, "Looks like you modified the input instead of constructing a new copy"
            output_props[bid] = output

            for nid in self.cfg.connects_to[bid]:
                inputs = [output_props.get(pid) for pid in self.cfg.connects_from[nid]]
                # print "Merging", self.cfg.connects_from[nid], "into", nid
                new_input, changed = analyzer.merge_func(inputs, input_props.get(nid))
                if changed:
                    input_props[nid] = new_input
                    if nid not in queue:
                        queue.append(nid)

        assert sorted(input_props.keys()) == sorted(output_props.keys()) + [self.cfg.end]

        return input_props, output_props


_cfa_cache = {}
def cfa(node, body=None):
    assert isinstance(node, _ast.AST)
    if body is None:
        body = node.body
    assert isinstance(body, list), (node, body)
    if node in _cfa_cache:
        return _cfa_cache[node]

    state = CFAState()
    state.cfg.start = 0
    j = Jump()
    state.cfg.blocks[state.cfg.start] = [j]
    ending_states = _cfa(body, state, [j.set_dest, lambda nbid: state.connect([state.cfg.start], [nbid])])
    ending_states += state.returns
    # state.show()
    # print ending_states

    last_block = len(state.cfg.blocks)
    assert last_block not in state.cfg.blocks
    for c in ending_states:
        c(last_block)
    state.cfg.end = last_block
    state.cfg.blocks[state.cfg.end] = []

    _cfa_cache[node] = state.cfg
    return state.cfg

_ntemps = 0
def _make_temp_name():
    global _ntemps
    rtn = "! %d" % (_ntemps)
    _ntemps += 1
    return rtn

# Flags you can turn on that affect how the ast is transformed into a cfg
PRUNE_UNREACHABLE_BLOCKS = 0 # prune out blocks that aren't reachable from the entrance
REDUCE_FORS_TO_WHILES = 0    # convert "for i in xrange" loops into while loops
ENFORCE_NO_MULTIMULTI = 0    # break critical edges
ADD_IF_ASSERTS = 0           # add an assertion in the true branch of every if statement that the condition was true [very dangerous semantically, but helps with type analysis]
SIMPLE_WITH_EXIT = 0         # call mgr.__exit__() instead of mgr.__exit__(None, None, None)

def _cfa(body, state, on_gen):
    assert isinstance(on_gen, list)
    for c in on_gen:
        assert callable(c)

    cfg = state.cfg

    def make_connect(cur_bid):
        assert isinstance(cur_bid, int)
        def inner(new_bid):
            assert isinstance(new_bid, int)
            state.connect([cur_bid], [new_bid])
        return inner

    def push_block(block):
        block_id = len(cfg.blocks)
        assert block_id not in cfg.blocks
        cfg.blocks[block_id] = block
        for c in on_gen:
            c(block_id)
        return block_id

    cur_block = []

    for b in body:
        if REDUCE_FORS_TO_WHILES and isinstance(b, _ast.For):
            if isinstance(b.iter, _ast.Call) and isinstance(b.iter.func, _ast.Name) and b.iter.func.id in ("range", "xrange"):
                if not b.iter.keywords and not b.iter.starargs and not b.iter.kwargs:
                    end_var = "__wfend_%d_%d_" % (b.lineno, b.col_offset)
                    iter_var = "__wfiter_%d_%d_" % (b.lineno, b.col_offset)
                    if len(b.iter.args) in (1, 2):
                        if len(b.iter.args) == 1:
                            start = _ast.Num(0)
                            end = b.iter.args[0]
                        elif len(b.iter.args) == 2:
                            start = b.iter.args[0]
                            end = b.iter.args[1]
                        else:
                            start = b.iter.args[0]
                            end = b.iter.args[1]
                        cur_block.append(_ast.Assign([_ast.Name(iter_var, _ast.Store(), not_real=True)], start, lineno=b.lineno, col_offset=b.col_offset, not_real=True))
                        cur_block.append(_ast.Assign([_ast.Name(end_var, _ast.Store(), not_real=True)], end, lineno=b.lineno, col_offset=b.col_offset, not_real=True))

                        body = [
                                _ast.Assign([b.target], _ast.Name(iter_var, _ast.Load(), not_real=True), lineno=b.lineno, col_offset=b.col_offset, not_real=True),
                                _ast.Assign([_ast.Name(iter_var, _ast.Store(), not_real=True)], _ast.BinOp(_ast.Name(iter_var, _ast.Load(), not_real=True), _ast.Add(), _ast.Num(1)), lineno=b.lineno, col_offset=b.col_offset, not_real=True)
                                ] + b.body
                        b = _ast.While(_ast.Compare(_ast.Name(iter_var, _ast.Load(), not_real=True), [_ast.Lt()], [_ast.Name(end_var, _ast.Load(), not_real=True)], lineno=b.lineno, col_offset=b.col_offset, not_real=True), body, b.orelse, not_real=True)


        if isinstance(b, (
                _ast.Assign,
                _ast.AugAssign,
                _ast.ClassDef,
                _ast.Delete,
                _ast.Exec,
                _ast.Expr,
                _ast.FunctionDef,
                _ast.Global,
                _ast.Import,
                _ast.ImportFrom,
                _ast.Print,
                _ast.Pass,
                )):
            cur_block.append(b)
        elif isinstance(b, _ast.Assert):
            cur_block.append(b)
            if isinstance(b.test, _ast.Call) and isinstance(b.test.func, _ast.Name) and b.test.func.id == "isinstance" and isinstance(b.test.args[0], _ast.Name) and isinstance(b.test.args[1], _ast.Name):
                varname = b.test.args[0].id
                cast = _ast.Call(_ast.Name("__cast__", _ast.Load(), not_real=True, **pos(b)), [_ast.Name(varname, _ast.Store(), not_real=True, **pos(b)), b.test.args[1]], [], None, None, not_real=True, **pos(b))
                assign = _ast.Assign([_ast.Name(varname, _ast.Store(), not_real=True, **pos(b))], cast, not_real=True, lineno=b.lineno, col_offset=b.col_offset)
                cur_block.append(assign)
        elif isinstance(b, (_ast.Break, _ast.Continue)):
            f = state.add_break if isinstance(b, _ast.Break) else state.add_continue
            if cur_block:
                j = Jump()
                cur_block.append(j)
                block_id = push_block(cur_block)
                f(j.set_dest)
                f(make_connect(block_id))
            else:
                for c in on_gen:
                    f(c)
            return []
        elif isinstance(b, _ast.If):
            br = Branch(b.test, lineno=b.lineno)
            cur_block.append(br)
            next_block = push_block(cur_block)
            on_gen = None # make sure this doesn't get used
            cur_block = []

            gen_true = [br.set_true, make_connect(next_block)]
            gen_false = [br.set_false, make_connect(next_block)]
            if ENFORCE_NO_MULTIMULTI:
                on_gen = gen_true
                j1 = Jump()
                gen_true = [make_connect(push_block([j1])), j1.set_dest]

                on_gen = gen_false
                j2 = Jump()
                gen_false = [make_connect(push_block([j2])), j2.set_dest]

                on_gen = None

            assert b.body
            body = b.body
            if isinstance(b.test, _ast.Call) and isinstance(b.test.func, _ast.Name) and b.test.func.id == "isinstance" and isinstance(b.test.args[0], _ast.Name) and isinstance(b.test.args[1], _ast.Name):
                varname = b.test.args[0].id
                cast = _ast.Call(_ast.Name("__cast__", _ast.Load(), not_real=True, **pos(b)), [_ast.Name(varname, _ast.Store(), not_real=True, **pos(b)), b.test.args[1]], [], None, None, not_real=True, **pos(b))
                assign = _ast.Assign([_ast.Name(varname, _ast.Store(), not_real=True, **pos(b))], cast, not_real=True, lineno=b.lineno, col_offset=b.col_offset)
                body = [assign] + body
            if ADD_IF_ASSERTS:
                body = [_ast.Assert(b.test, None, not_real=True, **pos(b))] + body
            ending_gen = _cfa(body, state, gen_true)
            if b.orelse:
                ending_gen += _cfa(b.orelse, state, gen_false)
            else:
                ending_gen += gen_false
            on_gen = ending_gen

            if not on_gen and PRUNE_UNREACHABLE_BLOCKS:
                return []
        elif isinstance(b, _ast.TryExcept):
            j = Jump()
            cur_block.append(j)
            next_block = push_block(cur_block)
            on_gen = [j.set_dest, make_connect(next_block)]
            cur_block = []

            on_gen = _cfa(b.body, state, on_gen)

            # Set this to evaluate a string to try to defeat simple flow analysis
            br = Branch(_ast.Str("nonzero"))
            next_block = push_block([br])

            on_except = [br.set_false, make_connect(next_block)]
            on_fine = [br.set_true, make_connect(next_block)]

            assert len(b.handlers) >= 1
            # for handler in b.handlers:
                # on_except = _cfa(b.handlers[0].body, state, on_except)

            if b.orelse:
                on_fine = _cfa(b.orelse, state, on_fine)

            if ENFORCE_NO_MULTIMULTI:
                j = Jump()
                on_gen = on_fine
                next_block = push_block([j])
                on_fine = [j.set_dest, make_connect(next_block)]

                j = Jump()
                on_gen = on_except
                next_block = push_block([j])
                on_except = [j.set_dest, make_connect(next_block)]

            on_gen = on_fine + on_except
            cur_block = []
        elif isinstance(b, _ast.TryFinally):
            j = Jump()
            cur_block.append(j)
            next_block = push_block(cur_block)
            on_gen = [j.set_dest, make_connect(next_block)]
            cur_block = []

            on_gen = _cfa(b.body, state, on_gen)
            on_gen = _cfa(b.finalbody, state, on_gen)
        elif isinstance(b, _ast.While):
            # This could also be architected as having no extra block and having two jump statements, but I don't like that
            if cur_block:
                j = Jump()
                cur_block.append(j)
                on_gen = [make_connect(push_block(cur_block)), j.set_dest]
                cur_block = []

            always_true = False
            always_false = False
            if isinstance(b.test, _ast.Name):
                if b.test.id == "True":
                    always_true = True
                elif b.test.id == "False":
                    always_false = True
            elif isinstance(b.test, _ast.Num):
                if b.test.n:
                    always_true = True
                else:
                    always_false = True

            if always_true:
                br = Jump()
                on_true = br.set_dest
            elif always_false:
                br = Jump()
                on_false = br.set_dest
            else:
                br = Branch(b.test)
                on_true = br.set_true
                on_false = br.set_false
            init_id = push_block([br])
            on_gen = None
            assert cur_block == [] # just checking

            if not always_false:
                gen_true = [on_true, make_connect(init_id)]
            if not always_true:
                gen_false = [on_false, make_connect(init_id)]
            if ENFORCE_NO_MULTIMULTI:
                if not always_false:
                    on_gen = gen_true
                    j1 = Jump()
                    gen_true = [make_connect(push_block([j1])), j1.set_dest]

                if not always_true:
                    on_gen = gen_false
                    j2 = Jump()
                    gen_false = [make_connect(push_block([j2])), j2.set_dest]

                on_gen = None

            ending_gen = []
            if not always_false:
                state.push_loop()
                assert b.body
                loop_ending_gen = _cfa(b.body, state, gen_true)
                loop_ending_gen += state.get_continues()
                for c in loop_ending_gen:
                    c(init_id)
                ending_gen = state.get_breaks()
                state.pop_loop()


            if not always_true:
                if b.orelse:
                    ending_gen += _cfa(b.orelse, state, gen_false)
                else:
                    ending_gen += gen_false

            on_gen = ending_gen
            if not on_gen and PRUNE_UNREACHABLE_BLOCKS:
                return []
        elif isinstance(b, _ast.For):
            iter_func = _ast.Attribute(b.iter, "__iter__", _ast.Load(), not_real=True, lineno=b.lineno, col_offset=b.col_offset)
            iter_call = _ast.Call(iter_func, [], [], None, None, not_real=True, lineno=b.lineno, col_offset=b.col_offset)
            # iter_var = _make_temp_name()
            iter_var = "__foriter_%d_%d_" % (b.lineno, b.col_offset)
            iter_assign = _ast.Assign([_ast.Name(iter_var, _ast.Store(), not_real=True, **pos(b))], iter_call, not_real=True, lineno=b.lineno, col_offset=b.col_offset)
            cur_block.append(iter_assign)

            j = Jump()
            cur_block.append(j)
            on_gen = [make_connect(push_block(cur_block)), j.set_dest]
            cur_block = []

            br = Branch(HasNext(_ast.Name(iter_var, _ast.Load(), not_real=True, **pos(b)), **pos(b)), **pos(b))
            init_id = push_block([br])
            on_gen = None
            assert cur_block == [] # just checking

            gen_true = [br.set_true, make_connect(init_id)]
            gen_false = [br.set_false, make_connect(init_id)]
            if ENFORCE_NO_MULTIMULTI:
                on_gen = gen_true
                j1 = Jump()
                gen_true = [make_connect(push_block([j1])), j1.set_dest]

                on_gen = gen_false
                j2 = Jump()
                gen_false = [make_connect(push_block([j2])), j2.set_dest]

                on_gen = None

            ending_gen = []

            state.push_loop()

            next_func = _ast.Attribute(_ast.Name(iter_var, _ast.Load(), not_real=True, **pos(b)), "next", _ast.Load(), not_real=True, lineno=b.lineno, col_offset=b.col_offset)
            next = _ast.Call(next_func, [], [], None, None, not_real=True, lineno=b.lineno, col_offset=b.col_offset)
            next_assign = _ast.Assign([b.target], next, not_real=True, lineno=b.lineno, col_offset=b.col_offset)
            next_iter_gen = _cfa([next_assign] + b.body, state, gen_true)
            next_iter_gen += state.get_continues()
            for c in next_iter_gen:
                c(init_id)

            loop_done_gen = list(state.get_breaks())

            state.pop_loop()

            if b.orelse:
            # if b.orelse and loop_ending_blocks:
                loop_done_gen += _cfa(b.orelse, state, gen_false)
            else:
                loop_done_gen += gen_false

            on_gen = loop_done_gen
            if not on_gen and PRUNE_UNREACHABLE_BLOCKS:
                return []
        elif isinstance(b, (_ast.Return, _ast.Raise)):
            cur_block.append(b)
            block_id = push_block(cur_block)
            state.returns.append(make_connect(block_id))
            return []
        elif isinstance(b, _ast.With):
            # XXX totally ignores the functionality of with statements

            # Have to save the context manager because the expression might not be valid later
            mgr_name = "__mgr_%s_%s_" % (b.lineno, b.col_offset)
            save_mgr = _ast.Assign([_ast.Name(mgr_name, _ast.Store(), lineno=b.lineno, col_offset=b.col_offset, not_real=True)], b.context_expr, lineno=b.lineno, col_offset=b.col_offset, not_real=True)

            enter_func = _ast.Attribute(_ast.Name(mgr_name, _ast.Load(), lineno=b.lineno, col_offset=b.col_offset, not_real=True), "__enter__", _ast.Load(), lineno=b.lineno, col_offset=b.col_offset, not_real=True)
            bind = _ast.Call(enter_func, [], [], None, None, lineno=b.lineno, col_offset="__enter__()", not_real=True)

            if b.optional_vars:
                assert isinstance(b.optional_vars, _ast.AST)
                init = _ast.Assign([b.optional_vars], bind, lineno=b.lineno, col_offset=b.col_offset, not_real=True)
            else:
                init = _ast.Expr(bind, lineno=b.lineno, col_offset=b.col_offset, not_real=True)

            exit_func = _ast.Attribute(_ast.Name(mgr_name, _ast.Load(), lineno=b.lineno, col_offset=b.col_offset, not_real=True), "__exit__", _ast.Load(), lineno=b.lineno, col_offset=b.col_offset, not_real=True)
            if SIMPLE_WITH_EXIT:
                exit_call = _ast.Call(exit_func, [], [], None, None, lineno=b.lineno, col_offset=b.col_offset, not_real=True)
            else:
                none_ = _ast.Name("None", _ast.Load(), lineno=b.lineno, col_offset=b.col_offset, not_real=True)
                exit_call = _ast.Call(exit_func, [none_, none_, none_], [], None, None, lineno=b.lineno, col_offset=b.col_offset, not_real=True)
            exit = _ast.Expr(exit_call, lineno=b.lineno, col_offset="__exit__()", not_real=True)

            cur_block.extend([save_mgr, init])
            j = Jump()
            cur_block.append(j)
            next_block = push_block(cur_block)
            on_gen = [j.set_dest, make_connect(next_block)]
            cur_block = []

            body = b.body + [exit]
            next_gen = _cfa(body, state, on_gen)
            on_gen = next_gen
        else:
            raise Exception(b)

    if cur_block:
        j = Jump()
        cur_block.append(j)
        next = push_block(cur_block)
        return [j.set_dest, make_connect(next)]
    return on_gen

    return on_gen

class TestAnalyzer(object):
    def __init__(self):
        self.start_prop = set()

    def update_func(self, state, bid, input_):
        rtn = set(input_)
        rtn.add(bid)
        return rtn

    def merge_func(self, inputs, output):
        new_output = set()
        for i in inputs:
            if not i:
                continue
            new_output.update(i)
        if not output:
            return new_output, True
        assert len(new_output) >= len(output)
        return new_output, (len(new_output) > len(output))

if __name__ == "__main__":
    fn = sys.argv[1]
    cfa(ast_utils.parse(open(fn).read(), fn)).show()
