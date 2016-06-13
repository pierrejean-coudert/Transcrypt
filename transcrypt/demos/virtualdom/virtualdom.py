from htmldomapi import *
from vnode import *
from h import h



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


vnode = h('div', {'style': {'color': '#000'}}, [
  h('h1', 'Headline'),
  h('p', 'A paragraph'),
])


