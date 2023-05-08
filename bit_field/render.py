from .tspan import tspan
import colorsys


def t(x, y):
    return 'translate({}, {})'.format(x, y)


def typeStyle(t):
    return ';fill:' + typeColor(t)


def typeColor(t):
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
        return 'rgb({:.0f}, {:.0f}, {:.0f})'.format(r * 255, g * 255, b * 255)
    else:
        return 'rgb({:.0f}, {:.0f}, {:.0f})'.format(229, 229, 229)


class Renderer(object):
    def __init__(self,
                 vspace=80,
                 hspace=640,
                 lanes=2,
                 bits=None,
                 fontsize=14,
                 fontfamily='sans-serif',
                 fontweight='normal',
                 compact=False,
                 hflip=False,
                 vflip=False,
                 strokewidth=1,
                 trim=None,
                 uneven=False,
                 legend=None):
        if vspace <= 19:
            raise ValueError(
                'vspace must be greater than 19, got {}.'.format(vspace))
        if hspace <= 39:
            raise ValueError(
                'hspace must be greater than 39, got {}.'.format(hspace))
        if lanes <= 0:
            raise ValueError(
                'lanes must be greater than 0, got {}.'.format(lanes))
        if bits is not None and bits <= 4:
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
        self.stroke_width = strokewidth
        self.trim_char_width = trim
        self.uneven = uneven
        self.legend = legend

    def get_total_bits(self, desc):
        return sum(e['bits'] for e in desc)

    def render(self, desc):
        self.bits = self.bits if self.bits is not None else self.get_total_bits(desc)

        mod = (self.bits + self.lanes - 1) // self.lanes
        self.mod = mod
        lsb = 0
        msb = self.bits - 1
        for e in desc:
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
            height = self.vspace * self.lanes  + self.stroke_width / 2
        else:
            self.vlane = self.vspace - self.fontsize * 1.2
            height = self.vlane * (self.lanes - 1) + self.vspace + self.stroke_width / 2
        if self.legend:
            height += self.fontsize * 1.2

        res = ['svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'width': self.hspace,
            'height': height,
            'viewbox': ' '.join(str(x) for x in [0, 0, self.hspace, height])
        }]

        if self.legend:
            res.append(self.legend_items())

        for i in range(0, self.lanes):
            if self.hflip:
                self.lane_index = i
            else:
                self.lane_index = self.lanes - i - 1
            self.index = i
            res.append(self.lane(desc))
        return res

    def legend_items(self):
        items = ['g', {'transform': t(0, self.stroke_width / 2)}]
        name_padding = 64
        square_padding = 20
        x = self.hspace / 2 - len(self.legend) / 2 * (square_padding + name_padding)
        for key, value in self.legend.items():
            items.append(['rect', {
                'x': x,
                'width': 12,
                'height': 12,
                'fill': typeColor(value),
                'style': 'stroke:#000; stroke-width:' + str(self.stroke_width) + ';' + typeStyle(value)
            }])
            x += square_padding
            items.append(['text', {
                'x': x,
                'font-size': self.fontsize,
                'font-family': self.fontfamily,
                'font-weight': self.fontweight,
                'y': self.fontsize / 1.2,
            }, key])
            x += name_padding
        return items

    def lane(self, desc):
        if self.compact:
            if self.index > 0:
                dy = (self.index - 1) * self.vlane + self.vspace
            else:
                dy = 0
        else:
            dy = self.index * self.vspace
        if self.legend:
            dy += self.fontsize * 1.2
        res = ['g', {
            'transform': t(0, dy)
        }]
        res.append(self.labels(desc))
        res.append(self.cage(desc))
        return res

    def cage(self, desc):
        if not self.compact or self.index == 0:
            dy = self.fontsize * 1.2
        else:
            dy = 0
        res = ['g', {
            'stroke': 'black',
            'stroke-width': self.stroke_width,
            'stroke-linecap': 'butt',
            'transform': t(0, dy)
        }]

        skip_count = 0
        if self.uneven and self.lanes > 1 and self.lane_index == self.lanes - 1:
            skip_count = self.mod - self.bits % self.mod
            if skip_count == self.mod:
                skip_count = 0

        hlen = (self.hspace / self.mod) * (self.mod - skip_count)
        hpos = 0 if self.vflip else (self.hspace / self.mod) * (skip_count)

        if not self.compact or self.hflip or self.lane_index == 0:
            res.append(self.hline(hlen, hpos, self.vlane))  # bottom
        if not self.compact or not self.hflip or self.lane_index == 0:
            res.append(self.hline(hlen, hpos))  # top

        hbit = (self.hspace - self.stroke_width) / self.mod
        for bit_pos in range(self.mod):
            bitm = (bit_pos if self.vflip else self.mod - bit_pos - 1)
            bit = self.lane_index * self.mod + bitm
            if bit >= self.bits:
                continue
            rpos = bit_pos + 1 if self.vflip else bit_pos
            lpos = bit_pos if self.vflip else bit_pos + 1
            if bitm + 1 == self.mod - skip_count:
                res.append(self.vline(self.vlane, rpos * hbit + self.stroke_width / 2))
            if bitm == 0:
                res.append(self.vline(self.vlane, lpos * hbit + self.stroke_width / 2))
            elif any(e['lsb'] == bit for e in desc):
                res.append(self.vline(self.vlane, lpos * hbit + self.stroke_width / 2))
            else:
                res.append(self.vline((self.vlane / 8),
                                      lpos * hbit + self.stroke_width / 2))
                res.append(self.vline((self.vlane / 8),
                                      lpos * hbit + self.stroke_width / 2, self.vlane * 7 / 8))

        return res

    def labels(self, desc):
        return ['g', {'text-anchor': 'middle'}, self.labelArr(desc)]

    def labelArr(self, desc):  # noqa: C901
        step = self.hspace / self.mod
        bits = ['g', {'transform': t(step / 2, self.fontsize)}]
        names = ['g', {'transform': t(step / 2, self.vlane / 2 + self.fontsize / 2)}]
        attrs = ['g', {'transform': t(step / 2, self.vlane + self.fontsize)}]
        blanks = ['g', {'transform': t(0, 0)}]

        for e in desc:
            lsbm = 0
            msbm = self.mod - 1
            lsb = self.lane_index * self.mod
            msb = (self.lane_index + 1) * self.mod - 1
            if e['lsb'] // self.mod == self.lane_index:
                lsbm = e['lsbm']
                lsb = e['lsb']
                if e['msb'] // self.mod == self.lane_index:
                    msb = e['msb']
                    msbm = e['msbm']
            else:
                if e['msb'] // self.mod == self.lane_index:
                    msb = e['msb']
                    msbm = e['msbm']
                elif not (lsb > e['lsb'] and msb < e['msb']):
                    continue
            msb_pos = msbm if self.vflip else (self.mod - msbm - 1)
            lsb_pos = lsbm if self.vflip else (self.mod - lsbm - 1)
            if not self.compact:
                bits.append(['text', {
                    'x': step * lsb_pos,
                    'font-size': self.fontsize,
                    'font-family': self.fontfamily,
                    'font-weight': self.fontweight
                }, str(lsb)])
                if lsbm != msbm:
                    bits.append(['text', {
                        'x': step * msb_pos,
                        'font-size': self.fontsize,
                        'font-family': self.fontfamily,
                        'font-weight': self.fontweight
                    }, str(msb)])
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
                available_space = step * (msbm - lsbm + 1)
                ltext = ['g', {
                    'transform': t(step * (msb_pos + lsb_pos) / 2, -6),
                }, ['text', ltextattrs] + tspan(self.trim_text(e['name'], available_space))]
                names.append(ltext)
            if 'name' not in e or e['type'] is not None:
                style = typeStyle(e['type'])
                blanks.append(['rect', {
                    'style': style,
                    'x': step * (lsb_pos if self.vflip else msb_pos),
                    'y': self.stroke_width / 2,
                    'width': step * (msbm - lsbm + 1),
                    'height': self.vlane - self.stroke_width / 2,
                    'fill': typeColor(e['type']),
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
                            bit_pos = lsb_pos + biti if self.vflip else (lsb_pos - biti)
                            atext += [['text', {
                                'x': step * bit_pos,
                                'font-size': self.fontsize,
                                'font-family': self.fontfamily,
                                'font-weight': self.fontweight,
                            }] + tspan(bit_text)]
                    else:
                        atext = [['text', {
                            'x': step * (msb_pos + lsb_pos) / 2,
                            'font-size': self.fontsize,
                            'font-family': self.fontfamily,
                            'font-weight': self.fontweight
                        }] + tspan(attribute)]
                    attrs.append(['g', {
                        'transform': t(0, i*self.fontsize)
                    }, *atext])
        if not self.compact or (self.index == 0):
            if self.compact:
                for i in range(self.mod):
                    bits.append(['text', {
                        'x': step * i,
                        'font-size': self.fontsize,
                        'font-family': self.fontfamily,
                        'font-weight': self.fontweight,
                    }, str(i if self.vflip else self.mod - i - 1)])
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
            att['x2'] = x + len
        if y != 0:
            att['y1'] = y
            att['y2'] = y
        res.append(att)
        return res

    def vline(self, len, x=None, y=None, stroke=None):
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
        if stroke:
            att['stroke'] = stroke
        res.append(att)
        return res

    def trim_text(self, text, available_space):
        if self.trim_char_width is None:
            return text
        text_width = len(text) * self.trim_char_width
        if text_width <= available_space:
            return text
        end = len(text) - int((text_width - available_space) / self.trim_char_width) - 3
        if end > 0:
            return text[:end] + '...'
        return text[:1] + '...'


def render(desc, **kwargs):
    renderer = Renderer(**kwargs)
    return renderer.render(desc)
