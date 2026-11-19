#!/usr/bin/env python3
"""Generate msa.html, msa-v1.0.html and order-form.html for the moderAItor landing."""
import json, re, html, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.join(HERE, 'data')  # extracted DOCX tables (see README)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(HERE))

VERSION = '1.0'
EFFECTIVE_EN = '20 November 2026'
EFFECTIVE_HY = '2026 թ. նոյեմբերի 20'
MSA_DOCX = 'assets/docs/moderAItor_MSA_v1.0_AM-EN.docx'
ORDER_DOCX = 'assets/docs/moderAItor_Order_Form_v1.0_AM-EN.docx'

ARM = re.compile(r'[԰-֏]')
esc = lambda s: html.escape(s, quote=False)


APPENDIX_PAGES = {1: 'order-form.html', 2: 'terms.html', 3: 'privacy.html', 4: 'data-deletion.html', 5: 'editorial-policy.html'}


def _outside_anchors(s, fn):
    """Apply fn to the parts of s that are not already inside an <a> element."""
    parts = re.split(r'(<a [^>]*>.*?</a>)', s)
    return ''.join(p if p.startswith('<a ') else fn(p) for p in parts)


def _clause_anchor(num, base):
    return f'{base}#clause-{num.replace(".", "-").rstrip("-")}'


def linkify(s, lang, msa_base='', section_base=None):
    """Turn references to appendices, clauses and sections into links.
    msa_base is '' on the MSA page itself and 'msa.html' on other pages.
    section_base is where "Section N" points (defaults to the MSA sections)."""
    if section_base is None:
        section_base = f'{msa_base}#section-'

    def L(href, text):
        return f'<a href="{href}">{text}</a>'

    def clause_list(m, lead, sep_re):
        nums = m.group(2)
        linked = re.sub(r'\d+(?:\.\d+)+', lambda n: L(_clause_anchor(n.group(0), msa_base), n.group(0)), nums)
        return m.group(1) + linked

    def sub(p):
        # "MSA 9.1.1" / "MSA-ի 9.1.1" / "MSA 3.2(E)" in both languages
        if msa_base:
            p = re.sub(r'(MSA(?:-\w+)?)(\s)(\d+(?:\.\d+)+)',
                       lambda m: L(msa_base, m.group(1)) + m.group(2) + L(_clause_anchor(m.group(3), msa_base), m.group(3)), p)
        if lang == 'en':
            p = re.sub(r'Model Comment Moderation Editorial Policy', lambda m: L(APPENDIX_PAGES[5], m.group(0)), p)
            p = re.sub(r'Privacy Policy', lambda m: L(APPENDIX_PAGES[3], m.group(0)), p)
            p = re.sub(r'Terms of Service', lambda m: L(APPENDIX_PAGES[2], m.group(0)), p)
            p = re.sub(r'Data Deletion Policy', lambda m: L(APPENDIX_PAGES[4], m.group(0)), p)
            p = re.sub(r'Order Form', lambda m: L(APPENDIX_PAGES[1], m.group(0)), p)
            p = re.sub(r'Appendix ([1-5])\b', lambda m: L(APPENDIX_PAGES[int(m.group(1))], m.group(0)), p)
            # Clause 1.6 / Clauses 4.2–4.4 / Clauses 1.6 and 2.4 / Clause 3.2(D)
            p = re.sub(r'(Clauses?\s)((?:\d+(?:\.\d+)+(?:\([A-Z]\))?)(?:(?:,\s|\sand\s|\sor\s|–|-)\d+(?:\.\d+)+(?:\([A-Z]\))?)*)',
                       lambda m: clause_list(m, None, None), p)
            # Section 16 / Sections 4 and 11 / Sections 8, 10, 12 and 15
            p = re.sub(r'(Sections?\s)((?:\d+)(?:(?:,\s|\sand\s)\d+)*)',
                       lambda m: m.group(1) + re.sub(r'\d+', lambda n: L(f'{section_base}{n.group(0)}', n.group(0)), m.group(2)), p)
            if msa_base:
                p = _outside_anchors(p, lambda q: re.sub(r'\bMSA\b', lambda m: L(msa_base, m.group(0)), q))
                p = _outside_anchors(p, lambda q: re.sub(r'Master Service Agreement', lambda m: L(msa_base, m.group(0)), q))
        else:
            W = r'[Ա-Ֆա-և]*'
            p = re.sub(r'Մեկնաբանությունների մոդերացիայի օրինակելի խմբագրական քաղաքականությ' + W, lambda m: L(APPENDIX_PAGES[5], m.group(0)), p)
            p = re.sub(r'Գաղտնիության քաղաքականությ' + W, lambda m: L(APPENDIX_PAGES[3], m.group(0)), p)
            p = re.sub(r'Ծառայությունների մատուցման պայմաններ' + W, lambda m: L(APPENDIX_PAGES[2], m.group(0)), p)
            p = re.sub(r'Տվյալների ոչնչացման քաղաքականությ' + W, lambda m: L(APPENDIX_PAGES[4], m.group(0)), p)
            p = re.sub(r'Պատվերի ձև' + W, lambda m: L(APPENDIX_PAGES[1], m.group(0)), p)
            p = re.sub(r'Հավելված ([1-5])(-\w+)?', lambda m: L(APPENDIX_PAGES[int(m.group(1))], m.group(0)), p)
            # 1.6 կետով / 4.2 և 4.3 կետերով / 3.2 կետի «Դ» ենթակետով
            p = re.sub(r'(\d+(?:\.\d+)+)(?=(?:(?:,\s|\sև\s|\sկամ\s|–|-)\d+(?:\.\d+)+)*\s(?:կետ|ենթակետ))',
                       lambda m: L(_clause_anchor(m.group(1), msa_base), m.group(1)), p)
            # 16-րդ գլխով / 4-րդ և 11-րդ գլուխների
            p = re.sub(r'(\d+)(-րդ)(?=(?:\sև\s\d+-րդ)*\sգլ)', lambda m: L(f'{msa_base}#section-{m.group(1)}', m.group(1) + m.group(2)), p)
            if section_base != f'{msa_base}#section-':
                p = re.sub(r'(\d+)(-րդ)(?=\sբաժ)', lambda m: L(f'{section_base}{m.group(1)}', m.group(1) + m.group(2)), p)
            if msa_base:
                p = _outside_anchors(p, lambda q: re.sub(r'MSA(-\w+)?', lambda m: L(msa_base, m.group(0)), q))
        return p
    return _outside_anchors(s, sub)


