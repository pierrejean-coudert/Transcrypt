def is_primitive(s):
    #direct call to JS
    return (typeof(s) =='string') or (typeof(s) == 'number')

def is_array(s):
    #direct call to JS
    return Array.isArray(s)


def VNode(sel, data={}, children, text, elm) :
    key = data['key'] if 'key' in data.keys else None
    return {
        'sel': sel,
        'data': data,
        'children': children,
        'text': text,
        'elm': elm,
        'key': key
    }

