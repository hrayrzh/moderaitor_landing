import zipfile, re, sys, json, html
from xml.etree import ElementTree as ET
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def para_text(p):
    out = []
    for node in p.iter():
        tag = node.tag.split('}')[1]
        if tag == 't': out.append(node.text or '')
        elif tag == 'tab': out.append('\t')
        elif tag == 'br': out.append('\n')
    return ''.join(out)
def para_bold(p):
    runs = p.findall('.//w:r', NS)
    if not runs: return False
    b = 0; n = 0
    for r in runs:
        t = ''.join((x.text or '') for x in r.findall('w:t', NS))
        if not t.strip(): continue
        n += 1
        if r.find('w:rPr/w:b', NS) is not None: b += 1
    return n > 0 and b == n
z = zipfile.ZipFile(sys.argv[1]); root = ET.fromstring(z.read('word/document.xml'))
body = root.find('w:body', NS)
out = []
for el in body:
    tag = el.tag.split('}')[1]
    if tag == 'p':
        t = para_text(el).strip()
        if t: out.append({'type': 'p', 'text': t, 'bold': para_bold(el)})
    elif tag == 'tbl':
        rows = []
        for tr in el.findall('w:tr', NS):
            cells = []
            for tc in tr.findall('w:tc', NS):
                span = tc.find('w:tcPr/w:gridSpan', NS)
                paras = [{'text': para_text(p).strip(), 'bold': para_bold(p)} for p in tc.findall('w:p', NS)]
                paras = [p for p in paras if p['text']]
                cells.append({'span': int(span.get('{%s}val' % NS['w'])) if span is not None else 1, 'paras': paras})
            rows.append(cells)
        out.append({'type': 'table', 'rows': rows})
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
# summary
for i, b in enumerate(out):
    if b['type'] == 'p': print(i, 'P', ('B ' if b['bold'] else '  ') + b['text'][:90])
    else:
        print(i, 'TABLE rows=%d' % len(b['rows']), 'cell-counts=', sorted(set(len(r) for r in b['rows'])), 'spans=', sorted(set(c['span'] for r in b['rows'] for c in r)))