def para_html(text, lang='en', msa_base=''):
    """Escape, bold leading clause numbers, link references, keep line breaks."""
    lines = [esc(l.strip()) for l in text.split('\n') if l.strip()]
    out = []
    for l in lines:
        l = re.sub(r'^(\d+(?:\.\d+)+\.)\s', r'<strong>\1</strong> ', l)
        l = re.sub(r'(https?://[^\s<)]+?)(?=[.,;։]?(?:\s|$|<|\)))', lambda m: f'<a href="{m.group(1).replace("https://moderaitor.app/", "")}">{m.group(1)}</a>', l)
        l = linkify(l, lang, msa_base)
        out.append(l)
    return '<br>'.join(out)


# ---------------------------------------------------------------- template
NAV = '''			<!-- ***** Header Start ***** -->
			<header id="header">
				<!-- Navbar -->
				<nav data-aos="zoom-out" data-aos-delay="800" class="navbar gameon-navbar navbar-expand">
					<div class="container header">

						<!-- Logo -->
						<a class="navbar-brand" href="index.html">
							<img src="assets/img/logo/logo.png" alt="Brand Logo" />
						</a>

						<div class="ms-auto"></div>

						<!-- Navbar Nav -->
						<ul class="navbar-nav items mx-auto">
							<li class="nav-item">
								<a class="nav-link" href="index.html">Home</a>
							</li>
							<li class="nav-item">
								<a class="nav-link" href="index.html#features">Features</a>
							</li>
							<li class="nav-item">
								<a class="nav-link" href="index.html#how-it-works">How it Works</a>
							</li>
							<li class="nav-item">
								<a class="nav-link" href="index.html#faq">FAQ</a>
							</li>
							<li class="nav-item">
								<a class="nav-link" href="index.html#contact">Contact</a>
							</li>
							<!-- Legal links - visible only in mobile menu -->
							<li class="nav-item d-none">
								<a class="nav-link" href="msa.html">Master Service Agreement</a>
							</li>
							<li class="nav-item d-none">
								<a class="nav-link" href="privacy.html">Privacy Policy</a>
							</li>
							<li class="nav-item d-none">
								<a class="nav-link" href="terms.html">Terms of Service</a>
							</li>
							<li class="nav-item d-none">
								<a class="nav-link" href="data-deletion.html">Data Deletion</a>
							</li>
						</ul>

						<!-- Navbar Toggler -->
						<ul class="navbar-nav toggle">
							<li class="nav-item">
								<a href="#" class="nav-link" data-bs-toggle="modal" data-bs-target="#menu">
									<i class="icon-menu m-0"></i>
								</a>
							</li>
						</ul>

					</div>
				</nav>
			</header>
			<!-- ***** Header End ***** -->
'''

