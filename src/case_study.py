"""Builds /case-study/index.html — the reader layer behind the Dribbble shot.
Same fonts (embedded like the main page), same grid, same colours. Videos lazy-play when on screen."""
import base64, html
F = lambda p: 'data:font/woff2;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
E = html.escape

IDEAS = [
 ('01', 'The wow never blocks the button.', 'idea-2',
  'The first version made visitors sit through a 13-second AI clip before they could act. The film now plays as eleven real frames shown as CCTV captures — hard cuts, a ticking camera clock, nothing that morphs. The page frame and the drop facts are there from the first capture, and Reserve is live after about five seconds. Anyone who saw the intro in the last week skips it: the finished wall sprays back on in two.'),
 ('02', 'The brand idea is the interaction.', 'idea-4',
  'OHSTA takes the most obedient garment ever made and breaks its rules. So the page never explains that — it does it. The manifesto fills in as you scroll, then FIT IN gets sprayed out and STAND OUT goes over it. Every product card names the dress-code rule its piece breaks and strikes it out as the card arrives. The same five marks — strike, stencil, splotch, drip, tear — carry all the motion.'),
 ('03', 'Every road leads to Reserve.', 'idea-6',
  'There is one action on this page. Six things lead to it: the O of INCOMING, the product tags, “Reserve →” on every card, the cursor turning into a Reserve bubble over each photo, a sticky bar with a live countdown, and the form itself. Reserving is free and takes ten seconds; the list gets the shop link 30 minutes early, which gives people a reason to sign up now instead of on Friday.'),
]
CHAPTERS = [
 ('Built to sell out', 'OHSTA (a concept brand) drops one collection a month: 300 hand-reworked suits, gone in a day. The landing page has one job — turn a Friday’s attention into reservations.'),
 ('The page is an argument', 'Every section answers the next question in a buyer’s head: Why should I stop scrolling? What is this? What exactly can I get? Is it worth the price? How do I get one?'),
 ('01 · Attention', 'CCTV captures instead of a cutscene. A clock from page load shows when each layer lands: the facts first, INCOMING at 3.7 s, Reserve at about 5 s.'),
 ('02 · Understanding', 'One sentence carries the brand. It fills in as you read; FIT IN is sprayed out and STAND OUT goes over it. The offer follows in three numbers — 300 · 10 · 0 — and the zero counts down.'),
 ('03 · Desire', 'Scarcity you can count: 10 designs × 30 pieces = 300. The rail moves sideways like a shop window, leans with your scroll speed, and every card sprays out the rule it breaks.'),
 ('04 · Trust', 'The handwork is the reason for the price, so the page shows it. Found → Ripped → Reworn on one pinned screen; RIPPED tears in two and the detail scraps get ripped off the wall.'),
 ('05 · Action', 'Six ways in, one destination. Free, no card, ten seconds. Early link at 17:30. The countdown always points to the next Friday 18:00, so the page never shows an expired drop.'),
 ('Mobile', 'Not a shrunken desktop. On phones the CCTV captures play on a monitor, then blue paint floods the screen; every section is re-composed for 390 px.'),
 ('The system', 'Two typefaces (PP Monument Extended for the shout, PP Neue Montreal for the facts), four colours, five marks from spray paint. One wall, one vocabulary.'),
]
def vid(name, cls=''):
    return f'<video class="v {cls}" muted loop playsinline preload="none" poster="media/{name}.jpg" data-src="media/{name}.mp4"></video>'

ideas = '\n'.join(f'''    <article class="idea">
      <div class="itext"><p class="lab"><b>[ {n} ]</b></p><h3 class="disp">{E(t)}</h3><p class="body">{E(b)}</p></div>
      {vid(v)}
    </article>''' for n, t, v, b in IDEAS)
chapters = '\n'.join(f'''    <article class="chap">
      {vid(f"ohsta-dribbble-{i + 1:02d}")}
      <div class="ctext"><p class="lab"><b>{i + 1:02d} / 09</b></p><h3>{E(t)}</h3><p>{E(b)}</p></div>
    </article>''' for i, (t, b) in enumerate(CHAPTERS))

