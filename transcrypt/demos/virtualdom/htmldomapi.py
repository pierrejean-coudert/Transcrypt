
def createElement(tag_name):
    document.createElement(tag_name)

def createElementNS(namespaceURI, qualifiedName):
    document.createElementNS(namespaceURI, qualifiedName)

def createTextNode(text):
    document.createTextNode(text)

def insertBefore(parent_node, new_node, reference_node):
    parent_node.insertBefore(new_node, reference_node)

def removeChild(node, child):
    node.removeChild(child)

def appendChild(node, child):
    node.appendChild(child)

def parentNode(node):
    return node.parentElement

def nextSibling(node):
    return node.nextSibling

def tagName(node):
    return node.tagName

def setTextContent(node, text):
    node.textContent = text
