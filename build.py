#!/usr/bin/env python3
"""Dựng website tĩnh Mèo về núi từ src/tours.json ra thư mục dist/.

Chạy:  python3 build.py
Không cần cài thêm thư viện nào.

Khi web nằm trong thư mục con (GitHub Pages dạng tênuser.github.io/meovenui):
  SITE_URL=https://lbphwork-cloud.github.io/meovenui BASE_PATH=/meovenui python3 build.py
"""
import hashlib, html, json, os, re, shutil, struct
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src')
DIST = os.path.join(ROOT, 'dist')
VERSION = hashlib.md5(b''.join(open(os.path.join(SRC, 'assets', f), 'rb').read() for f in ('style.css', 'main.js'))).hexdigest()[:8]

data = json.load(open(os.path.join(SRC, 'tours.json'), encoding='utf-8'))
SITE, HOME, TOURS, VIDEOS, BOOK = data['site'], data['home'], data['tours'], data['videos'], data['booking']
BASE = os.environ.get('BASE_PATH', '').rstrip('/')
if os.environ.get('SITE_URL'):
    SITE['url'] = os.environ['SITE_URL'].rstrip('/')


def e(s):
    return html.escape(str(s), quote=True)


def rich(s):
    """Chữ thường, cho phép **đậm**."""
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', e(s))


def emph(s):
    """Chữ cho tiêu đề, phần nằm giữa *...* in nghiêng màu nhấn."""
    return re.sub(r'\*(.+?)\*', r'<em>\1</em>', e(s))


def jpeg_size(path):
    with open(path, 'rb') as f:
        f.read(2)
        while True:
            b = f.read(1)
            while b and b != b'\xff':
                b = f.read(1)
            while b == b'\xff':
                b = f.read(1)
            if not b:
                return None
            m = b[0]
            if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                f.read(3)
                h, w = struct.unpack('>HH', f.read(4))
                return w, h
            ln = struct.unpack('>H', f.read(2))[0]
            f.read(ln - 2)


_sizes = {}


def img_url(name):
    return f'/img/{name}.jpg'


def img(name, alt='', cls='', lazy=True, zoom=False, extra=''):
    p = os.path.join(SRC, 'img', name + '.jpg')
    if name not in _sizes:
        if not os.path.exists(p):
            raise SystemExit(f'Thiếu ảnh: src/img/{name}.jpg')
        _sizes[name] = jpeg_size(p)
    w, h = _sizes[name]
    attrs = f' class="{cls}"' if cls else ''
    if lazy:
        attrs += ' loading="lazy" decoding="async"'
    else:
        attrs += ' fetchpriority="high"'
    if zoom:
        attrs += f' data-zoom="{img_url(name)}"'
    return f'<img src="{img_url(name)}" width="{w}" height="{h}" alt="{e(alt)}"{attrs}{extra}>'


def tour_url(t, absolute=False):
    path = f'/tour/{t["slug"]}/'
    return SITE['url'] + path if absolute else path


def book_msg(t=None):
    if t:
        return f'Mèo ơi, mình muốn hỏi tour {t["name"]}. Link: {tour_url(t, True)}'
    return 'Mèo ơi, mình muốn hỏi tour Quảng Trị'


def zalo_btn(label, t=None, cls='btn btn--primary'):
    return (f'<a class="{cls}" href="{e(SITE["zalo"])}" target="_blank" rel="noopener" '
            f'data-book="{e(book_msg(t))}">{e(label)}</a>')


def call_btn(label='Gọi Mèo', cls='btn btn--ghost'):
    return f'<a class="{cls}" href="tel:{SITE["phone"]}">{e(label)}</a>'


def head(title, desc, path, og_img, extra=''):
    url = SITE['url'] + path
    og = SITE['url'] + f'/img/og/{og_img}.jpg'
    return f'''<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta name="theme-color" content="#43704e">
<meta property="og:type" content="website">
<meta property="og:locale" content="vi_VN">
<meta property="og:site_name" content="{e(SITE['name'])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{e(og)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v={VERSION}">
{extra}</head>
<body>
'''


