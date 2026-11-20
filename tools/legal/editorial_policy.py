"""Convert the Armenian Model Comment Moderation Editorial Policy (text extracted
from the PDF with `pdftotext`) into the HTML body of editorial-policy.html.

The text is reproduced verbatim; only structure (headings, lists, glossary) is
added. Known quirks of the source (duplicate clause numbers, section 8 numbered
7.x) are kept as in the PDF.
"""
import re, html

esc = lambda s: html.escape(s, quote=False)

TOP_HEADINGS = [
    'Ներածություն',
    'Իրավական և Էթիկական համապատասխանություն',
    'Քաղաքականության նպատակները',
    'Համատեքստ',
    'Գործողության շրջանակը և կիրառելիությունը',
    'Քաղաքականություններ',
    'Տերմինների բառարան',
    'Հակապնդում',
]
DOT = '[.․]'  # ASCII dot or Armenian one-dot leader used in the PDF numbering
SECTION_RE = re.compile(r'^(\d)' + DOT + r'\s+(\S.*)$')
# a clause starts with its number followed by an uppercase Armenian letter, a quote or "moderAItor"
CLAUSE_RE = re.compile(r'^(\d+' + DOT + r'\d+(?:' + DOT + r'\d+)?)\s+((?:[Ա-Ֆ«]|moderAItor).*)$', re.S)
LOWER_ARM = re.compile(r'^[ա-և]')
LABEL_RE = re.compile(r'^(Նպատակը|Ընդգրկումը)\s+-\s+(.*)$', re.S)

GLOSSARY_TERMS = [
    'Ատելության խոսք',
    'Առցանց ատելության խոսք',
    'Անձնական տվյալներ',
    'Մոդերացիա (կանոնակարգում)',
    'Մոդերացիոն թիմ / մոդերատոր',
    'Ապօրինի բովանդակություն',
    'Կեղծ ինքնություն (ֆեյք)',
    'Խոցելի խումբ',
    'Վիրավորանք / Նվաստացում',
    'Ապամարդկայնացում (դեհումանիզացիա)',
    'Սպառնալիք, բռնության կոչ, ինքնասպանության, ցեղասպանության, ահաբեկչության հրահրում',
    'Կարծրատիպավորում',
    'Հետապնդում (բուլինգ)',
    'Ատելության հրահրում/ հիմնավորում/ արդարացում, իրավունքների ժխտում',
    'Բռնության կամ խտրականության արդարացում',
    'Անջատում, օտարում, բացառում',
    'Պիտակավորում',
    'Թաքնված ատելության խոսք',
    'Ապատեղեկատվություն, դավադրապաշտական տեսություն, վախի տարածում',
]

# Clause 1.1 lists its 11 categories without blank lines between items; split them explicitly.
CATEGORIES_1_1 = [
    'Վիրավորանք կամ նվաստացում (ատելության, խտրականության շարժառիթով)',
    'Ապամարդկայնացում (դեհումանիզացիա)',
    'Սպառնալիք, բռնության կոչ, ինքնասպանության, ցեղասպանության, ահաբեկչության հրահրում',
    'Կարծրատիպավորում (ատելության, խտրականության շարժառիթով)',
    'Հետապնդում (բուլինգ)',
    'Ատելության հրահրում և/կամ հիմնավորում/արդարացում, իրավունքների ժխտում',
    'Բռնության կամ խտրականության արդարացում',
    'Անջատում, օտարում, բացառում',
    'Պիտակավորում (ատելության, խտրականության շարժառիթով)',
    'Թաքնված (կոդավորված) ատելության խոսք',
    'Ապատեղեկատվություն, դավադրապաշտական տեսություն, վախի տարածում (եթե ուղեկցվում է ատելության խոսքով, խտրականության դրսևորումներով):',
]


def _starts_glossary_term(line):
    return any(line.startswith(t[:24]) for t in GLOSSARY_TERMS)


def blocks(text):
    """Split the extracted text into logical blocks. Headings, numbered clauses,
    labels, bullets and glossary terms start a new block even without a blank line."""
    out, buf = [], []
    prev_blank = True
    in_glossary = False

    def flush():
        nonlocal buf
        if buf:
            out.append(' '.join(buf))
            buf = []

    for raw in text.split('\n'):
        line = raw.replace('\f', '').strip()
        if not line or line.isdigit():      # blank line or page number
            prev_blank = prev_blank or not line
            if not line:
                prev_blank = True
            continue
        is_heading = line in TOP_HEADINGS
        starts = (prev_blank or is_heading or line == '●'
                  or bool(SECTION_RE.match(line)) or bool(CLAUSE_RE.match(line))
                  or bool(LABEL_RE.match(line))
                  or (in_glossary and _starts_glossary_term(line)))
        if starts:
            flush()
        buf.append(line)
        prev_blank = False
        if is_heading:
            flush()
            in_glossary = (line == 'Տերմինների բառարան')
    flush()
    return out


