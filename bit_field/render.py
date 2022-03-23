from .tspan import tspan
import colorsys


def t(x, y):
    return 'translate({}, {})'.format(x, y)


def typeStyle(t):
    styles = {
        '2': 0,
        '3': 80,
        '4': 170,
        '5': 45,
        '6': 126,
        '7': 215,
    }
    t = str(t)
    if t in styles:
        r, g, b = colorsys.hls_to_rgb(styles[t] / 360, 0.9, 1)
        return ';fill:rgb({:.0f}, {:.0f}, {:.0f})'.format(r * 255, g * 255, b * 255)
    else:
        return ';fill:rgb({:.0f}, {:.0f}, {:.0f})'.format(229, 229, 229)


class Renderer(object):
    def __init__(self,
                 vspace=80,
                 hspace=640,
                 lanes=2,
                 bits=32,
                 fontsize=14,
                 fontfamily='sans-serif',
                 fontweight='normal',
                 compact=False,
                 hflip=True,
                 vflip=True):
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
        self.fontfamily = fontfamily
        self.fontweight = fontweight
        self.compact = compact
        self.hflip = hflip
        self.vflip = vflip

    def render(self, desc):
        res = ['svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'width': self.hspace,
            'height': self.vspace * self.lanes,
            'viewbox': ' '.join(str(x) for x in [0, 0, self.hspace, self.vspace * self.lanes])
        }]

        mod = self.bits // self.lanes
        self.mod = mod
        lsb = 0
        msb = self.bits - 1
        for e in desc:
            if self.vflip:
                e['msb'] = msb
                msb -= e['bits']
                e['lsb'] = msb + 1
            else:
                e['lsb'] = lsb
                lsb += e['bits']
                e['msb'] = lsb - 1
            e['lsbm'] = e['lsb'] % mod
            e['msbm'] = e['msb'] % mod
            if 'type' not in e:
                e['type'] = None

        max_attr_count = 0
        for e in desc:
            if 'attr' in e:
                if isinstance(e['attr'], list):
                    max_attr_count = max(max_attr_count, len(e['attr']))
                else:
                    max_attr_count = max(max_attr_count, 1)

        if not self.compact:
            self.vlane = self.vspace - self.fontsize * (1.2 + max_attr_count)
        else:
            self.vlane = self.vspace - self.fontsize * 1.2
        for i in range(0, self.lanes):
            if self.hflip != self.vflip:
                self.lane_index = self.lanes - i - 1
            else:
                self.lane_index = i
            self.index = i
            res.append(self.lane(desc))

        return res

    def lane(self, desc):
        dy = (self.lanes - self.lane_index - 1) * self.vspace
        if self.compact and self.lane_index != self.lanes - 1:
            dy -= (self.lanes - self.lane_index - 2) * (self.fontsize * 1.2)
        res = ['g', {
            'transform': t(0, dy)
        }]
        res.append(self.labels(desc))
        res.append(self.cage(desc))
        return res

    def cage(self, desc):
        stroke_width = 1
        if not self.compact or self.lane_index == self.lanes - 1:
            dy = self.fontsize * 1.2
        else:
            dy = 0
        res = ['g', {
            'stroke': 'black',
            'stroke-width': stroke_width,
            'stroke-linecap': 'round',
            'transform': t(0, dy)
        }]
        res.append(self.hline(self.hspace, padding=stroke_width/2))
        res.append(self.vline(self.vlane))
        res.append(self.hline(self.hspace, 0, self.vlane, padding=stroke_width/2))

        i, j = self.index * self.mod, self.mod
        hbit = (self.hspace - stroke_width/2) / self.mod
        while True:
            if j == self.mod or any(e['lsb'] == i for e in desc):
                res.append(self.vline(self.vlane,
                                      j * hbit))
            else:
                res.append(self.vline((self.vlane / 8),
                                      j * hbit))
                res.append(self.vline((self.vlane / 8),
                                      j * hbit, self.vlane * 7 / 8))
            i += 1
            j -= 1
            if j == 0:
                break

        return res

    def labels(self, desc):
        return ['g', {'text-anchor': 'middle'}, self.labelArr(desc)]

    def labelArr(self, desc):
        step = self.hspace / self.mod
        bits = ['g', {'transform': t(step / 2, self.fontsize)}]
        names = ['g', {'transform': t(step / 2, self.vlane / 2 + self.fontsize / 2)}]
        attrs = ['g', {'transform': t(step / 2, self.vlane + self.fontsize)}]
        blanks = ['g', {'transform': t(0, 0)}]

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
                elif not (lsb > e['lsb'] and msb < e['msb']):
                    continue
            if not self.compact:
                bits.append(['text', {
                    'x': step * (self.mod - lsbm - 1),
                    'font-size': self.fontsize,
                    'font-family': self.fontfamily,
                    'font-weight': self.fontweight
                }, str(self.bits - lsb - 1) if self.vflip else str(lsb)])
                if lsbm != msbm:
                    bits.append(['text', {
                        'x': step * (self.mod - msbm - 1),
                        'font-size': self.fontsize,
                        'font-family': self.fontfamily,
                        'font-weight': self.fontweight
                    }, str(self.bits - msb - 1) if self.vflip else str(msb)])
            if 'name' in e:
                ltextattrs = {
                    'font-size': self.fontsize,
                    'font-family': self.fontfamily,
                    'font-weight': self.fontweight,
                    'text-anchor': 'middle',
                    'y': 6
                }
                if 'rotate' in e:
                    ltextattrs['transform'] = ' rotate({})'.format(e['rotate'])
                if 'overline' in e and e['overline']:
                    ltextattrs['text-decoration'] = 'overline'
                ltext = ['g', {
                    'transform': t(step * (self.mod - ((msbm + lsbm) / 2) - 1), -6),
                }, ['text', ltextattrs] + tspan(e['name'])]
                names.append(ltext)
            if 'name' not in e or e['type'] is not None:
                style = typeStyle(e['type'])
                blanks.append(['rect', {
                    'style': style,
                    'x': step * (self.mod - msbm - 1),
                    'y': 0,
                    'width': step * (msbm - lsbm + 1),
                    'height': self.vlane
                }])
            if 'attr' in e and not self.compact:
                if isinstance(e['attr'], list):
                    e_attr = e['attr']
                else:
                    e_attr = [e['attr']]
                for i, attribute in enumerate(e_attr):
                    if isinstance(attribute, int):
                        atext = []
                        for biti in range(0, msb - lsb + 1):
                            if (1 << (biti + lsb - e['lsb'])) & attribute == 0:
                                bit_text = "0"
                            else:
                                bit_text = "1"
                            atext+=[['text', {
                                'x': step * (self.mod - lsbm - 1 - biti),
                                'font-size': self.fontsize,
                                'font-family': self.fontfamily,
                                'font-weight': self.fontweight,
                            }] + tspan(bit_text)]
                    else:
                        atext = [['text', {
                            'x': step * (self.mod - ((msbm + lsbm) / 2) - 1),
                            'font-size': self.fontsize,
                            'font-family': self.fontfamily,
                            'font-weight': self.fontweight
                        }] + tspan(attribute)]
                    attrs.append(['g', {
                        'transform': t(0, i*self.fontsize)
                    }, *atext])
        if not self.compact or self.lane_index == self.lanes - 1:
            if self.compact:
                for i in range(self.bits // self.lanes):
                    bits.append(['text', {
                        'x': step * (self.mod - i - 1),
                        'font-size': self.fontsize,
                        'font-family': self.fontfamily,
                        'font-weight': self.fontweight
                    }, str(self.bits // self.lanes - i - 1) if self.vflip else str(i)])
            res = ['g', {}, bits, ['g', {
                'transform': t(0, self.fontsize*1.2)
            }, blanks, names, attrs]]
        else:
            res = ['g', {}, blanks, names, attrs]
        return res

    def hline(self, len, x=0, y=0, padding=0):
        res = ['line']
        att = {}
        if padding != 0:
            len -= padding
            x += padding/2
        if x != 0:
            att['x1'] = x
        if len != 0:
            att['x2'] = len
        if y != 0:
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
