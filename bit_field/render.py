from .tspan import tspan


def t(x, y):
    return 'translate({}, {})'.format(x, y)


def typeStyle(t):
    styles = {
        '2': '0',
        '3': '80',
        '4': '170',
        '5': '45',
        '6': '126',
        '7': '215',
    }
    t = str(t)
    if t in styles:
        return ';fill:hsl(' + styles[t] + ',100%,50%)'
    else:
        return ''


class Renderer(object):
    def __init__(self,
                 vspace=80,
                 hspace=640,
                 lanes=2,
                 bits=32,
                 fontsize=14,
                 bigendian=False,
                 fontfamily='sans-serif',
                 fontweight='normal'):
        if vspace <= 19:
            raise ValueError(
                'vspace must be greater than 19, got {}.'.format(vspace))
        if hspace <= 39:
            raise ValueError(
                'hspace must be greater than 39, got {}.'.format(hspace))
        if lanes <= 0:
            raise ValueError(
                'lanes must be greater than 0, got {}.'.format(lanes))
        if bits <= 4:
            raise ValueError(
                'bits must be greater than 4, got {}.'.format(bits))
        if fontsize <= 5:
            raise ValueError(
                'fontsize must be greater than 5, got {}.'.format(fontsize))
        self.vspace = vspace
        self.hspace = hspace
        self.lanes = lanes
        self.bits = bits
        self.fontsize = fontsize
        self.bigendian = bigendian
        self.fontfamily = fontfamily
        self.fontweight = fontweight

    def render(self, desc):
        res = ['svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'width': self.hspace + 9,
            'height': self.vspace * self.lanes + 5,
            'viewbox': ' '.join(str(x) for x in [0, 0, self.hspace + 9, self.vspace * self.lanes + 5])
        }]

        lsb = 0
        mod = self.bits // self.lanes
        self.mod = mod

        for e in desc:
            e['lsb'] = lsb
            e['lsbm'] = lsb % mod
            lsb += e['bits']
            e['msb'] = lsb - 1
            e['msbm'] = e['msb'] % mod
            if 'type' not in e:
                e['type'] = None

        for i in range(0, self.lanes):
            self.index = i
            res.append(self.lane(desc))

        return res

    def lane(self, desc):
        res = ['g', {
            'transform': t(4.5, (self.lanes - self.index - 1) * self.vspace + 0.5)
        }]
        res.append(self.cage(desc))
        res.append(self.labels(desc))
        return res

    def cage(self, desc):
        res = ['g', {
            'stroke': 'black',
            'stroke-width': 1,
            'stroke-linecap': 'round',
            'transform': t(0, self.vspace / 4)
        }]
        res.append(self.hline(self.hspace))
        res.append(self.vline(self.vspace / 2))
        res.append(self.hline(self.hspace, 0, self.vspace / 2))

        i, j = self.index * self.mod, self.mod
        while True:
            if j == self.mod or any(e['lsb'] == i for e in desc):
                res.append(self.vline((self.vspace / 2),
                                      j * (self.hspace / self.mod)))
            else:
                res.append(self.vline((self.vspace / 16),
                                      j * (self.hspace / self.mod)))
                res.append(self.vline((self.vspace / 16),
                                      j * (self.hspace / self.mod)))
            i += 1
            j -= 1
            if j == 0:
                break

        return res

    def labels(self, desc):
        return ['g', {'text-anchor': 'middle'}, self.labelArr(desc)]

    def labelArr(self, desc):
        step = self.hspace / self.mod
        bits = ['g', {'transform': t(step / 2, self.vspace / 5)}]
        names = ['g', {'transform': t(step / 2, self.vspace / 2 + 4)}]
        attrs = ['g', {'transform': t(step / 2, self.vspace)}]
        blanks = ['g', {'transform': t(0, self.vspace / 4)}]

        for e in desc:
            lsbm = 0
            msbm = self.mod - 1
            lsb = self.index * self.mod
            msb = (self.index + 1) * self.mod - 1
            if e['lsb'] // self.mod == self.index:
                lsbm = e['lsbm']
                lsb = e['lsb']
                if e['msb'] // self.mod == self.index:
                    msb = e['msb']
                    msbm = e['msbm']
            else:
                if e['msb'] // self.mod == self.index:
                    msb = e['msb']
                    msbm = e['msbm']
                else:
                    continue
            bits.append(['text', {
                'x': step * (self.mod - lsbm - 1),
                'font-size': self.fontsize,
                'font-family': self.fontfamily,
                'font-weight': self.fontweight
            }, str(lsb)])
            if lsbm != msbm:
                bits.append(['text', {
                    'x': step * (self.mod - msbm - 1),
                    'font-size': self.fontsize,
                    'font-family': self.fontfamily,
                    'font-weight': self.fontweight
                }, str(msb)])
            if 'name' in e:
                ltext = ['text', {
                    'x': step * (self.mod - ((msbm + lsbm) / 2) - 1),
                    'font-size': self.fontsize,
                    'font-family': self.fontfamily,
                    'font-weight': self.fontweight
                }] + tspan(e['name'])
                names.append(ltext)
            if 'name' not in e or e['type'] is not None:
                style = ''.join(['fill-opacity:0.1', typeStyle(e['type'])])
                blanks.append(['rect', {
                    'style': style,
                    'x': step * (self.mod - msbm - 1),
                    'y': 0,
                    'width': step * (msbm - lsbm + 1),
                    'height': self.vspace / 2
                }])
            if 'attr' in e:
                atext = ['text', {
                    'x': step * (self.mod - ((msbm + lsbm) / 2) - 1),
                    'font-size': self.fontsize,
                    'font-family': self.fontfamily,
                    'font-weight': self.fontweight
                }] + tspan(e['attr'])
                attrs.append(atext)
        res = ['g', {}, blanks, bits, names, attrs]
        return res

    def hline(self, len, x=None, y=None):
        res = ['line']
        att = {}
        if x is not None:
            att['x1'] = x
            att['x2'] = len
        else:
            att['x2'] = len
        if y is not None:
            att['y1'] = y
            att['y2'] = y
        res.append(att)
        return res

    def vline(self, len, x=None, y=None):
        res = ['line']
        att = {}
        if x is not None:
            att['x1'] = x
            att['x2'] = x
        if y is not None:
            att['y1'] = y
            att['y2'] = y + len
        else:
            att['y2'] = len
        res.append(att)
        return res


def render(desc, **kwargs):
    renderer = Renderer(**kwargs)
    return renderer.render(desc)
