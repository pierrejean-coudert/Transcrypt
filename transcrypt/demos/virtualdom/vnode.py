def is_primitive(s):
    #direct call to JS
    return (typeof(s) =='string') or (typeof(s) == 'number')

def is_array(s):
    #direct call to JS
    return Array.isArray(s)


def VNode(sel, data=None, children=None, text=None, elm=None) :
    data = dict() if data is None else data
    children = list() if children is None else children
    key = data['key'] if 'key' in data else None
    return {
        'sel': sel,
        'data': data,
        'children': children,
        'text': text,
        'elm': elm,
        'key': key
    }