def header():
    return f'''<header class="site-header">
  <div class="wrap">
    <a class="logo" href="/" aria-label="Mèo về núi, về trang chủ"><img src="/img/brand/logo.svg" width="202" height="96" alt="Mèo về núi - Quang Tri Tour"></a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav">Menu</button>
    <nav class="nav" id="nav">
      <a href="/#tour">Các tour</a>
      <a href="/#ve-meo">Về Mèo</a>
      <a href="/#video">Video</a>
      <a href="/dat-tour/">Đặt tour</a>
      {zalo_btn('Nhắn Zalo', cls='btn btn--primary btn--sm')}
    </nav>
  </div>
</header>
'''


def footer():
    tours = ''.join(f'<li><a href="{tour_url(t)}">{e(t["name"])}</a></li>' for t in TOURS)
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div>
      <a class="logo logo--footer" href="/" aria-label="Mèo về núi, về trang chủ"><img src="/img/brand/logo-light.svg" width="202" height="96" alt="Mèo về núi - Quang Tri Tour"></a>
      <p style="margin-top:12px;max-width:340px">Mình là Mèo, local guide người Quảng Trị. Mình dẫn tour ghép nhóm nhỏ và tour riêng đi khắp quê mình, từ di tích lịch sử tới núi rừng phía Tây.</p>
    </div>
    <div>
      <h4>Các tour</h4>
      <ul>{tours}<li><a href="/dat-tour/">Cách đặt tour và hoàn huỷ</a></li></ul>
    </div>
    <div>
      <h4>Nhắn Mèo</h4>
      <ul>
        <li><a href="tel:{SITE['phone']}">{e(SITE['phone_display'])}</a> (Zalo, điện thoại)</li>
        <li><a href="mailto:{e(SITE['email'])}">{e(SITE['email'])}</a></li>
        <li><a href="{e(SITE['tiktok'])}" target="_blank" rel="noopener">TikTok</a> &nbsp; <a href="{e(SITE['facebook'])}" target="_blank" rel="noopener">Facebook</a> &nbsp; <a href="{e(SITE['instagram'])}" target="_blank" rel="noopener">Instagram</a></li>
      </ul>
    </div>
    <div class="footer-copy">&copy; {date.today().year} {e(SITE['name'])}. Ảnh và video là của Mèo tự chụp, tự quay nha.</div>
  </div>
</footer>
<div class="modal" id="video-modal" role="dialog" aria-modal="true" aria-label="Xem video">
  <div class="modal__box">
    <button class="modal__close" type="button">Đóng</button>
    <iframe class="modal__frame" src="about:blank" allow="autoplay; encrypted-media; fullscreen; picture-in-picture" allowfullscreen title="Video TikTok của Mèo về núi"></iframe>
    <a class="modal__link" href="{e(SITE['tiktok'])}" target="_blank" rel="noopener">Xem video này trên TikTok của Mèo</a>
  </div>
</div>
<div class="modal lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Xem ảnh">
  <div class="modal__box"><button class="modal__close" type="button">Đóng</button><img alt=""></div>
</div>
<div class="toast" role="status" aria-live="polite"></div>
<script src="/assets/main.js?v={VERSION}" defer></script>
</body>
</html>
'''


def video_rail(ids):
    cards = []
    for vid in ids:
        title = VIDEOS.get(vid, '')
        cards.append(f'''<button class="video-card" type="button" data-video="{vid}" aria-label="Xem video: {e(title)}">
  <div class="video-card__thumb">{img('video/' + vid, title)}<span class="video-card__play">Xem video</span></div>
  <div class="video-card__title">{e(title)}</div>
</button>''')
    return '<div class="video-rail">' + '\n'.join(cards) + '</div>'


def tour_card(t, small=False):
    dur = t['facts'][0]['v']
    return f'''<a class="tour-card reveal" href="{tour_url(t)}">
  <div class="tour-card__media">{img(t['card_img'], t['name'])}<span class="tour-card__tag">{e(dur)}</span></div>
  <div class="tour-card__body">
    <h3>{e(t['name'])}</h3>
    <p class="tour-card__short">{e(t['short'])}</p>
    <div class="tour-card__foot">
      <div class="price-sm">Giá từ<b>{e(t['price_from'])}<span style="font-size:14px;font-weight:500;color:var(--ink-3)">{e(t['price_unit'])}</span></b></div>
      <span class="link-arrow">Xem chi tiết</span>
    </div>
  </div>