FOOTER = '''			<!--====== Footer Area Start ======-->
			<footer class="footer-area primary-bg p-0">
				<!-- Footer Top -->
				<div class="footer-top">
					<div class="container">
						<div class="row items">
							<div class="col-12 col-sm-6 col-lg-4 item">
								<!-- Footer Items -->
								<div class="footer-items">
									<!-- Logo -->
									<a class="navbar-brand" href="index.html">
										<img class="logo" src="assets/img/logo/logo.png" alt="">
									</a>
									<p class="slug mt-3">AI-powered hate speech detection and content moderation tool for media organizations and civil society.</p>

									<hr>

									<!-- Social Icons -->
									<div class="social-icons d-flex mt-3">
										<a class="icon has-overlay overlay-gradient" href="#" aria-label="Social media link">
											<i class="fa-brands fa-facebook-f"></i>
											<i class="fa-brands fa-facebook-f"></i>
										</a>
										<a class="icon has-overlay overlay-gradient" href="#" aria-label="Social media link">
											<i class="fa-brands fa-x-twitter"></i>
											<i class="fa-brands fa-x-twitter"></i>
										</a>
										<a class="icon has-overlay overlay-gradient" href="#" aria-label="Social media link">
											<i class="fa-brands fa-linkedin-in"></i>
											<i class="fa-brands fa-linkedin-in"></i>
										</a>
										<a class="icon has-overlay overlay-gradient" href="#" aria-label="Social media link">
											<i class="fa-brands fa-github"></i>
											<i class="fa-brands fa-github"></i>
										</a>
									</div>
								</div>
							</div>
							<div class="col-12 col-sm-6 col-lg-4 item">
								<!-- Footer Items -->
								<div class="footer-items">
									<h4 class="footer-title mt-0">Useful Links</h4>

									<!-- Navigation -->
									<ul class="nav flex-column" role="list">
										<li class="nav-item">
											<a class="nav-link" href="index.html">Home</a>
										</li>
										<li class="nav-item">
											<a class="nav-link" href="index.html#features">Features</a>
										</li>
										<li class="nav-item">
											<a class="nav-link" href="index.html#how-it-works">How it Works</a>
										</li>
										<li class="nav-item">
											<a class="nav-link" href="index.html#faq">FAQ</a>
										</li>
										<li class="nav-item">
											<a class="nav-link" href="index.html#contact">Contact</a>
										</li>
									</ul>
								</div>
							</div>
							<div class="col-12 col-sm-6 col-lg-4 item">
								<!-- Footer Items -->
								<div class="footer-items">
									<h4 class="footer-title mt-0">Legal</h4>

									<!-- Navigation -->
									<ul class="nav flex-column" role="list">
										<li class="nav-item">
											<a class="nav-link" href="msa.html">Master Service Agreement</a>
										</li>
										<li class="nav-item">
											<a class="nav-link" href="order-form.html">Appendix 1: Order Form</a>
										</li>
										<li class="nav-item">
											<a class="nav-link" href="terms.html">Appendix 2: Terms of Service</a>
										</li>
										<li class="nav-item">
											<a class="nav-link" href="privacy.html">Appendix 3: Privacy Policy</a>
										</li>
										<li class="nav-item">
											<a class="nav-link" href="data-deletion.html">Appendix 4: Data Deletion Policy</a>
										</li>
										<li class="nav-item">
											<a class="nav-link" href="editorial-policy.html">Appendix 5: Editorial Policy</a>
										</li>
									</ul>
								</div>
							</div>
						</div>
					</div>
				</div>
				<!-- Footer Bottom -->
				<div class="footer-bottom">
					<div class="container">
						<div class="row">
							<div class="col-12">
								<!-- Copyright Area -->
								<div class="copyright-area d-flex flex-wrap justify-content-center justify-content-sm-between align-items-center text-center py-4">
									<span>&copy; <span id="footer-year"></span> moderAItor | Powered by <a href="https://mdi.am/" target="_blank" rel="noopener noreferrer">Media Diversity Institute</a></span>
									<span>Operated by Media Diversity Institute</span>
								</div>
							</div>
						</div>
					</div>
				</div>
			</footer>
			<!--====== Footer Area End ======-->

			<!--====== Modal Responsive Menu Area Start ======-->
			<div id="menu" class="modal fade p-0">
				<div class="modal-dialog modal-dialog-slideout">
					<div class="modal-content full">
						<div class="modal-header" data-bs-dismiss="modal">
							Menu <i class="icon-close"></i>
						</div>
						<div class="menu modal-body">
							<div class="items p-0 text-center">
								<!-- Append [navbar] -->
							</div>
						</div>
					</div>
				</div>
			</div>
			<!--====== Modal Responsive Menu Area End ======-->

			<!--====== Scroll To Top Area Start ======-->
			<div id="scroll-to-top" class="scroll-to-top">
				<a href="#home" class="smooth-anchor">
					<i class="fa-solid fa-arrow-up"></i>
				</a>
			</div>
			<!--====== Scroll To Top Area End ======-->
		</div>


		<!-- ***** All jQuery Plugins ***** -->

		<!-- jQuery(necessary for all JavaScript plugins) -->
		<script src="assets/js/vendor/jquery.min.js"></script>

		<!-- Bootstrap js -->
		<script src="assets/js/vendor/popper.min.js"></script>
		<script src="assets/js/vendor/bootstrap.min.js"></script>

		<!-- Plugins js -->
		<script src="assets/js/vendor/slider.min.js"></script>
		<script src="assets/js/vendor/owl.carousel.min.js"></script>
		<script src="assets/js/vendor/counterup.js"></script>
		<script src="assets/js/vendor/waypoint.js"></script>
		<script src="assets/js/vendor/aos.js"></script>
		<script src="assets/js/vendor/wow.min.js"></script>
		<script src="assets/js/vendor/countdown.min.js"></script>
		<script src="assets/js/vendor/gallery.min.js"></script>

		<!-- Main js -->
		<script src="assets/js/main.js"></script>
		<script>document.getElementById('footer-year').textContent = new Date().getFullYear();</script>
'''