page = f'''<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OHSTA — Case study: a landing page built to sell out</title>
<meta name="description" content="How the OHSTA Drop 010 landing page turns a Friday’s attention into reservations: three design decisions, the full story, the system.">
<meta name="theme-color" content="#0013ff">
<style>
@font-face{{font-family:MON;src:url({F('../fonts/mon-black.woff2')}) format("woff2");font-weight:900;font-display:swap}}
@font-face{{font-family:NM;src:url({F('../fonts/nm-book.woff2')}) format("woff2");font-weight:400;font-display:swap}}
@font-face{{font-family:NM;src:url({F('../fonts/nm-bold.woff2')}) format("woff2");font-weight:800;font-display:swap}}
:root{{--blue:#0013ff;--ink:#0b0b0b;--paper:#ebeae5;--u:calc(100vw / 1920)}}
@media (max-width:760px){{:root{{--u:calc(100vw / 390)}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:NM}}
a{{color:inherit}}
.lab{{font:400 max(12px, calc(18 * var(--u)))/1.3 NM;margin:0}}
.lab b{{font-weight:800}}
.disp{{font-family:MON;font-weight:900;text-transform:uppercase;letter-spacing:-.05em;line-height:.88;margin:0}}
.body{{font:400 max(16px, calc(26 * var(--u)))/1.3 NM;letter-spacing:-.01em;margin:0}}
header{{position:sticky;top:0;z-index:5;display:flex;justify-content:space-between;align-items:center;padding:calc(20 * var(--u)) calc(50 * var(--u));background:rgba(235,234,229,.86);backdrop-filter:blur(10px)}}
header .logo{{font:900 max(16px, calc(24 * var(--u)))/1 MON;text-decoration:none}}
header .cta{{background:var(--blue);color:#fff;text-decoration:none;font:800 max(13px, calc(17 * var(--u)))/1 NM;padding:.85em 1.3em;border-radius:99em}}
.hero{{padding:calc(140 * var(--u)) calc(50 * var(--u)) calc(110 * var(--u))}}
.hero h1{{font-size:calc(250 * var(--u))}}
.hero h1 span{{color:var(--blue)}}
.hero .row{{display:grid;grid-template-columns:1fr 1fr;gap:calc(80 * var(--u));margin-top:calc(80 * var(--u))}}
.hero ul{{margin:0;padding:0;list-style:none;font:400 max(15px, calc(22 * var(--u)))/1.35 NM}}
.hero li{{padding:.6em 0;border-top:1px solid rgba(11,11,11,.25)}}
.hero li b{{font-weight:800;margin-right:.6em;color:var(--blue)}}
section{{padding:calc(110 * var(--u)) calc(50 * var(--u))}}
section>.lab{{margin-bottom:calc(50 * var(--u))}}
.v{{width:100%;aspect-ratio:4/3;display:block;background:#000;object-fit:cover}}
.idea{{display:grid;grid-template-columns:calc(620 * var(--u)) 1fr;gap:calc(80 * var(--u));align-items:start;padding:calc(70 * var(--u)) 0;border-top:1px solid rgba(11,11,11,.25)}}
.idea h3{{font-size:calc(62 * var(--u));margin:calc(24 * var(--u)) 0 calc(30 * var(--u))}}
.dark{{background:#000;color:#fff}}
.dark .chap{{border-color:rgba(255,255,255,.25)}}
.chaps{{display:grid;grid-template-columns:1fr 1fr;gap:calc(60 * var(--u)) calc(40 * var(--u))}}
.chap h3{{font:800 max(18px, calc(30 * var(--u)))/1.15 NM;margin:calc(10 * var(--u)) 0}}
.chap p{{font:400 max(15px, calc(21 * var(--u)))/1.35 NM;margin:0;opacity:.85}}
.ctext{{padding-top:calc(22 * var(--u))}}
.end{{background:var(--blue);color:#fff;padding:calc(140 * var(--u)) calc(50 * var(--u))}}
.end h2{{font-size:calc(200 * var(--u))}}
.end p{{margin-top:calc(50 * var(--u))}}
.end a.big{{display:inline-block;margin-top:calc(40 * var(--u));background:#fff;color:var(--blue);text-decoration:none;font:900 max(18px, calc(34 * var(--u)))/1 MON;text-transform:uppercase;letter-spacing:-.03em;padding:.8em 1.2em;border-radius:99em}}
.fine{{opacity:.75;font-size:max(12px, calc(16 * var(--u)))}}
@media (max-width:760px){{
  .hero .row,.idea,.chaps{{grid-template-columns:1fr}}
  header>.lab{{display:none}}
  .hero h1{{font-size:calc(64 * var(--u))}}
  .idea h3{{font-size:calc(28 * var(--u))}}
  .end h2{{font-size:calc(54 * var(--u))}}
}}
</style>
<body>
<header><a class="logo" href="../">OH®</a><span class="lab">OHSTA — Drop 010 · Case study</span><a class="cta" href="../">See it live</a></header>

<div class="hero">
  <p class="lab"><b>[ Case study ]</b>&nbsp;&nbsp; Landing page · UX/UI · Motion · Build</p>
  <h1 class="disp" style="margin-top:calc(40 * var(--u))">Built to<br><span>sell out.</span></h1>
  <div class="row">
    <p class="body">OHSTA is a concept streetwear label that drops one collection a month: 300 hand-reworked suits, gone in a day. Its landing page is a business tool before it is a picture — it has one job, to turn a Friday’s attention into reservations. Everything on it either earns attention, explains the offer, builds trust, or leads to Reserve.</p>
    <ul>
      <li><b>01</b>The wow never blocks the button.</li>
      <li><b>02</b>The brand idea is the interaction.</li>
      <li><b>03</b>Every road leads to Reserve.</li>
    </ul>
  </div>
</div>

<section>
  <p class="lab"><b>[ Three decisions ]</b>&nbsp;&nbsp; The ones that matter most</p>
{ideas}
</section>

<section class="dark">
  <p class="lab"><b>[ The full story ]</b>&nbsp;&nbsp; Nine chapters — the page as an argument, the buyer’s five questions, mobile and the system</p>
  <div class="chaps">
{chapters}
  </div>
</section>

<div class="end">
  <p class="lab"><b>[ Drop 010 ]</b>&nbsp;&nbsp; Suits, ripped &amp; reworn</p>
  <h2 class="disp" style="margin-top:calc(30 * var(--u))">See it<br>live.</h2>
  <a class="big" href="../">ohsta-drop.vercel.app</a>
  <p class="lab fine">OHSTA is a fictional brand created for this project. Product photos are moodboard references.</p>
</div>
<script>
// videos load and play only while on screen
const io = new IntersectionObserver(es => es.forEach(e => {{
  const v = e.target;
  if (e.isIntersecting){{ if (!v.src) v.src = v.dataset.src; v.play().catch(() => {{}}); }} else v.pause();
}}), {{ rootMargin: '200px 0px' }});
document.querySelectorAll('video[data-src]').forEach(v => io.observe(v));
</script>
</body>
</html>
'''
open('../case-study/index.html', 'w').write(page)
print('case study', round(len(page) / 1024), 'KB')