</a>'''


def steps_html(light=False):
    items = ''.join(f'<div class="step"><h3>{e(s["title"])}</h3><p>{e(s["text"])}</p></div>' for s in BOOK['steps'])
    return f'<div class="steps{" steps--light" if light else ""}">{items}</div>'


# ---------------- Trang chủ ----------------
def build_home():
    a = HOME['about']
    stats = ''.join(f'<div class="stat"><div class="stat__num">{e(s["num"])}</div><div class="stat__label">{e(s["label"])}</div></div>' for s in HOME['stats'])
    paras = ''.join(f'<p>{e(p)}</p>' for p in a['paras'])
    cards = '\n'.join(tour_card(t) for t in TOURS)
    ld = {
        '@context': 'https://schema.org', '@type': 'TravelAgency', 'name': SITE['name'], 'url': SITE['url'],
        'telephone': '+84' + SITE['phone'][1:], 'email': SITE['email'], 'image': SITE['url'] + '/img/og/home.jpg',
        'areaServed': 'Quảng Trị, Việt Nam', 'sameAs': [SITE['tiktok'], SITE['facebook'], SITE['instagram']],
    }
    out = head(f'{SITE["name"]} - Tour Quảng Trị cùng local guide', SITE['description'], '/', 'home',
               f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n')
    out += header()
    out += f'''<main>
<section class="hero">
  {img(HOME['hero_img'], 'Máy bay tại Sân bay Tà Cơn, Khe Sanh', 'hero__img', lazy=False)}
  <div class="wrap">
    <div class="hero__eyebrow">{e(HOME['eyebrow'])}</div>
    <h1>{emph(HOME['title'])}</h1>
    <p class="hero__lead">{e(HOME['lead'])}</p>
    <div class="hero__actions">
      <a class="btn btn--light" href="#tour">Xem các tour</a>
      {zalo_btn('Nhắn Zalo cho Mèo', cls='btn btn--ghost-light')}
    </div>
  </div>
</section>
<div class="stats"><div class="wrap"><div>{stats}</div></div></div>

<section class="section" id="tour">
  <div class="wrap">
    <div class="section-head reveal">
      <span class="eyebrow">Các tour của Mèo</span>
      <h2 class="h2">Bạn muốn đi đâu với mình?</h2>
      <p>Mỗi tour mình để sẵn lịch trình, bảng giá, những gì đã bao gồm và cả video từ các chuyến đi trước. Muốn biết lịch khởi hành gần nhất hay muốn đi riêng theo nhóm thì nhắn Mèo nha.</p>
    </div>
    <div class="tour-grid">{cards}</div>
  </div>
</section>

<section class="section section--sand" id="ve-meo">
  <div class="wrap about">
    <div class="about__img reveal">{img(a['img'], 'Mèo về núi giữa rừng thông Khe Sanh')}</div>
    <div class="about__text reveal">
      <span class="eyebrow">Về Mèo</span>
      <h2 class="h2">{emph(a['title'])}</h2>
      {paras}
      <div class="about__social">
        <a class="btn btn--ghost btn--sm" href="{e(SITE['tiktok'])}" target="_blank" rel="noopener">TikTok @meovenui</a>
        <a class="btn btn--ghost btn--sm" href="{e(SITE['facebook'])}" target="_blank" rel="noopener">Facebook</a>
        <a class="btn btn--ghost btn--sm" href="{e(SITE['instagram'])}" target="_blank" rel="noopener">Instagram</a>
      </div>
    </div>
  </div>
</section>

<section class="section" id="video">
  <div class="wrap">
    <div class="section-head reveal">
      <span class="eyebrow">Video Mèo quay</span>
      <h2 class="h2">Xem thử chuyến đi nè</h2>
      <p>Bấm vào video là xem được liền, không cần cài TikTok đâu nha.</p>
    </div>
    {video_rail(HOME['featured_videos'])}
  </div>
