from .render import render
from .jsonml_stringify import jsonml_stringify
import argparse

def beautify(res):
    import xml.dom.minidom
    xml = xml.dom.minidom.parseString(res)
    res = xml.toprettyxml()
    return res

def bit_field_cli():
    parser = argparse.ArgumentParser('bitfield')

    parser.add_argument(
        'input', help='input JSON filename - must be specified always')
    parser.add_argument(
        '--input', help='(compatibility option)', action='store_true')
    parser.add_argument('--vspace', help='vertical space', default=80, type=int)
    parser.add_argument('--hspace', help='horizontal space', default=800, type=int)
    parser.add_argument('--lanes', help='rectangle lanes', default=1, type=int)
    parser.add_argument('--bits', help='overall bitwidth', default=32, type=int)
    parser.add_argument('--fontfamily', default='sans-serif')
    parser.add_argument('--fontweight', default='normal')
    parser.add_argument('--fontsize', default=14, type=int)
    parser.add_argument('--beautify', action='store_true')
    parser.add_argument('--json5', action='store_true')
    parser.add_argument('--no-json5', action='store_true')
    parser.add_argument('--compact', action='store_true')
    parser.add_argument('--hflip', help='horizontal flip', action='store_true')
    parser.add_argument('--vflip', help='vertical flip', action='store_true')
    args = parser.parse_args()

    # default is json5, unless forced with --(no-)json5
    if args.json5:
        import json5 as json
    elif args.no_json5:
        import json
    else:
        try:
            import json5 as json
        except ModuleNotFoundError:
            import json

    with open(args.input, 'r') as f:
        data = json.load(f)
        res = render(data,
                     hspace=args.hspace,
                     vspace=args.vspace,
                     lanes=args.lanes,
                     bits=args.bits,
                     fontfamily=args.fontfamily,
                     fontweight=args.fontweight,
                     fontsize=args.fontsize,
                     compact=args.compact,
                     hflip=args.hflip,
                     vflip=args.vflip)

    res = jsonml_stringify(res)
    if args.beautify:
        res = beautify(res)
    print(res)