LANG_SCRIPT = '''		<script>
		(function () {
			var body = document.body;
			var buttons = document.querySelectorAll('.lang-toggle button');
			function apply(mode) {
				body.classList.remove('lang-hy', 'lang-en');
				if (mode === 'hy' || mode === 'en') { body.classList.add('lang-' + mode); }
				buttons.forEach(function (b) { b.classList.toggle('active', b.getAttribute('data-lang') === mode); });
				try { localStorage.setItem('legal-lang', mode); } catch (e) {}
			}
			buttons.forEach(function (b) { b.addEventListener('click', function () { apply(b.getAttribute('data-lang')); }); });
			var saved = 'both';
			try { saved = localStorage.getItem('legal-lang') || 'both'; } catch (e) {}
			apply(saved);
		})();
		</script>
'''


def page(*, file, title, description, h1, crumb, body_html, extra_head='', extra_script='', noindex=False):
    robots = 'noindex, follow' if noindex else 'index, follow'
    canonical = 'https://moderaitor.app/msa.html' if file.startswith('msa') else 'https://moderaitor.app/' + file
    return f'''<!doctype html>
<html class="no-js" lang="en">

<head>
	<meta charset="UTF-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

	<!-- Title  -->
	<title>{esc(title)}</title>

	<!-- Meta Description -->
	<meta name="description" content="{esc(description)}">

	<!-- Author & Robots -->
	<meta name="author" content="moderAItor">
	<meta name="robots" content="{robots}">

	<!-- Canonical URL -->
	<link rel="canonical" href="{canonical}">

	<!-- Open Graph -->
	<meta property="og:type" content="article">
	<meta property="og:url" content="https://moderaitor.app/{file}">
	<meta property="og:title" content="{esc(title)}">
	<meta property="og:description" content="{esc(description)}">
	<meta property="og:site_name" content="moderAItor">

	<!-- Twitter Card -->
	<meta name="twitter:card" content="summary">
	<meta name="twitter:title" content="{esc(title)}">
	<meta name="twitter:description" content="{esc(description)}">

	<!-- Favicon  -->
	<link rel="icon" href="assets/img/favicon.ico">
	<link rel="apple-touch-icon" sizes="180x180" href="assets/img/logo/logo.png">

	<!-- ***** All CSS Files ***** -->

	<!-- Style css -->
	<link rel="stylesheet" href="assets/css/style.css">
	<link rel="stylesheet" href="assets/css/legal.css">
{extra_head}
</head>

<body>
	<div class="main">
		<!-- ***** Preloader Start ***** -->
		<div class="preloader-main">
			<div class="preloader-wapper">
				<div class="preloader-logo-wrapper">
					<img src="assets/img/logo/logo.png" alt="moderAItor" class="preloader-logo">
				</div>
				<div>
					<div class="loader-section section-left"></div>
					<div class="loader-section section-right"></div>
				</div>
			</div>
		</div>
		<!-- ***** Preloader End ***** -->

{NAV}
		<!-- ***** Breadcrumb Area Start ***** -->
		<section id="home" class="breadcrumb-area has-overlay overlay-gradient d-flex align-items-center">
			<div class="container">
				<div class="row">
					<div class="col-12">
						<!-- Breamcrumb Content -->
						<div class="breadcrumb-content text-center">
							<h2 class="text-white">{esc(h1)}</h2>
							<ol class="breadcrumb d-flex justify-content-center">
								<li class="breadcrumb-item"><a class="text-white" href="index.html">Home</a></li>
								<li class="breadcrumb-item text-white active">{esc(crumb)}</li>
							</ol>
						</div>
					</div>
				</div>
			</div>
		</section>
		<!-- ***** Breadcrumb Area End ***** -->

		<!-- ***** Content Area Start ***** -->
		<section class="content-section">
			<div class="container">
				<div class="row justify-content-center">
					<div class="col-12 col-md-11 col-lg-10">
						<div class="content-wrapper">
{body_html}
						</div>
					</div>
				</div>
			</div>
		</section>
		<!-- ***** Content Area End ***** -->

{FOOTER}{extra_script}</body>

</html>
'''