</section>

<section class="section section--green" id="dat-tour">
  <div class="wrap">
    <div class="section-head reveal">
      <span class="eyebrow">Đặt tour</span>
      <h2 class="h2">Đặt tour với Mèo dễ lắm, 4 bước thui</h2>
    </div>
    {steps_html()}
    <div class="policy-link"><a class="btn btn--ghost-light" href="/dat-tour/">Xem chính sách hoàn huỷ</a></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="cta-band reveal">
      <div>
        <h2>Đi riêng cả nhóm hay cả nhà?</h2>
        <p>Mình nhận lên lịch trình riêng theo số ngày, sở thích và sức khoẻ của cả đoàn. Nhắn Mèo kể mình nghe bạn muốn đi kiểu gì nha.</p>
      </div>
      <div class="cta-band__actions">
        {zalo_btn('Nhắn Zalo', cls='btn btn--light')}
        {call_btn('Gọi ' + SITE['phone_display'], 'btn btn--ghost-light')}
      </div>
    </div>
  </div>
</section>
</main>
'''
    out += footer()
    return out


# ---------------- Trang tour ----------------
def day_html(d):
    items, last = [], None
    for it in d['items']:
        part = it.get('part')
        if part and part != last:
            items.append(f'<li class="tl-part">{e(part)}</li>')
            last = part
        items.append(f'<li class="tl"><span class="tl__time">{e(it["time"])}</span><span class="tl__text">{rich(it["text"])}</span></li>')
    pre = f'<div class="day__pre">{rich(d["pre"])}</div>' if d.get('pre') else ''
    extra = ''
    if d.get('extra'):
        extra = f'<div class="day__extra"><h4>{e(d["extra_title"])}</h4><ul>' + ''.join(f'<li>{e(x)}</li>' for x in d['extra']) + '</ul></div>'
    note = f'<div class="day__note">{rich(d["note"])}</div>' if d.get('note') else ''
    media = ''.join(f'<figure>{img(n, d["title"], zoom=True)}</figure>' for n in d.get('imgs', []))
    if d.get('img_note'):
        media += f'<figcaption>{e(d["img_note"])}</figcaption>'
    return f'''<div class="day reveal">
  <div>
    <span class="day__label">{e(d['label'])}</span>
    <h3>{e(d['title'])}</h3>
    {pre}
    <ul class="timeline">{''.join(items)}</ul>
    {extra}{note}
  </div>
  <div class="day__media">{media}</div>
</div>'''


def build_tour(t):
    url = tour_url(t)
    facts = ''.join(f'<div class="fact"><div class="fact__k">{e(f["k"])}</div><div class="fact__v">{e(f["v"])}</div></div>' for f in t['facts'])
    sections = [('gioi-thieu', 'Giới thiệu')]
    if t.get('videos'):
        sections.append(('video', 'Video'))
    sections.append(('lich-trinh', 'Lịch trình'))
    if t.get('places'):
        sections.append(('diem-den', 'Điểm đến'))
    sections.append(('gia-tour', 'Giá tour'))
    if t.get('season'):
        sections.append(('mua-dep', 'Mùa đẹp'))
    if t.get('more'):
        sections.append(('kham-pha', 'Khám phá thêm'))
    sections.append(('anh', 'Ảnh'))
    subnav = ''.join(f'<a href="#{i}">{e(n)}</a>' for i, n in sections)

    intro = ''.join(f'<p>{rich(p)}</p>' for p in t['intro'])
    fit = f'<div class="fit">{e(t["fit"])}</div>' if t.get('fit') else ''
    hls = ''
    if t.get('highlights'):
        hls = '<div class="highlights">' + ''.join(f'<div class="hl"><h3>{e(h["title"])}</h3><p>{e(h["text"])}</p></div>' for h in t['highlights']) + '</div>'
    else:
        hls = f'<div class="highlights"><div class="about__img" style="aspect-ratio:4/3">{img(t["gallery"][1] if len(t["gallery"]) > 1 else t["hero_img"], t["name"], zoom=True)}</div></div>'

    videos = ''
    if t.get('videos'):
        videos = f'''<section class="section section--green anchor" id="video">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Video Mèo quay</span><h2 class="h2">Xem thử chuyến đi nè</h2><p>Bấm vào video là xem được liền nha.</p></div>
    {video_rail(t['videos'])}
  </div>
