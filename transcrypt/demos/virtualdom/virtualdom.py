import  htmldomapi as api
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

cbs = {}


def init(modules=[]):
    for hook in hooks:
        cbs[hook] = []
        for module in modules:
            if module[hooks] is not None:
                cbs[hook].append(module[hook])

def emptyNodeAt(elm):
    return VNode(api.tagName(elm).toLowerCase(), {}, [], None, elm)

def createRmCb(childElm, listeners):
    def remove_child():
        listeners -= 1
        if listeners == 0:
            api.removeChild(api.parentNode(childElm), childElm)
    return remove_child

def createElm(vnode, insertedVnodeQueue):
    data = vnode['data']
    if data is not None:
        if data['hook'] is not None:
            if data['hook']['init'] is not None:
                i= data['hook']['init']
                i(vnode)
                data = vnode['data']

    children = vnode['children']
    sel = vnode['sel']

    if sel is not None:
        # Parse selector
        hashIdx = sel.find('#')
        dotIdx = sel.find('.', hashIdx)
        hash = hashIdx if hashIdx > 0 else len(sel)
        dot = dotIdx if dotIdx > 0 else len(sel)
        tag =  sel[0: min(hash, dot)] if (hashIdx != -1 or dotIdx != -1) else sel

        if data is not None and data['ns'] is not None:
            elm = vnode['elm'] = api.createElementNS(data['ns'], tag)
        else:
            elm = vnode['elm'] = api.createElement(tag)
        if hash < dot:
            elm.id = sel[hash + 1:dot]
        if dotIdx > 0:
            elm.className = sel[dot + 1:].replace( '.', ' ')
        if is_array(children):
            for child in children:
                api.appendChild(elm, createElm(child, insertedVnodeQueue))
        elif is_primitive(vnode['text']):
            api.appendChild(elm, api.createTextNode(vnode['text']))

        for cb in cbs['create']:
            cb(emptyNode, vnode)

        i = vnode['data']['hook'] # Reuse variable
        if i is not None:
            if i['create'] is not None:
                i['create'](emptyNode, vnode)
            if i['insert'] is not None:
                insertedVnodeQueue.append(vnode)
        else:
            elm = vnode.elm = api.createTextNode(vnode.text)
    return vnode.elm

def addVnodes(parentElm, before, vnodes, startIdx, endIdx, insertedVnodeQueue):
    for Idx in range(startIdx, endIdx+1):
        api.insertBefore(parentElm, createElm(vnodes[Idx], insertedVnodeQueue), before)

def invokeDestroyHook(vnode):
    data = vnode['data']
    if data is not None:
        if data['hook'] is not None:
            if data['hook']['destroy'] is not None:
                i = data['hook']['destroy']
                i(vnode)
        for cb in cbs['destroy']:
            cb(emptyNode, vnode)
        if vnode['children'] is not None:
            for child in vnode['children']:
                invokeDestroyHook(child)

def removeVnodes(parentElm, vnodes, startIdx, endIdx):
    for Idx in range(startIdx, endIdx+1):
        ch = vnodes[Idx]
        if ch is not None:
            if ch['sel'] is not None:
                invokeDestroyHook(ch)
                listeners = len(cbs['remove']) + 1
                rm = createRmCb(ch['elm'], listeners)
                for cb in cbs['remove']:
                    cb(ch, rm)
                if ch['data'] is not None:
                    if ch['data']['hook'] is not None:
                        if ch['data']['hook']['remove'] is not None:
                            i = ch['data']['hook']['remove']
                            i(ch, rm)
                else:
                    rm()
            else: # Text node
                api.removeChild(parentElm, ch.elm)