# ---------------------------------------------------------------- MSA
def build_msa(archived):
    rows = json.load(open(os.path.join(SCRATCH, 'msa.json')))[0]['rows']
    out = []
    toc = []
    sec_re = re.compile(r'^(\d+)\.\s+\S')
    for i, r in enumerate(rows):
        hy, en = r[0]['paras'], r[1]['paras']
        if i == 0:
            continue  # column headers (ՀԱՅԵՐԵՆ / ENGLISH)
        en_text = en[0]['text'] if en else ''
        cls = 'bi-row'
        wrap = ('', '')
        attrs = ''
        if i == 1:
            cls += ' bi-title'; wrap = ('<h2>', '</h2>')
        elif i == 2:
            cls += ' bi-meta'
        elif en and en[0]['bold'] and sec_re.match(en_text) and not re.match(r'^\d+\.\d', en_text):
            n = sec_re.match(en_text).group(1)
            cls += ' bi-section'; wrap = ('<h3>', '</h3>'); attrs = f' id="section-{n}"'
            toc.append((n, en_text, hy[0]['text'] if hy else ''))
        elif re.match(r'^[A-Za-zԱ-Ֆա-և]\)\s', en_text) or re.match(r'^[Ա-Ֆա-ևa-zA-Z]\)\s', hy[0]['text'] if hy else ''):
            cls += ' bi-sub'
        elif re.match(r'^\d+\.\d+\.\d+\.', en_text):
            cls += ' bi-sub'

        # anchor for every numbered clause (1.6 -> clause-1-6, 5.1.1 -> clause-5-1-1)
        cm = re.match(r'^(\d+(?:\.\d+)+)\.', en_text)
        if cm and not attrs:
            attrs = f' id="clause-{cm.group(1).replace(".", "-")}"'

        def cell(paras, lang):
            if wrap[0]:
                inner = wrap[0] + esc(paras[0]['text']) + wrap[1] if paras else ''
            else:
                inner = ''.join(
                    ('<p><strong>%s</strong></p>' % para_html(p['text'], lang)) if p['bold'] else ('<p>%s</p>' % para_html(p['text'], lang))
                    for p in paras)
            return f'<div class="bi-cell {lang}" lang="{lang}">{inner}</div>'

        out.append(f'<div class="{cls}"{attrs}>{cell(hy, "hy")}{cell(en, "en")}</div>')

    toc_html = '<ol class="legal-toc">' + ''.join(
        f'<li><a href="#section-{n}">{esc(re.sub(r"^\d+\.\s+", "", e).title() if e.isupper() else e)}</a><small lang="hy">{esc(re.sub(r"^\d+\.\s+", "", h))}</small></li>'
        for n, e, h in toc) + '</ol>'

    if archived:
        banner = f'''<div class="archived-banner">
	<p><strong>Archived copy.</strong> You are viewing version {VERSION} of the Master Service Agreement, effective from {EFFECTIVE_EN}. This is the current version. The latest version is always published at <a href="msa.html">moderaitor.app/msa.html</a>.</p>
	<p lang="hy" class="mt-2"><strong>Արխիվային օրինակ.</strong> Դուք դիտում եք Հիմնական պայմանագրի {VERSION} խմբագրությունը, որը գործում է {EFFECTIVE_HY}-ից։ Գործող խմբագրությունը միշտ հրապարակվում է <a href="msa.html">moderaitor.app/msa.html</a> հասցեում։</p>
</div>'''
    else:
        banner = ''

    meta = f'''<div class="legal-meta">
	<span class="legal-badge">Master Service Agreement · Public Offer</span>
	<dl>
		<dt>Document</dt><dd>"moderAItor" Artificial Intelligence Moderation Tool Master Service Agreement (MSA)<br><span lang="hy">«moderAItor» ԱԲ մոդերացիոն գործիքի ծառայությունների մատուցման հիմնական պայմանագիր</span></dd>
		<dt>Version</dt><dd>{VERSION}</dd>
		<dt>Effective from</dt><dd>{EFFECTIVE_EN} · <span lang="hy">{EFFECTIVE_HY}</span></dd>
		<dt>Status</dt><dd>Current version</dd>
		<dt>Languages</dt><dd>Armenian and English. In case of discrepancy, the Armenian text prevails (Clause 17.2).</dd>
	</dl>
	<p>The Appendices form an integral part of this Agreement: <a href="order-form.html">Appendix 1 – Order Form</a>, <a href="terms.html">Appendix 2 – Terms of Service</a>, <a href="privacy.html">Appendix 3 – Privacy Policy</a>, <a href="data-deletion.html">Appendix 4 – Data Deletion Policy</a>, <a href="editorial-policy.html">Appendix 5 – Model Comment Moderation Editorial Policy</a>. Previous versions: see <a href="#version-history">Version history</a>.</p>
	<div class="legal-actions">
		<a class="btn btn-bordered swap-icon" href="{MSA_DOCX}" download><i class="fa-solid fa-file-word"></i>Download DOCX (AM/EN)</a>
		<a class="btn btn-bordered swap-icon" href="order-form.html"><i class="fa-solid fa-file-signature"></i>Order Form</a>
	</div>
</div>'''

    toggle = '''<div class="lang-toggle" role="group" aria-label="Document language">
	<span>Show:</span>
	<button type="button" data-lang="both" class="active">Հայերեն + English</button>
	<button type="button" data-lang="hy" lang="hy">Հայերեն</button>
	<button type="button" data-lang="en">English</button>
</div>'''

    history = f'''<h3 id="version-history" class="mt-5 mb-3">Version history · <span lang="hy">Խմբագրությունների պատմություն</span></h3>
<table class="version-table">
	<thead><tr><th>Version</th><th>Effective from</th><th>Status</th><th>Changes</th><th>Permanent link</th></tr></thead>
	<tbody>
		<tr><td>{VERSION}</td><td>{EFFECTIVE_EN}</td><td>Current</td><td>Initial version of the public offer.</td><td><a href="msa-v{VERSION}.html">msa-v{VERSION}.html</a> · <a href="{MSA_DOCX}" download>DOCX</a></td></tr>
	</tbody>
</table>
<p class="text-muted small">Each version of the Agreement remains available at its permanent link after an update. Amendments are notified and enter into force in accordance with Section 16 of the Agreement.</p>'''

    body = '\n'.join([banner, meta, toggle, toc_html, '<div class="bi">', *out, '</div>', history])
    return body