</section>'''

    days = '\n'.join(day_html(d) for d in t['days'])

    places = ''
    if t.get('places'):
        ps = ''.join(f'<figure class="place reveal">{img(p["img"], p["name"], zoom=True)}<figcaption>{e(p["name"])}</figcaption></figure>' for p in t['places'])
        places = f'''<section class="section section--sand anchor" id="diem-den">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Trong lịch trình</span><h2 class="h2">Mình sẽ cùng nhau ghé những nơi này</h2></div>
    <div class="places">{ps}</div>
  </div>
</section>'''

    # Giá
    left = ''
    if t.get('price_table'):
        pt = t['price_table']
        rows = ''.join(f'<tr><td>{e(r[0])}</td><td>{e(r[1])}</td></tr>' for r in pt['rows'])
        pn = ''
        if pt.get('notes'):
            pn = '<ul class="pnotes">' + ''.join(f'<li>{e(n)}</li>' for n in pt['notes']) + '</ul>'
        left = f'<div class="card reveal"><h3>Bảng giá</h3><table class="ptable"><thead><tr><th>{e(pt["head"][0])}</th><th>{e(pt["head"][1])}</th></tr></thead><tbody>{rows}</tbody></table>{pn}</div>'
    else:
        left = f'''<div class="card reveal"><h3>Giá tour</h3>
  <div style="font-family:var(--serif);font-size:44px;font-weight:500;color:var(--clay-600);line-height:1.1;font-variation-settings:'SOFT' 100">{e(t['price_from'])}<small style="font-family:var(--sans);font-size:16px;font-weight:500;color:var(--ink-3)">{e(t['price_unit'])}</small></div>
  <p style="color:var(--ink-2);margin-top:10px">{e(t['price_note'])}. {e(t['facts'][2]['v'])}.</p>
  <div class="share-row">{zalo_btn('Hỏi Mèo lịch khởi hành', t)}{call_btn()}</div>
</div>'''
    inc = '<ul class="checklist">' + ''.join(f'<li>{e(x)}</li>' for x in t['included']) + '</ul>'
    exc = ''
    if t.get('excluded'):
        exc = '<div class="card reveal"><h3>Chưa bao gồm</h3><ul class="checklist checklist--no">' + ''.join(f'<li>{e(x)}</li>' for x in t['excluded']) + '</ul></div>'
    notes = ''
    if t.get('notes'):
        notes = '<div class="notes-box reveal"><h4>Lưu ý</h4><ul>' + ''.join(f'<li>{e(n)}</li>' for n in t['notes']) + '</ul></div>'
    price = f'''<section class="section anchor" id="gia-tour">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Chi phí</span><h2 class="h2">Giá tour và những gì đã có</h2></div>
    <div class="price-grid">
      <div>{left}{notes}</div>
      <div><div class="card reveal"><h3>Đã bao gồm</h3>{inc}</div>{exc}</div>
    </div>
  </div>
</section>'''

    season = ''
    if t.get('season'):
        s = t['season']
        st = ''.join(f'<p>{e(p)}</p>' for p in s['text'])
        mos = ''.join(img(n, s['title'], zoom=True) for n in s['imgs'])
        season = f'''<section class="section section--green anchor" id="mua-dep">
  <div class="wrap season">
    <div class="season__text reveal"><span class="eyebrow">Từ đầu tháng 11 đến giữa tháng 1</span><h2 class="h2" style="margin-bottom:20px">{e(s['title'])}</h2>{st}
      <div class="share-row">{zalo_btn('Hỏi Mèo lịch mùa lá đỏ', t, 'btn btn--light')}</div></div>
    <div class="mosaic reveal">{mos}</div>
  </div>
