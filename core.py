# coding: utf-8

from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

import re


ESC_STR = r'#[!]#'


class Symbol(str):
    pass


class Lambda(object):

    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env

    def __call__(self, *args):
        return zy_eval(self.body, Env(self.parms, args, self.env))


class Env(dict):
    def __init__(self, parms=(), args=(), outer=None):
        self.outer = outer
        self.update(zip(parms, args))

    def find(self, var):
        return self if (var in self) else self.outer.find(var)


class ZyString(str):
    def __div__(self, other):
        return map(ZyString, self.split(other))

    __truediv__ = __div__

    def __sub__(self, other):
        return ZyString(self.replace(other, ''))

    def __add__(self, other):
        return ZyString(super(ZyString, self).__add__(other))

    def __mul__(self, other):
        return ZyString(super(ZyString, self).__mul__(other))


class ZyBool(object):
    true = True
    false = False

    def __new__(cls, val):
        if val:
            if cls.true is True:
                cls.true = super(ZyBool, cls).__new__(cls, cls.true)
            return cls.true
        else:
            if cls.false is False:
                cls.false = super(ZyBool, cls).__new__(cls, cls.false)
            return cls.false

    def __init__(self, val):
        self.val = val

    def __nonzero__(self):
        return self.val

    def __repr__(self):
        return '#t' if self.val else '#f'

    __str__ = __repr__

ZyTrue = ZyBool(True)
ZyFalse = ZyBool(False)


def atom(token):
    if token[0] == '"':
        return ZyString(token[1:-1].decode('utf-8'))
    try:
        return float(token)
    except ValueError:
        return Symbol(token)


def tokenize(program):
    program_iter = iter(program)
    strings = []
    while True:
        try:
            c = program_iter.next()
        except StopIteration:
            break

        if c == '"':
            r = []
            while True:
                try:
                    c = program_iter.next()
                except StopIteration:
                    break
                if c == '"':
                    strings.append(''.join(r).replace('"', ''))
                    break
                else:
                    r.append(c)

    tokens = re.sub('\"(.+?)\"', ESC_STR, program).replace(')', ' ) ').replace('(', ' ( ').split()
    str_index = 0
    for k, t in enumerate(tokens):
        if t == ESC_STR:
            tokens[k] = '"%s"' % strings[str_index]
            str_index += 1
    return tokens


def atomize(tokens):
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')
    token = tokens.pop(0)
    if token == '(':
        r = []
        while tokens[0] != ')':
            r.append(atomize(tokens))
        tokens.pop(0)
        return r
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)


def parse(program):
    return atomize(tokenize(program))


def standard_env():
    env = Env()

    env.update({
        '.': lambda *args, **kwargs: None,
        '!': lambda x: ZyBool(x),
        '!!': lambda x: ZyBool(not x),
        '#pi': 3.141592653589793,
        '#nil': None,
        '#f': ZyFalse,
        '#t': ZyTrue,
        '*': lambda x, y: x * y,
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '/': lambda x, y: x / y,
        '<': lambda x, y: x < y,
        '>': lambda x, y: x > y,
        '=': lambda x, y: x == y,
        '**': lambda x, y: x ** y,
        '++': lambda x: x + 1.,
        '--': lambda x: x - 1.,
        '..': lambda x, y, s=1: range(int(x), int(y), int(s)),
        '/]': lambda x: float(int(x)),
        '/[': round,
        '[]': lambda *x: list(x),
        '[:]': lambda x, y: y[int(x)],
        ',': float,
        "'": ZyString,
        '<=': lambda x, y: x <= y,
        '>=': lambda x, y: x >= y,
        '<->': lambda x, y: [y, x],
        '>>': print,
        '<<': raw_input,
    })
    return env


GLOBAL_ENV = standard_env()


def zy_eval(x, env=GLOBAL_ENV):
    if isinstance(x, Symbol):
        return env.find(x)[x]
    elif not isinstance(x, list):
        return x
    elif x[0] == '?':
        _, test, _if, _else = x
        exp = (_if if zy_eval(test, env) else _else)
        return zy_eval(exp, env)
    elif x[0] == '->':
        _, var, exp = x
        env[var] = zy_eval(exp, env)
    elif x[0] == ',->':
        x = x[1:]
        ln = int(len(x) / 2)
        params, args = x[:ln], x[ln:]
        if len(params) != len(args):
            raise ValueError('It has not been possible to do the unpack')
        for i in range(ln):
            env[params[i]] = zy_eval(args[i], env)
    elif x[0] == '@':
        _, parms, body = x
        return Lambda(parms, body, env)
    elif x[0] == '*>':
        _, var, _list, body, r = x
        _env = env
        for w in zy_eval(_list, _env):
            _env = Env([var], [w], _env)
            zy_eval(body, _env)
        return zy_eval(r, _env)
    else:
        return zy_eval(x[0], env)(*[zy_eval(exp, env) for exp in x[1:]])


def to_zy_str(exp):
    if isinstance(exp, Symbol):
        return exp
    elif isinstance(exp, ZyString):
        return '"%s"' % exp.encode('utf-8').replace('"', r'\"')
    elif isinstance(exp, list):
        return "(%s)" % ' '.join(map(to_zy_str, exp))
    else:
        return str(exp)