msa_body = build_msa(archived=False)
open(os.path.join(OUT, 'msa.html'), 'w').write(page(
    file='msa.html',
    title='Master Service Agreement (Public Offer) - moderAItor',
    description=f'moderAItor Master Service Agreement (MSA), public offer, version {VERSION}, effective from {EFFECTIVE_EN}. Armenian and English text with all appendices.',
    h1='Master Service Agreement', crumb='Master Service Agreement',
    body_html=msa_body, extra_script=LANG_SCRIPT))

open(os.path.join(OUT, f'msa-v{VERSION}.html'), 'w').write(page(
    file=f'msa-v{VERSION}.html',
    title=f'Master Service Agreement v{VERSION} (archived copy) - moderAItor',
    description=f'Archived copy of the moderAItor Master Service Agreement version {VERSION}, effective from {EFFECTIVE_EN}.',
    h1=f'Master Service Agreement · Version {VERSION}', crumb=f'MSA v{VERSION}',
    body_html=build_msa(archived=True), extra_script=LANG_SCRIPT, noindex=True))


# ---------------------------------------------------------------- Order form
def split_langs(text):
    """Split a paragraph into HY / EN parts where both are present on separate lines."""
    parts = [l.strip() for l in text.split('\n') if l.strip()]
    hy = [p for p in parts if ARM.search(p)]
    en = [p for p in parts if not ARM.search(p)]
    return hy, en


