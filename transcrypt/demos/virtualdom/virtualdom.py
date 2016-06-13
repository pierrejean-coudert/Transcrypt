from htmldomapi import *
from vnode import *
from h import h

# inspired by https://github.com/paldepind/snabbdom/blob/master/snabbdom.js

emptyNode = VNode('', {}, [], None, None)


def sameVnode(vnode1, vnode2):
    return (vnode1['key'] == vnode2['key']) and (vnode1['sel'] == vnode2['sel'])


def createKeyToOldIdx(children, begin_idx, end_idx):
    map = {}
    for i in range(begin_idx, end_idx):
        key = children[i]['key']
        if key in map:
            map[key] = i
    return map

hooks = ['create', 'update', 'remove', 'destroy', 'pre', 'post']


def init(modules=[]):
    cbs = {}

    for hook in hooks:
        cbs[hook] = []
        for module in modules:
            if module[hooks] is not None:
                cbs[hook].append(module[hook])

    def emptyNodeAt(elm):
        return VNode(tagName(elm).toLowerCase(), {}, [], None, elm)

    def createRmCb(childElm, listeners):
        def remove_child():
            listeners -= 1
            if listeners == 0:
                removeChild(parentNode(childElm), childElm)
        return remove_child
    pass

vnode = h('div', {'style': {'color': '#000'}}, [
  h('h1', 'Headline'),
  h('p', 'A paragraph'),
])


