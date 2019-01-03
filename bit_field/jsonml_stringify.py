def jsonml_stringify(res):
    if res is None:
        return ''
    tag = res[0]
    attributes = ' '.join('{}="{}"'.format(k, v) for k, v in res[1].items())
    if len(res) > 2 and isinstance(res[2], str):
        content = res[2]
    else:
        content = ''.join(jsonml_stringify(child) for child in res[2:])
    if len(content) > 0:
        return '<{0} {1}>{2}</{0}>'.format(tag, attributes, content)
    else:
        return '<{0} {1}/>'.format(tag, attributes)