def build_body(text):
    paras = blocks(text)
    paras = paras[paras.index('Ներածություն'):]   # drop the cover page (rendered separately)

    out = []
    i = 0
    in_glossary = False
    bullet_pending = False
    ul_open = False
    section = '0'
    used_ids = set()

    def close_ul():
        nonlocal ul_open
        if ul_open:
            out.append('</ul>')
            ul_open = False

    while i < len(paras):
        p = paras[i]
        # a lowercase continuation right after a list item belongs to that item
        if ul_open and not bullet_pending and LOWER_ARM.match(p) and out[-1].startswith('<li>'):
            out[-1] = out[-1][:-5] + ' ' + esc(p) + '</li>'
            i += 1
            continue
        if p == '●':
            # a run of 11 bullets precedes the unsplit category list of clause 1.1
            run = 0
            while i + run < len(paras) and paras[i + run] == '●':
                run += 1
            if run >= 10:
                close_ul()
                out.append('<ul>' + ''.join(f'<li>{esc(c)}</li>' for c in CATEGORIES_1_1) + '</ul>')
                i += run + 1          # skip bullets and the following items block
                continue
            bullet_pending = True
            i += 1
            continue
        if bullet_pending:
            if not ul_open:
                out.append('<ul>')
                ul_open = True
            out.append(f'<li>{esc(p)}</li>')
            bullet_pending = False
            i += 1
            continue
        close_ul()
        if p in TOP_HEADINGS:
            in_glossary = (p == 'Տերմինների բառարան')
            slug = 'policy-' + str(TOP_HEADINGS.index(p) + 1)
            out.append(f'<h3 id="{slug}" class="mt-5 mb-3">{esc(p)}</h3>')
        elif SECTION_RE.match(p) and len(p) < 80:
            m = SECTION_RE.match(p)
            section = m.group(1)
            out.append(f'<h4 id="policy-s{section}" class="mt-4 mb-3">{section}. {esc(m.group(2))}</h4>')
        elif in_glossary and _starts_glossary_term(p):
            term = next(t for t in GLOSSARY_TERMS if p.startswith(t[:24]))
            m = re.match(re.escape(term) + r'\s*-\s*(.*)$', p, re.S)
            definition = m.group(1) if m else p[len(term):].lstrip(' -')
            out.append(f'<p><strong>{esc(term)}</strong> – {esc(definition)}</p>')
        elif CLAUSE_RE.match(p):
            m = CLAUSE_RE.match(p)
            num = m.group(1).replace('․', '.')
            cid = f'policy-s{section}-c{num.replace(".", "-")}'
            while cid in used_ids:          # the source repeats some clause numbers
                cid += 'b'
            used_ids.add(cid)
            out.append(f'<p id="{cid}"><strong>{num}</strong> {esc(m.group(2))}</p>')
        elif LABEL_RE.match(p):
            m = LABEL_RE.match(p)
            out.append(f'<p><strong>{esc(m.group(1))}</strong> – {esc(m.group(2))}</p>')
        else:
            out.append(f'<p>{esc(p)}</p>')
        i += 1
    close_ul()
    return '\n'.join(out)


CREDITS = '''<div class="policy-credits">
	<p>Այս քաղաքականությունը մշակվել է <a href="https://www.allrights.am/" target="_blank" rel="noopener noreferrer">Բոլորը հանուն հավասար իրավունքների հիմնադրամի</a> կողմից։</p>
	<p>Այս քաղաքականության մշակմանն աջակցել են <a href="https://mdi.am/" target="_blank" rel="noopener noreferrer">Բազմակողմանի տեղեկատվության ինստիտուտը</a> և <a href="https://www.mediaethics.am/" target="_blank" rel="noopener noreferrer">ԶԼՄ-ների էթիկայի Դիտորդ մարմինը</a>։</p>
	<p>Այս քաղաքականության իրականացմանը նպաստում է <a href="https://moderaitor.app/">moderAItor</a> գործիքը։</p>
	<p class="small text-muted">Սույն քաղաքականությունը մշակվել է Միացյալ Թագավորության միջազգային զարգացման աջակցության շրջանակներում՝ ՄԹ կառավարության ֆինանսավորմամբ իրականացվող «Ուժեղացնելով Արևելյան հարևանության դիմակայունությունը» ծրագրի ներքո, որը համակարգում է Պատերազմի և խաղաղության լուսաբանման ինստիտուտը (IWPR) և իրականացվում է «Բոլորը հանուն հավասար իրավունքների» հիմնադրամի և «Բազմակողմանի տեղեկատվության ինստիտուտ» ՀԿ-ի կողմից։ Փաստաթղթում արտահայտված տեսակետները/բովանդակությունը, պատկանում են հեղինակներին և պարտադիր չէ, որ արտացոլեն IWPR-ի կամ Միացյալ Թագավորության կառավարության (ՄԹ) պաշտոնական տեսակետները։</p>
</div>'''
