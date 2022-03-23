A Python3 port of the javascript [bit-field library](https://github.com/drom/bitfield/) by [Aliaksei Chapyzhenka](https://github.com/drom).

## Install

```sh
pip install bit_field
```

To install this package with JSON5 support:

```sh
pip install bit_field[JSON5]
```

## Library usage

```python
from bit_field import render, jsonml_stringify

reg = [
  {'bits': 8, 'name': 'data'}
]

jsonml = render(reg, hspace=888)
html = jsonml_stringify(jsonml)
# <svg...>
```

## CLI Usage

```sh
bit_field [options] input > alpha.svg
```

### options

```
input        : input JSON filename - must be specified always
--input      : input JSON filename (kept for compatibility)
--compact    : compact rendering mode
--vspace     : vertical space - default 80
--hspace     : horizontal space - default 640
--lanes      : rectangle lanes - default 2
--bits       : overall bitwidth - default 32
--fontfamily : - default sans-serif
--fontweight : - default normal
--fontsize   : - default 14
--hflip      : horizontal flip
--vflip      : horizontal flip

--beautify   : use xml beautifier

--json5      : force json5 input format (need json5 python module)
--no-json5   : never use json5 input format
```

### alpha.json

```json
[
    { "name": "IPO",   "bits": 8, "attr": "RO" },
    {                  "bits": 7 },
    { "name": "BRK",   "bits": 5, "attr": "RW", "type": 4 },
    { "name": "CPK",   "bits": 1 },
    { "name": "Clear", "bits": 3 },
    { "bits": 8 }
]
```
### alpha.svg

![Heat Sink](https://raw.githubusercontent.com/Arth-ur/bitfield/master/bit_field/test/alpha.svg?sanitize=true)

### Licensing
This work is based on original work by [Aliaksei Chapyzhenka](https://github.com/drom) under the MIT license (see LICENSE-ORIGINAL).
