import re
trans = {
    '<o>': {'add': {'text-decoration': 'overline'}},
    '</o>': {'del': {'text-decoration': 'overline'}},
    '<ins>': {'add': {'text-decoration': 'underline'}},
    '</ins>': {'del': {'text-decoration': 'underline'}},
    '<s>': {'add': {'text-decoration': 'line-through'}},
    '</s>': {'del': {'text-decoration': 'line-through'}},
    '<b>': {'add': {'font-weight': 'bold'}},
    '</b>': {'del': {'font-weight': 'bold'}},
    '<i>': {'add': {'font-style': 'italic'}},
    '</i>': {'del': {'font-style': 'italic'}},
    '<sub>': {'add': {'baseline-shift': 'sub', 'font-size': '.7em'}},
    '</sub>': {'del': {'baseline-shift': 'sub', 'font-size': '.7em'}},
    '<sup>': {'add': {'baseline-shift': 'super', 'font-size': '.7em'}},
    '</sup>': {'del': {'baseline-shift': 'super', 'font-size': '.7em'}},
    '<tt>': {'add': {'font-family': 'monospace'}},
    '</tt>': {'del': {'font-family': 'monospace'}}
}
pattern = '|'.join(re.escape(k) for k in trans.keys())

def dump(state):
    att = {}
    for k, v in state.items():
        for kk, vv in v.items():
            if vv == True:
                att[k] = kk
    return att


def tspan(str):
    state = {
        'text-decoration': {},
        'font-weight': {},
        'font-style': {},
        'baseline-shift': {},
        'font-size': {},
        'font-family': {}
    }

    res = []

    while True:
        m = re.search(pattern, str, flags=re.IGNORECASE | re.UNICODE)
        if m is None:
            res.append(['tspan', dump(state), str])
            break
        if m.start(0) > 0:
            res.append(['tspan', dump(state), str[:m.start(0)]])
        tag = m.group(0)
        cmd = trans[tag]
        if 'add' in cmd:
            for k, v in cmd['add'].items():
                state[k][v] = True
        if 'del' in cmd:
            for k, v in cmd['del'].items():
                del state[k][v]
        str = str[m.end(0):]
        if len(str) == 0:
            break
    return res

if __name__ == '__main__':
    import sys
    print(tspan(''.join(sys.stdin.readlines())))