</section>'''

    more = ''
    if t.get('more'):
        m = t['more']
        items = ''.join(f'<div class="more reveal">{img(i["img"], i["title"])}<div class="more__body"><h3>{e(i["title"])}</h3><p>{e(i["text"])}</p></div></div>' for i in m['items'])
        more = f'''<section class="section section--sand anchor" id="kham-pha">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Ngoài lịch trình</span><h2 class="h2">{e(m['title'])}</h2></div>
    <div class="more-grid">{items}</div>
  </div>
</section>'''

    gal = ''.join(img(n, t['name'], zoom=True) for n in t['gallery'])
    others = ''.join(tour_card(o) for o in TOURS if o['slug'] != t['slug'])

    desc = f'{t["name"]}: {t["short"]}. Giá từ {t["price_from"]}{t["price_unit"]}. Lịch trình chi tiết, chi phí bao gồm và video thực tế.'
    ld = {
        '@context': 'https://schema.org', '@type': 'TouristTrip', 'name': t['name'], 'description': t['short'],
        'url': SITE['url'] + url, 'image': SITE['url'] + f'/img/og/{t["slug"]}.jpg',
        'touristType': 'Du lịch lịch sử, văn hoá, thiên nhiên',
        'provider': {'@type': 'TravelAgency', 'name': SITE['name'], 'telephone': '+84' + SITE['phone'][1:], 'url': SITE['url']},
        'offers': {'@type': 'Offer', 'price': re.sub(r'\D', '', t['price_from']), 'priceCurrency': 'VND', 'url': SITE['url'] + url},
    }
    out = head(f'{t["name"]} | {SITE["name"]}', desc, url, t['slug'],
               f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n')
    out += header()
    out += f'''<main>
<section class="hero tour-hero">
  {img(t['hero_img'], t['name'], 'hero__img', lazy=False, extra=f' style="object-position:{t.get("hero_pos", "center")}"')}
  <div class="wrap">
    <div class="crumbs"><a href="/">Trang chủ</a> / <a href="/#tour">Các tour</a></div>
    <h1>{e(t['name'])}</h1>
    <p class="tour-hero__short">{e(t['short'])}</p>
    <div class="hero__actions" style="margin-top:28px">
      {zalo_btn('Đặt tour qua Zalo', t, 'btn btn--light')}
      <a class="btn btn--ghost-light" href="#lich-trinh">Xem lịch trình</a>
    </div>
  </div>
</section>
<div class="facts-bar"><div class="wrap"><div>{facts}
  <div class="fact fact--price"><div><div class="fact__k">Giá từ</div><div class="fact__v">{e(t['price_from'])}<small>{e(t['price_unit'])}</small></div><div class="fact__note">{e(t['price_note'])}</div></div></div>
</div></div></div>
<nav class="subnav" aria-label="Mục lục tour"><div class="wrap">{subnav}</div></nav>

<section class="section anchor" id="gioi-thieu">
  <div class="wrap intro">
    <div class="intro__text reveal"><span class="eyebrow">Giới thiệu</span><h2 class="h2">{e(t['intro_title'])}</h2>{intro}{fit}
      <div class="share-row"><button class="btn btn--ghost btn--sm" type="button" data-copy-link="{e(SITE['url'] + url)}">Copy link tour</button></div>
    </div>
    {hls}
  </div>
</section>
{videos}
<section class="section anchor" id="lich-trinh">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Lịch trình chi tiết</span><h2 class="h2">Mình sẽ đi những đâu?</h2><p>Lịch trình có thể đổi chút xíu theo thời tiết và tình hình thực tế, để cả đoàn đi vui và an toàn nhất nha.</p></div>
    {days}
  </div>
</section>
{places}
{price}
{season}
{more}
<section class="section anchor" id="anh">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Album</span><h2 class="h2">Ảnh từ mấy chuyến đi trước</h2></div>
    <div class="gallery reveal">{gal}</div>
  </div>
</section>

<section class="section section--green">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Đặt tour</span><h2 class="h2">Đặt tour với Mèo dễ lắm, 4 bước thui</h2></div>
    {steps_html()}
    <div class="share-row" style="margin-top:28px">{zalo_btn('Đặt tour qua Zalo', t, 'btn btn--light')}<a class="btn btn--ghost-light" href="/dat-tour/">Chính sách hoàn huỷ</a></div>
  </div>
