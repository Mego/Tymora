#!/usr/bin/env python3

import re
from random import randint
from collections import Iterable, OrderedDict
from functools import total_ordering


def as_list(x):
    if isinstance(x, Iterable):
        return list(x)
    else:
        return [x]


def roll(num_sides):
    if int(num_sides) == 0:
        return Die(0, 0)
    return Die(randint(1, num_sides), num_sides)


def roll_many(num_dice, num_sides):
    num_dice = sum(as_list(num_dice))
    num_sides = sum(as_list(num_sides))
    return [roll(num_sides) for _ in range(num_dice)]


def roll_count(num_dice, num_sides):
    rolls = roll_many(num_dice, num_sides)
    counts = {int(x):rolls.count(x) for x in rolls}
    return "{%s}" % (', '.join("{}: {}".format(k, counts[k]) for k in sorted(counts)))


def reroll(dice, values):
    dice, values = as_list(dice), as_list(values)
    return [die.reroll() if die in values else die for die in dice]


def reroll_all(dice, values):
    dice, values = as_list(dice), as_list(values)
    while any(die in values for die in dice):
        dice = [die.reroll() if die in values else die for die in dice]
    return dice


def take_low(dice, num_values):
    dice = as_list(dice)
    num_values = sum(as_list(num_values))
    return sorted(dice)[:num_values]


def take_high(dice, num_values):
    dice = as_list(dice)
    num_values = sum(as_list(num_values))
    return sorted(dice, reverse=True)[:num_values]


def add(a, b):
    a = sum(as_list(a))
    b = sum(as_list(b))
    return a+b


def sub(a, b):
    a = sum(as_list(a))
    b = sum(as_list(b))
    return a-b


def mul(a, b):
    a = sum(as_list(a))
    b = sum(as_list(b))
    return a*b


def div(a, b):
    a = sum(as_list(a))
    b = sum(as_list(b))
    return a//b


def concat(a, b):
    return as_list(a)+as_list(b)


def list_diff(a, b):
    return [x for x in as_list(a) if x not in as_list(b)]


def if_op(a, b):
    return b if (sum(as_list(a)) > 0) else 0


@total_ordering
class Die:
    def __init__(self, value, sides):
        self.value = value
        self.sides = sides

    def reroll(self):
        self.value = roll(self.sides).value
        return self

    def __int__(self):
        return self.value

    __index__ = __int__

    def __lt__(self, other):
        return int(self) < int(other)

    def __eq__(self, other):
        return int(self) == int(other)

    def __add__(self, other):
        return int(self) + int(other)

    def __sub__(self, other):
        return int(self) - int(other)

    __radd__ = __add__
    __rsub__ = __sub__

    def __str__(self):
        return str(int(self))

    def __repr__(self):
        return "{} ({})".format(self.value, self.sides)


class Operator:
    def __init__(self, op_str, precedence, func):
        self.op_str = op_str
        self.precedence = precedence
        self.func = func

    def __call__(self, *args):
        return self.func(*args)

    def __str__(self):
        return self.op_str

    __repr__ = __str__


ops = {
    'd': Operator('d', 4, roll_many),
    'r': Operator('r', 3, reroll),
    'R': Operator('R', 3, reroll_all),
    't': Operator('t', 3, take_low),
    'T': Operator('T', 3, take_high),
    '/': Operator('/', 2, div),
    '*': Operator('*', 2, mul),
    '+': Operator('+', 1, add),
    '-': Operator('-', 1, sub),
    '.': Operator('.', 1, concat),
    '_': Operator('_', 1, list_diff),
    '?': Operator('?', 0, if_op),
}


def evaluate_dice(expr):
    try:
        return sum(as_list(evaluate_rpn(shunting_yard(tokenize(expr)))))
    except:
        return None


def evaluate_rpn(expr):
    stack = []
    while expr:
        tok = expr.pop()
        if isinstance(tok, Operator):
            a, b = stack.pop(), stack.pop()
            stack.append(tok(b, a))
        else:
            stack.append(tok)
    return stack[0]


def shunting_yard(tokens):
    outqueue = []
    opstack = []
    for tok in tokens:
        if isinstance(tok, int):
            outqueue = [tok] + outqueue
        elif tok == '(':
            opstack.append(tok)
        elif tok == ')':
            while opstack[-1] != '(':
                outqueue = [opstack.pop()] + outqueue
            opstack.pop()
        else:
            while opstack and opstack[-1] != '(' and opstack[-1].precedence > tok.precedence:
                outqueue = [opstack.pop()] + outqueue
            opstack.append(tok)
    while opstack:
        outqueue = [opstack.pop()] + outqueue
    return outqueue


def tokenize(expr):
    global ops
    while expr:
        tok, expr = expr[0], expr[1:]
        if tok in "0123456789":
            while expr and expr[0] in "0123456789":
                tok, expr = tok + expr[0], expr[1:]
            tok = int(tok)
        else:
            tok = ops[tok] if tok in ops else tok
        yield tok


if __name__ == '__main__':
    while True:
        try:
            dice_str = input()
            print("{} => {}".format(dice_str, evaluate_dice(dice_str)))
        except EOFError:
            exit()