def updateChildren(parentElm, oldCh, newCh, insertedVnodeQueue):
    oldStartIdx = 0
    newStartIdx = 0
    oldEndIdx = len(oldCh) - 1
    oldStartVnode = oldCh[0]
    oldEndVnode = oldCh[oldEndIdx]
    newEndIdx = len(newCh) - 1
    newStartVnode = newCh[0]
    newEndVnode = newCh[newEndIdx]

    while oldStartIdx <= oldEndIdx and newStartIdx <= newEndIdx :
        if oldStartVnode is None :
            oldStartVnode = oldCh[++oldStartIdx] # Vnode has been moved left
        elif oldEndVnode is None:
            oldEndVnode = oldCh[--oldEndIdx]
        elif sameVnode(oldStartVnode, newStartVnode):
            patchVnode(oldStartVnode, newStartVnode, insertedVnodeQueue)
            oldStartVnode = oldCh[++oldStartIdx]
            newStartVnode = newCh[++newStartIdx]
        elif sameVnode(oldEndVnode, newEndVnode):
            patchVnode(oldEndVnode, newEndVnode, insertedVnodeQueue)
            oldEndVnode = oldCh[--oldEndIdx]
            newEndVnode = newCh[--newEndIdx]
        elif sameVnode(oldStartVnode, newEndVnode): # Vnode moved right
            patchVnode(oldStartVnode, newEndVnode, insertedVnodeQueue)
            api.insertBefore(parentElm, oldStartVnode['elm'], api.nextSibling(oldEndVnode['elm']))
            oldStartVnode = oldCh[++oldStartIdx]
            newEndVnode = newCh[--newEndIdx]
        elif sameVnode(oldEndVnode, newStartVnode): # Vnode moved left
            patchVnode(oldEndVnode, newStartVnode, insertedVnodeQueue)
            api.insertBefore(parentElm, oldEndVnode['elm'], oldStartVnode['elm'])
            oldEndVnode = oldCh[--oldEndIdx]
            newStartVnode = newCh[++newStartIdx]
        else:
            if oldKeyToIdx is None:
                oldKeyToIdx = createKeyToOldIdx(oldCh, oldStartIdx, oldEndIdx)
            idxInOld = oldKeyToIdx[newStartVnode['key']]
            if idxInOld is None: # New element
                api.insertBefore(parentElm, createElm(newStartVnode, insertedVnodeQueue), oldStartVnode['elm'])
                newStartVnode = newCh[++newStartIdx]
            else:
                elmToMove = oldCh[idxInOld]
                patchVnode(elmToMove, newStartVnode, insertedVnodeQueue)
                oldCh[idxInOld] = None
                api.insertBefore(parentElm, elmToMove['elm'], oldStartVnode['elm'])
                newStartVnode = newCh[++newStartIdx]

    if oldStartIdx > oldEndIdx:
        before = None if newCh[newEndIdx+1] is None else newCh[newEndIdx + 1].elm
        addVnodes(parentElm, before, newCh, newStartIdx, newEndIdx, insertedVnodeQueue)
    elif newStartIdx > newEndIdx:
        removeVnodes(parentElm, oldCh, oldStartIdx, oldEndIdx)


def patchVnode(oldVnode, vnode, insertedVnodeQueue):
    hook = None
    if vnode['data'] is not None:
        if vnode['data']['hook'] is not None:
            hook =vnode['data']['hook']
            if hook['prepatch'] is not None:
                i = hook['prepatch']
                i(oldVnode, vnode)
    elm = vnode['elm'] = oldVnode['elm']
    oldCh = oldVnode['children']
    ch = vnode['children']
    if oldVnode == vnode:
        return
    if not sameVnode(oldVnode, vnode):
        parentElm = api.parentNode(oldVnode['elm'])
        elm = createElm(vnode, insertedVnodeQueue)
        api.insertBefore(parentElm, elm, oldVnode['elm'])
        removeVnodes(parentElm, [oldVnode], 0, 0)
        return
    if vnode['data'] is not None:
        for cb in cbs['update']:
            cb(oldVnode, vnode)

        if vnode['data']['hook'] is not None:
            if vnode['data']['hook']['update'] is not None:
                i = vnode['data']['hook']['update']
                i(oldVnode, vnode)

    if vnode['text'] is None:
        if oldCh is not None and ch is not None:
            if oldCh != ch:
                updateChildren(elm, oldCh, ch, insertedVnodeQueue)
        elif ch is not None:
            if oldVnode['text'] is not None:
                api.setTextContent(elm, '')
            addVnodes(elm, None, ch, 0, ch.length - 1, insertedVnodeQueue)
        elif oldCh is not None:
            removeVnodes(elm, oldCh, 0, oldCh.length - 1)
        elif oldVnode['text'] is not None:
            api.setTextContent(elm, '')
    elif oldVnode['text'] != vnode['text']:
        api.setTextContent(elm, vnode['text'])
    if hook is not None:
        if hook['postpatch'] is not None:
            hook['postpatch'](oldVnode, vnode)

def patch(oldVnode, vnode):
    insertedVnodeQueue = []
    for cb in cbs['pre']:
        cb()

    if oldVnode['sel'] is None:
        oldVnode = emptyNodeAt(oldVnode)

    if sameVnode(oldVnode, vnode):
        patchVnode(oldVnode, vnode, insertedVnodeQueue)
    else :
        elm = oldVnode['elm']
        parent = api.parentNode(elm)

        createElm(vnode, insertedVnodeQueue)

        if parent != None:
            api.insertBefore(parent, vnode['elm'], api.nextSibling(elm))
            removeVnodes(parent, [oldVnode], 0, 0)

    for ivnode in insertedVnodeQueue:
        ivnode['data']['hook']['insert'](ivnode)

    for cb in cbs['post']:
        cb()

    return vnode


init()

vnode = h('div#container.two.classes', {'on': {'click': 'someFn'}}, [
  h('span', {'style': {'fontWeight': 'bold'}}, 'This is bold'),
  ' and this is just normal text',
  h('a', {'props': {'href': '/foo'}}, 'I\'ll take you places!')
])

container = document.getElementById('container')

#  Patch into empty DOM element - this modifies the DOM as a side effect
patch(container, vnode)


newVnode = h('div#container.two.classes', {'on': {'click': 'anotherEventHandler'}}, [
  h('span', {'style': {'fontWeight': 'normal', 'fontStyle': 'italics'}}, 'This is now italics'),
  ' and this is still just normal text',
  h('a', {'props': {'href': '/bar'}}, 'I\'ll take you places!')
])

# Second `patch` invocation
patch(vnode, newVnode)