def paras_html(paras):
    out = []
    for p in paras:
        for line in [l for l in p['text'].split('\n') if l.strip()]:
            lang = 'hy' if ARM.search(line) else 'en'
            t = esc(line.strip())
            t = re.sub(r'(https?://[^\s<)]+?)(?=[.,;։]?(?:\s|$|<|\)))', lambda m: f'<a href="{m.group(1).replace("https://moderaitor.app/", "")}">{m.group(1)}</a>', t)
            t = linkify(t, lang, 'msa.html', section_base='#order-section-')
            t = t.replace('☐', '<span class="check">☐</span>')
            if p['bold']:
                t = f'<strong>{t}</strong>'
            out.append(f'<p class="{lang}" lang="{lang}">{t}</p>')
    return ''.join(out)


def build_order():
    blocks = json.load(open(os.path.join(SCRATCH, 'order.json')))
    out = []
    for i, b in enumerate(blocks):
        if b['type'] == 'p':
            t = b['text']
            if i == 0:
                continue  # "ՀԱՎԵԼՎԱԾ 1 · APPENDIX 1" – covered by the meta block
            if i in (1, 2):
                out.append(f'<h2 lang="{"hy" if ARM.search(t) else "en"}">{esc(t)}</h2>')
                continue
            m = re.match(r'^(\d+)\.\s+(.+?)\s{2,}(.+)$', t)
            if m:
                out.append(f'<h3 id="order-section-{m.group(1)}">{m.group(1)}. {esc(m.group(3))} · <span lang="hy">{esc(m.group(2))}</span></h3>')
                continue
            out.append(paras_html([b]))
        else:
            rows = b['rows']
            ncols = len(rows[0])
            is_check = all(len(r) == 2 and r[0]['paras'] and r[0]['paras'][0]['text'].strip() == '☐' for r in rows)
            two_equal = (i in (3, 22))
            trs = []
            for r in rows:
                if is_check:
                    trs.append(f'<tr><td class="check-cell">☐</td><td>{paras_html(r[1]["paras"])}</td></tr>')
                elif two_equal:
                    trs.append('<tr>' + ''.join(f'<td class="half">{paras_html(c["paras"])}</td>' for c in r) + '</tr>')
                else:
                    label = paras_html(r[0]['paras'])
                    value = paras_html(r[1]['paras']) if len(r) > 1 else ''
                    if not value:
                        value = '<p class="en">________________________________________</p>'
                    trs.append(f'<tr><td class="label">{label}</td><td>{value}</td></tr>')
            out.append('<table>' + ''.join(trs) + '</table>')
    return '\n'.join(out)


