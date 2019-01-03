from .render import render
from .jsonml_stringify import jsonml_stringify
import re
import argparse
import json

parser = argparse.ArgumentParser('bitfield')

parser.add_argument(
    'input', help='input JSON filename - must be specified always')
parser.add_argument(
    '--input', help='(compatibility option)', action='store_true')
parser.add_argument('--vspace', help='vertical space', default=80)
parser.add_argument('--hspace', help='horizontal space', default=640)
parser.add_argument('--lanes', help='rectangle lanes', default=2)
parser.add_argument('--bits', help='overall bitwidth', default=32)
parser.add_argument('--bigendian', action='store_true')
parser.add_argument('--fontfamily', default='sans-serif')
parser.add_argument('--fontweight', default='normal')
parser.add_argument('--fontsize', default=14)
parser.add_argument('--beautify', action='store_true')


def beautify(res):
    import xml.dom.minidom
    xml = xml.dom.minidom.parseString(res)
    res = xml.toprettyxml()
    return res


if __name__ == '__main__':
    args = parser.parse_args()
    with open(args.input, 'r') as f:
        data = json.load(f)
        res = render(data,
                     hspace=args.hspace,
                     vspace=args.vspace,
                     lanes=args.lanes,
                     bits=args.bits,
                     bigendian=args.bigendian,
                     fontfamily=args.fontfamily,
                     fontweight=args.fontweight,
                     fontsize=args.fontsize)

    res = jsonml_stringify(res)
    if args.beautify:
        res = beautify(res)
    print(res)
