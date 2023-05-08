from pathlib import Path
import xml.etree.ElementTree as ET

def render_report():
    root = Path(__file__).parent
    output_file = root / f'output-compare.html'
    dirs = [dir for dir in root.glob('output-*') if dir.is_dir()]

    # dir -> [files...]
    tree = {}
    for dir in dirs:
        tree[dir] = []
        tree[dir].extend(file.name for file in dir.glob('*'))

    # file -> [dirs...]
    compare_tree = {}
    for dir, files in tree.items():
        for file in files:
            compare_list = [dir]
            for other_dir in tree:
                if other_dir == dir:
                    continue
                compare_list.append(other_dir)
                if file in tree[other_dir]:
                    tree[other_dir].remove(file)
            compare_tree[file] = sorted(compare_list)
        tree[dir] = []

    output_lines = ['<!DOCTYPE html>']
    output_lines += ['<head><title>Bitfield Render Compare</title></head>']
    output_lines += ['<body>']
    output_lines += [f'<h1>Bitfield Render Compare</h1>']
    for test_index, file in enumerate(compare_tree):
        output_lines += [f'<h2>Test {test_index+1}: {file}</h2>']
        output_lines += [f'<table>']
        header_lines = []
        content_lines = []
        data_lines = []
        for dir in compare_tree[file]:
            name = dir.name[len('output-'):]
            header_lines += [f'<th>{name}</th>']
            if (dir / file).exists():
                content_lines += [f'<td><a href="{(dir / file).relative_to(root)}">']
                content_lines += [f'<img src="{(dir / file).relative_to(root)}"/>']
                content_lines += [f'</a></td>']
                data = {key[len('data-'):]: value for key, value in ET.parse(dir/file).getroot().attrib.items() if key.startswith('data-')}
                data_lines += [f'<td><p>']
                for key, value in data.items():
                    data_lines += [f'<b><tt>{key}</tt></b>']
                    data_lines += [f'<tt>{value}</tt>']
                data_lines += [f'</p></td>']
            else:
                content_lines += [f'<td>(N/A)</td>']
                data_lines += [f'<td></td>']
            
        output_lines += [f'<tr>'] + header_lines + [f'</tr>']
        output_lines += [f'<tr>'] + content_lines + [f'</tr>']
        output_lines += [f'<tr>'] + data_lines + [f'</tr>']
        output_lines += [f'</table>']
    output_lines += ['</body>']

    output_file.write_text('\n'.join(output_lines))

if __name__ == '__main__':
    render_report()