order_meta = f'''<div class="legal-meta">
	<span class="legal-badge">Appendix 1 to the Master Service Agreement</span>
	<dl>
		<dt>Document</dt><dd>Order Form · <span lang="hy">Պատվերի ձև</span></dd>
		<dt>Version</dt><dd>{VERSION}</dd>
		<dt>Effective from</dt><dd>{EFFECTIVE_EN} · <span lang="hy">{EFFECTIVE_HY}</span></dd>
		<dt>Status</dt><dd>Current version</dd>
	</dl>
	<p>This Order Form is an integral part of the <a href="msa.html">moderAItor Master Service Agreement (public offer)</a>. Signing or confirming the Order in the manner set out in Clauses 1.6 and 2.4 of the MSA constitutes acceptance of the Agreement and all its Appendices.</p>
	<p><strong>How to use:</strong> download the form, fill in Sections 1–4, and send it signed with an electronic digital signature, or confirm it from the email address specified in the Order, to <strong>info@moderaitor.app</strong>. The text below is published for reference.</p>
	<div class="legal-actions">
		<a class="btn swap-icon" href="{ORDER_DOCX}" download><i class="fa-solid fa-file-word"></i>Download Order Form (DOCX, AM/EN)</a>
	</div>
</div>'''

order_history = f'''<h3 id="version-history" class="mt-5 mb-3">Version history · <span lang="hy">Խմբագրությունների պատմություն</span></h3>
<table class="version-table">
	<thead><tr><th>Version</th><th>Effective from</th><th>Status</th><th>Changes</th><th>File</th></tr></thead>
	<tbody>
		<tr><td>{VERSION}</td><td>{EFFECTIVE_EN}</td><td>Current</td><td>Initial version, published together with MSA version {VERSION}.</td><td><a href="{ORDER_DOCX}" download>DOCX</a></td></tr>
	</tbody>
</table>
<p class="text-muted small">Previous versions of the form remain available for download after each update.</p>'''

open(os.path.join(OUT, 'order-form.html'), 'w').write(page(
    file='order-form.html',
    title='Order Form (Appendix 1 to the MSA) - moderAItor',
    description=f'Order Form for the use of the moderAItor AI tool, Appendix 1 to the Master Service Agreement, version {VERSION}. Download, fill in and send to conclude the agreement.',
    h1='Order Form', crumb='Appendix 1 · Order Form',
    body_html=order_meta + '\n<div class="order-form">\n' + build_order() + '\n</div>\n' + order_history))

# ---------------------------------------------------------------- Appendix 5 placeholder
editorial_body = f'''<div class="legal-meta">
	<span class="legal-badge">Appendix 5 to the Master Service Agreement</span>
	<dl>
		<dt>Document</dt><dd>Model Comment Moderation Editorial Policy · <span lang="hy">Մեկնաբանությունների մոդերացիայի օրինակելի խմբագրական քաղաքականություն</span></dd>
		<dt>Status</dt><dd>In preparation</dd>
	</dl>
	<p>This Appendix is a model document referred to in Clauses 1.5, 1.8 and 5.2.4 of the <a href="msa.html">moderAItor Master Service Agreement</a>. It is binding on the Client only to the extent the Client has adopted it as its own moderation policy.</p>
</div>

<h3 class="mt-4 mb-3">About this document</h3>
<p>The Model Comment Moderation Editorial Policy is a template that media organizations and civil society organizations can adopt, in full or with amendments, as their own public editorial policy for moderating comments on their social media pages. It describes what kinds of comments are not allowed, how flagged comments are reviewed, how temporary hiding and final decisions work, and how users can raise objections.</p>
<p>Under Clause 5.2.4 of the Master Service Agreement, each Client must develop, define and apply a publicly available, transparent and lawful moderation policy, and may use this model policy as a basis.</p>

<h3 class="mt-4 mb-3">Publication</h3>
<p>The text of the model policy is being finalized and will be published on this page in Armenian and English. Once published, it will carry its own version number and effective date, and previous versions will remain available at permanent links.</p>
<p lang="hy">Օրինակելի քաղաքականության տեքստը վերջնականացվում է և կհրապարակվի այս էջում հայերեն և անգլերեն։</p>

<h3 class="mt-4 mb-3">Contact</h3>
<p>For questions about moderation policies or for consulting support in developing your own editorial policy (Clause 3.2(H) of the MSA), contact <strong>info@moderaitor.app</strong>.</p>'''

open(os.path.join(OUT, 'editorial-policy.html'), 'w').write(page(
    file='editorial-policy.html',
    title='Model Comment Moderation Editorial Policy (Appendix 5) - moderAItor',
    description='Model Comment Moderation Editorial Policy, Appendix 5 to the moderAItor Master Service Agreement. A template moderation policy for media and civil society organizations.',
    h1='Model Editorial Policy', crumb='Appendix 5 · Editorial Policy',
    body_html=editorial_body))

print('written: msa.html, msa-v%s.html, order-form.html, editorial-policy.html' % VERSION)
