######
# My blatant copy of Peter Norvig's Lis.py for learning purposes
######

from __future__ import division

Symbol = str

class Env(dict):
    "An environment: a dict of {'var': val} pairs, with an outer Env."
    def __init__(self, params=(), args=(), outer=None):
        self.update(zip(params, args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears"
        return self if var in self else self.outer.find(var)

def add_globals(env):
    "Add some Scheme standard procedures to an environment."
    import math, operator as op
    env.update(vars(math))
    env.update(
        {'+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv, 'not': op.not_,
         '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,
         'equal?': op.eq, 'eq?': op.is_, 'length': len, 'cons': lambda x,y: [x]+y,
         'car': lambda x: x[0], 'cdr': lambda x: x[1:], 'append': op.add,
         'list': lambda *x: list(x), 'list?': lambda x: isa(x, list),
         'null?': lambda x: x==[], 'symbol?': lambda x: isa(x, Symbol)})
    return env

global_env = add_globals(Env())
isa = isinstance


def eval(x, env=global_env):
    "Evaluate an expression in an environment."
    if isa(x, Symbol):
        return env.find(x)[x]
    elif not isa(x, list):
        return x
    elif x[0] == 'quote':
        (_, exp) = x
        return exp
    elif x[0] == 'if':
        (_, test, conseq, alt) = x
        return eval((conseq if eval(test, env) else alt), env)
    elif x[0] == 'set!':
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == 'define':
        (_, var, exp) = x
        env[var] = eval(exp, env)
    elif x[0] == 'lambda':
        (_, vars, exp) = x
        return lambda *args: eval(exp, Env(vars, args, env))
    elif x[0] == 'begin':
        for exp in x[1:]:
            val = eval(exp, env)
        return val
    else:
        exps = [eval(exp, env) for exp in x]
        proc = exps.pop(0)
        return proc(*exps)

def read(s):
    "Read a scheme expression from a string."
    return read_from(tokenize(s))

parse = read

def tokenize(s):
    "Convert a string into a list of tokens."
    return s.replace('(', ' ( ').replace(')',' ) ').split()

def read_from(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from(tokens))
        tokens.pop(0)
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

def to_string(exp):
    "Convert a Python object back into a Lisp-readable string."
    return '('+' '.join(map(to_string, exp))+')' if isa(exp, list) else str(exp)

def repl(prompt='lis.py> '):
    "A read-eval-print loop."
    while True:
        val = eval(parse(input(prompt)))
        if val is not None: print(to_string(val))
