import pytest
import json
from .. import render
from ..jsonml_stringify import jsonml_stringify
from pathlib import Path
from subprocess import run
from .render_report import render_report


@pytest.mark.parametrize('bits', [None, 32])
@pytest.mark.parametrize('lanes', [1, 2, 4])
@pytest.mark.parametrize('compact', [True, False])
@pytest.mark.parametrize('hflip', [True, False])
@pytest.mark.parametrize('vflip', [True, False])
@pytest.mark.parametrize('strokewidth', [1, 4])
@pytest.mark.parametrize('trim', [None, 8])
def test_render(request,
                output_dir,
                input_data,
                bits,
                lanes,
                compact,
                hflip,
                vflip,
                strokewidth,
                trim):
    res = render(input_data,
                 bits=bits,
                 lanes=lanes,
                 compact=compact,
                 hflip=hflip,
                 vflip=vflip,
                 strokewidth=strokewidth,
                 trim=trim)
    res[1]['data-bits'] = bits
    res[1]['data-lanes'] = lanes
    res[1]['data-compact'] = compact
    res[1]['data-hflip'] = hflip
    res[1]['data-vflip'] = vflip
    res[1]['data-strokewidth'] = strokewidth
    res[1]['data-trim'] = trim
    res = jsonml_stringify(res)

    output_filename = request.node.name
    output_filename += '.svg'

    (output_dir / output_filename).write_text(res)


@pytest.fixture
def input_data():
    return json.loads("""
[
  { "name": "IPO",   "bits": 8, "attr": "RO" },
  {                  "bits": 7 },
  { "name": "BRK",   "bits": 5, "attr": [ 9, "RO"], "type": 4 },
  { "name": "CPK",   "bits": 1 },
  { "name": "Clear", "bits": 3 },
  { "bits": 8 }
]
    """)


@pytest.fixture
def output_dir():
    git_describe = run(['git', 'describe', '--tags', '--match', 'v*'],
                       capture_output=True, check=True, text=True).stdout.strip()
    output_dir = Path(__file__).parent / f'output-{git_describe}'
    output_dir.mkdir(exist_ok=True)
    return output_dir

@pytest.fixture(scope='module', autouse=True)
def fixture_render_report():
    yield
    render_report()
