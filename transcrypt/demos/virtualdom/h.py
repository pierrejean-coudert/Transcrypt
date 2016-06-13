from vnode import *


def map(f, l):
    return [f(item) for item in l]


def filter(f, l):
    return [item for item in l if f(item)]


def add_ns(data, children):
    data['ns'] = 'http://www.w3.org/2000/svg'
    if children is not None:
        for child in children:
            add_ns(child['data'], child['children'])


def h(sel, b=None, c=None):
    data = {}
    text = None
    children = None

    if c is not None:
        data = b
        if is_array(c):
            children = c
        elif is_primitive(c):
            text = c
    elif b is not None:
        if is_array(b):
            children = b
        elif is_primitive(b):
            text = b
        else:
            data = b

    if is_array(children):
        children2 = map(lambda child: (VNode(None, None, None, child) if is_primitive(child) else child),
            children)
        children = children2

    if sel[0:2] == 'svg':
        add_ns(data, children)

    return VNode(sel, data, children, text, None)