</section>

<section class="section section--sand other-tours">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Tour khác</span><h2 class="h2">Mèo còn mấy tour này nữa nè</h2></div>
    <div class="tour-grid">{others}</div>
  </div>
</section>
</main>
<div class="book-bar">
  <div class="book-bar__price">Giá mỗi khách từ<b>{e(t['price_from'])}</b></div>
  {call_btn('Gọi', 'btn btn--ghost')}
  {zalo_btn('Đặt qua Zalo', t)}
</div>
'''
    out += footer()
    return out


# ---------------- Trang đặt tour ----------------
def build_booking():
    cancel = ''.join(f'<li>{e(c)}</li>' for c in BOOK['cancel'])
    out = head(f'Cách đặt tour và chính sách hoàn huỷ | {SITE["name"]}',
               'Các bước đặt tour, đặt cọc và chính sách hoàn huỷ tour của Mèo về núi.', '/dat-tour/', 'home')
    out += header()
    out += f'''<main>
<section class="page-head"><div class="wrap">
  <span class="eyebrow">Đặt tour</span>
  <h1>Cách đặt tour và chính sách hoàn huỷ</h1>
  <p>Trước khi chuyển cọc, bạn nhắn Zalo hoặc gọi Mèo qua số {e(SITE['phone_display'])} để mình kiểm tra lịch còn chỗ giúp bạn nha.</p>
</div></section>
<section class="section" style="padding-top:24px"><div class="wrap">
  {steps_html(light=True)}
  <div class="prose">
    <h2>Chính sách hoàn huỷ</h2>
    <p>Số ngày tính tới ngày khởi hành nha.</p>
    <ul>{cancel}</ul>
    <h2>Điều kiện bất khả kháng</h2>
    <p>{e(BOOK['force_majeure'])}</p>
    <div class="share-row">{zalo_btn('Nhắn Zalo cho Mèo')}{call_btn('Gọi ' + SITE['phone_display'])}</div>
  </div>
</div></section>
</main>
'''
    out += footer()
    return out


def build_404():
    out = head(f'Không tìm thấy trang | {SITE["name"]}', SITE['description'], '/404', 'home')
    out += header()
    out += f'''<main><section class="page-head"><div class="wrap">
  <h1>Ui, Mèo không tìm thấy trang này</h1>
  <p>Chắc đường link cũ rồi đó. Bạn quay về trang chủ xem các tour của mình nha.</p>
  <div class="share-row"><a class="btn btn--primary" href="/#tour">Xem các tour</a></div>
</div></section></main>
'''
    return out + footer()


def with_base(content):
    """Thêm tiền tố thư mục con vào các đường dẫn nội bộ bắt đầu bằng /."""
    if not BASE:
        return content
    return re.sub(r'((?:href|src|data-zoom)=")/(?!/)', r'\1' + BASE + '/', content)


def write(rel, content):
    if rel.endswith('.html'):
        content = with_base(content)
    p = os.path.join(DIST, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    shutil.copytree(os.path.join(SRC, 'assets'), os.path.join(DIST, 'assets'))
    shutil.copytree(os.path.join(SRC, 'img'), os.path.join(DIST, 'img'))
    for f in ('favicon.svg', '_headers'):
        shutil.copy(os.path.join(SRC, f), os.path.join(DIST, f))

    write('index.html', build_home())
    for t in TOURS:
        write(f'tour/{t["slug"]}/index.html', build_tour(t))
    write('dat-tour/index.html', build_booking())
    write('404.html', build_404())

    urls = ['/', '/dat-tour/'] + [tour_url(t) for t in TOURS]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += ''.join(f'  <url><loc>{SITE["url"]}{u}</loc><lastmod>{date.today().isoformat()}</lastmod></url>\n' for u in urls)
    sm += '</urlset>\n'
    write('sitemap.xml', sm)
    write('.nojekyll', '')
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {SITE["url"]}/sitemap.xml\n')
    print(f'Xong: {len(TOURS)} tour, thư mục dist/ sẵn sàng để đưa lên Cloudflare Pages.')


if __name__ == '__main__':
    main()
