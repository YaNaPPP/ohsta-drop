/* OHSTA — the page below the wall.
   Story: the rule (manifesto) → the pieces (horizontal) → how a suit breaks → the drop (reserve).
   Motion is scroll-driven (GSAP ScrollTrigger + Lenis) and reuses the hero's spray vocabulary:
   sprayed strike-throughs, stencil reveals (--sx mask), splotch buttons and paint runs.
   Hero globals used here: introDone, act2Started, isVideo, skipFilm, breath, dropState, fmtCD, fitText,
   makeSplotch, renderBase, drawSplotch, drawRun, mulberry. */
(() => {
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
gsap.registerPlugin(ScrollTrigger);
const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
const isMob = () => innerWidth <= 760;
const root = document.documentElement;
const clamp = gsap.utils.clamp;

/* ---------- the hero's film grain tile, shared with the light and blue sections ---------- */
(function shareGrain(){
  const g = $('#grain'), bg = g && g.style.backgroundImage;
  if (bg){ root.style.setProperty('--grain', bg); root.style.setProperty('--grainSize', g.style.backgroundSize); }
  else setTimeout(shareGrain, 200);
})();

/* ---------- smooth scroll; held while the CCTV preloader runs ---------- */
const lenis = new Lenis({ lerp: .1, wheelMultiplier: .9, smoothWheel: !RM });
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add(t => lenis.raf(t * 1000));
gsap.ticker.lagSmoothing(0);
lenis.stop();
let unlocked = false;
function unlock(){ if (unlocked) return; unlocked = true; root.classList.remove('lock'); lenis.start(); ScrollTrigger.refresh(); }
(function watchPre(){ if ($('#pre').classList.contains('gone')) unlock(); else setTimeout(watchPre, 150); })();
// scrolling during the film fast-forwards to the finished wall, so nobody comes back to half a tag
function intent(){ if (unlocked && isVideo() && !act2Started && !introDone) { try { skipFilm(); } catch (e) {} } }
addEventListener('wheel', intent, { passive: true });
addEventListener('touchmove', intent, { passive: true });
window.goTo = sel => {
  unlock(); intent();
  lenis.scrollTo(sel === '#top' ? 0 : $(sel), { duration: 1.5, easing: x => 1 - Math.pow(1 - x, 4) });
};
document.addEventListener('click', e => {
  const a = e.target.closest('[data-go]'); if (!a) return;
  e.preventDefault();
  if (a.dataset.piece){ const sel = $('#reserveForm select[name=piece]'); sel.value = a.dataset.piece; }
  goTo(a.dataset.go);
});
$('#fScroll').addEventListener('click', () => goTo('#rule'));

/* ---------- lines set to fill the full measure ---------- */
function fitFills(){
  $$('.fill').forEach(f => {
    const fi = f.querySelector('.fi'); if (!fi) return;
    const W = f.clientWidth; if (!W) return;
    f.style.fontSize = '100px';
    const w = fi.getBoundingClientRect().width;
    if (w) f.style.fontSize = (100 * W / w).toFixed(2) + 'px';
  });
}

/* ---------- torn top edge of the first paper section ---------- */
(function torn(){
  const R = mulberry(17); let d = 'M0 60 L0 31', x = 0;
  while (x < 1920){ x = Math.min(1920, x + 10 + R() * 30); d += ` L${x.toFixed(0)} ${(18 + R() * 22 - (R() < .1 ? R() * 14 : 0)).toFixed(1)}`; }
  $('.js-torn').setAttribute('d', d + ' L1920 60Z');
})();

/* ---------- sprayed strokes: a hand-drawn path, sized from the text it crosses ---------- */
function wobblyLine(x0, y0, x1, y1, amp, R){
  const n = 5, pts = [];
  for (let i = 0; i <= n; i++){ const t = i / n; pts.push([x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + (i && i < n ? (R() - .5) * amp : 0)]); }
  let d = `M${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)}`;
  for (let i = 1; i < pts.length; i++){
    const [px, py] = pts[i - 1], [qx, qy] = pts[i], mx = (px + qx) / 2;
    d += ` Q${px.toFixed(1)} ${py.toFixed(1)} ${mx.toFixed(1)} ${((py + qy) / 2).toFixed(1)}`;
  }
  return d + ` L${pts[n][0].toFixed(1)} ${pts[n][1].toFixed(1)}`;
}
function primePath(p){ const L = p.getTotalLength(); p.style.strokeDasharray = L; p._L = L; return L; }

/* ---------- where paint can run from: the feet of the letters ----------
   The text is drawn once on an offscreen canvas in the same font, size and tracking. For every pixel column we
   find the glyph's lowest point; columns whose bottom sits on the baseline (the feet of H, T, A, the bottom of
   O and S) are where a drip can hang. Runs start a little inside the letter so the top flare merges into it. */
function glyphFeet(text, fs0, ls0){
  const s = Math.max(1, 240 / fs0), fs = fs0 * s, ls = ls0 * s;          // small sizes are measured at a larger scale
  const c = document.createElement('canvas'), g = c.getContext('2d'), font = `900 ${fs}px "OH Display"`;
  g.font = font;
  const m = g.measureText(text), pad = Math.ceil(fs * .1);
  c.width = Math.ceil(m.width + Math.abs(ls) * text.length + pad * 2); c.height = Math.ceil(fs * 1.5);
  g.font = font; g.textBaseline = 'alphabetic'; g.fillStyle = '#000';
  let W;
  if ('letterSpacing' in g){ g.letterSpacing = ls + 'px'; g.fillText(text, pad, fs); W = g.measureText(text).width; }
  else { let x = pad; for (const ch of text){ g.fillText(ch, x, fs); x += g.measureText(ch).width + ls; } W = x - pad; }
  const d = g.getImageData(0, 0, c.width, c.height).data, bottom = new Float32Array(c.width).fill(-1);
  for (let x = 0; x < c.width; x++) for (let y = c.height - 1; y >= 0; y--) if (d[(y * c.width + x) * 4 + 3] > 140){ bottom[x] = y; break; }
  return { bottom, pad, base: fs, W, s, asc: m.fontBoundingBoxAscent || fs * .8, desc: m.fontBoundingBoxDescent || fs * .2 };
}
// pick n hanging points on the feet, each at least minW wide; returns canvas x and the foot's y (top of the run)
function pickFeet(f, n, minW, seed){
  const segs = [], tol = Math.max(2, f.base * .015);
  minW *= f.s;
  let s = -1;
  for (let x = 0; x <= f.bottom.length; x++){
    const on = x < f.bottom.length && f.bottom[x] >= f.base - tol;
    if (on && s < 0) s = x;
    if (!on && s >= 0){ if (x - s >= minW) segs.push([s, x - 1]); s = -1; }
  }
  const R = mulberry(seed), cands = [];
  segs.forEach(([a, b]) => {
    const w = b - a, k = w > minW * 5 ? 2 : 1;                        // a wide foot can carry two runs
    for (let i = 0; i < k; i++) cands.push(a + w * (k === 1 ? .3 + R() * .4 : (i ? .68 : .3) + (R() - .5) * .08));
  });
  // keep them spread: drop candidates until n remain, removing the one closest to a neighbour
  while (cands.length > n){
    let bi = 1, bd = Infinity;
    for (let i = 1; i < cands.length; i++){ const dd = cands[i] - cands[i - 1]; if (dd < bd){ bd = dd; bi = R() < .5 ? i : i - 1; } }
    cands.splice(bi, 1);
  }
  return cands.map(x => { let top = Infinity; for (let i = Math.round(x - minW / 2); i <= Math.round(x + minW / 2); i++) if (f.bottom[i] >= f.base - tol) top = Math.min(top, f.bottom[i]); return { x, y: top === Infinity ? f.base : top }; });
}
// canvas coords → coords inside the inline-block that holds the text (line-height lh, in em)
function feetToBox(f, pts, fs, lh, boxW){
  const sx = boxW / f.W, baseInBox = (lh * fs - (f.asc + f.desc) / f.s) / 2 + f.asc / f.s;
  return pts.map(p => ({ x: (p.x - f.pad) * sx, y: baseInBox + (p.y - f.base) / f.s }));
}

/* ---------- 01 · the rule: words fill in, FIT IN gets sprayed out, STAND OUT goes over it ---------- */
const statement = $('.statement'), last = $('.statement .fill.last'), lastFi = last.querySelector('.fi');
const tag = $('.tagword'), strike = $('.js-strike path');
function layoutRule(){
  const sr = statement.getBoundingClientRect(), lr = lastFi.getBoundingClientRect(), fs = parseFloat(last.style.fontSize);
  const svg = $('.js-strike'); svg.setAttribute('viewBox', `0 0 ${sr.width.toFixed(0)} ${sr.height.toFixed(0)}`);
  const y = lr.top - sr.top + lr.height * .47;
  strike.setAttribute('d', wobblyLine(lr.left - sr.left - fs * .06, y + fs * .05, lr.right - sr.left + fs * .05, y - fs * .07, fs * .05, mulberry(5)));
  strike.style.strokeWidth = (fs * .13).toFixed(1);
  primePath(strike);
  const tfs = fs * (isMob() ? .3 : .34);
  tag.style.fontSize = tfs.toFixed(1) + 'px';
  const tw = tag.querySelector('.tw').getBoundingClientRect().width;
  tag.style.left = Math.min(lr.right - sr.left - tw * 1.02, lr.left - sr.left + lr.width * .3).toFixed(1) + 'px';
  tag.style.top = (y - fs * .07 - tfs * .84).toFixed(1) + 'px';          // sits on top of the sprayed line, not inside it
  const twEl = tag.querySelector('.tw'), drips = $$('.tagword .drip');
  const f = glyphFeet(twEl.textContent.toUpperCase(), tfs, -.04 * tfs);
  const pts = feetToBox(f, pickFeet(f, drips.length, tfs * .16, 8), tfs, .9, twEl.offsetWidth);
  const h = twEl.offsetHeight, k = Math.tan(-9 * Math.PI / 180);       // .tw is skewX(-9deg) around its centre
  const lens = [1.1, .6, 1.4, .8, 1.2, .7];
  drips.forEach((dr, i) => {
    const p = pts[i]; if (!p){ dr.style.display = 'none'; return; }
    dr.style.display = '';
    dr.style.left = (twEl.offsetLeft + p.x + k * (p.y - h / 2) - tfs * .0325).toFixed(1) + 'px';
    dr.style.top = (twEl.offsetTop + p.y - tfs * .05).toFixed(1) + 'px';
    dr.style.setProperty('--l', lens[i % lens.length]);
  });
}
function buildRule(){
  const words = $$('.statement .w'), lastW = $$('.statement .fill.last .w');
  const tl = gsap.timeline({ scrollTrigger: { trigger: '#statementPin', start: 'top top', end: () => '+=' + innerHeight * (isMob() ? 1.2 : 1.6),
    pin: true, scrub: .7, anticipatePin: 1, invalidateOnRefresh: true } });
  tl.fromTo(words, { color: '#c4c2ba' }, { color: '#0b0b0b', stagger: .14, duration: .35, ease: 'none' })
    .fromTo(strike, { strokeDashoffset: () => strike._L }, { strokeDashoffset: 0, duration: .45, ease: 'power1.inOut' }, '+=.1')
    .to(lastW, { color: '#9d9b93', duration: .25 }, '<.15')
    .fromTo('.tagword .tw', { '--sx': '-12%' }, { '--sx': '135%', duration: .55, ease: 'power1.inOut' }, '-=.05')
    .fromTo('.tagword .drip', { scaleY: 0 }, { scaleY: 1, stagger: .06, duration: .35, ease: 'power2.out' }, '-=.2')
    .to({}, { duration: .3 });
  // numbers count when they arrive; "0 restocks" counts down to nothing
  $$('.js-count').forEach(b => {
    const to = +b.dataset.to, from = to === 0 ? 9 : 0, o = { v: from };
    b.textContent = from;
    ScrollTrigger.create({ trigger: b, start: 'top 88%', once: true,
      onEnter: () => gsap.to(o, { v: to, duration: to === 0 ? 1.1 : 1.6, ease: 'power3.out', onUpdate: () => b.textContent = Math.round(o.v) }) });
  });
  gsap.from('.rule-body > *', { y: 40, autoAlpha: 0, stagger: .1, duration: 1, ease: 'power3.out', scrollTrigger: { trigger: '.rule-body', start: 'top 82%' } });
}

/* ---------- hero hand-off: the paper slides over the wall; the wall stops drawing once covered ---------- */
function buildHandoff(){
  const view = $('#view'), shade = document.createElement('div');
  shade.style.cssText = 'position:absolute;inset:0;background:#000;opacity:0;pointer-events:none;z-index:8';
  view.appendChild(shade);
  gsap.timeline({ scrollTrigger: { trigger: '#rule', start: 'top bottom', end: 'top top', scrub: true } })
    .to(view, { scale: RM ? 1 : .93, ease: 'none', transformOrigin: '50% 35%' }, 0)
    .to(shade, { opacity: .75, ease: 'none' }, 0);
  ScrollTrigger.create({ trigger: '#rule', start: 'top top',
    onEnter: () => { window.heroPaused = true; view.style.visibility = 'hidden'; try { breath && breath.pause(); } catch (e) {} },
    onLeaveBack: () => { window.heroPaused = false; view.style.visibility = ''; try { breath && breath.play(); } catch (e) {} } });
}

/* ---------- sticky bar: appears after the wall, takes the colour of the section under it ---------- */
function buildBar(){
  const bar = $('#bar');
  ScrollTrigger.create({ trigger: '#rule', start: 'top 30%', onEnter: () => bar.classList.add('on'), onLeaveBack: () => bar.classList.remove('on') });
  $$('#page .sec').forEach(sec => {
    const th = sec.classList.contains('light') ? 'light' : sec.classList.contains('blue') ? 'blue' : 'dark';
    ScrollTrigger.create({ trigger: sec, start: 'top 40px', end: 'bottom 40px', onToggle: s => { if (s.isActive) bar.dataset.theme = th; } });
  });
}

/* ---------- caution tapes: drift on their own, run faster with the scroll ---------- */
function buildTapes(){
  const tts = $$('.tape .tt');
  tts.forEach(tt => { tt.innerHTML = tt.innerHTML.repeat(4); });
  const x = [0, 0]; let on = false;
  ScrollTrigger.create({ trigger: '.tapes', start: 'top bottom+=200', end: 'bottom top-=200', onToggle: s => on = s.isActive });
  gsap.ticker.add(() => {
    if (!on || RM) return;
    const boost = Math.min(9, Math.abs(lenis.velocity || 0) * .35), dir = (lenis.direction || 1);
    tts.forEach((tt, i) => {
      const w = tt.scrollWidth / 4; if (!w) return;
      x[i] += (i ? 1 : -1) * (.7 + boost) * dir;
      x[i] = ((x[i] % w) - w) % w;
      tt.style.transform = `translate3d(${x[i].toFixed(1)}px,0,0)`;
    });
  });
}

/* ---------- 02 · the pieces: vertical scroll drives a horizontal run of cards ---------- */
function layoutCardStrikes(){
  $$('.card .rt').forEach((rt, i) => {
    const w = rt.offsetWidth, h = rt.offsetHeight, p = rt.querySelector('path'), svg = rt.querySelector('svg');
    svg.setAttribute('viewBox', `0 0 ${(w + h * .4).toFixed(0)} ${h.toFixed(0)}`);
    p.setAttribute('d', wobblyLine(h * .1, h * .62, w + h * .3, h * .48, h * .18, mulberry(31 + i)));
    p.style.strokeWidth = (h * .17).toFixed(1);
    primePath(p);
  });
}
let runTween = null;
function buildPieces(){
  const track = $('.htrack'), cards = $$('.card'), hud = $('.hhud'), pi = $('.js-pi'), pbar = $('.js-pbar'), pname = $('.js-pname');
  const dist = () => Math.max(0, track.scrollWidth - innerWidth);
  const skew = gsap.quickTo(cards, 'skewX', { duration: .6, ease: 'power3' });
  let lastI = -1;
  const run = runTween = gsap.to(track, { x: () => -dist(), ease: 'none', scrollTrigger: {
    trigger: '#pieces', start: 'top top', end: () => '+=' + dist(), pin: '.hwrap', scrub: .8, anticipatePin: 1, invalidateOnRefresh: true,
    onToggle: s => hud.classList.toggle('on', s.isActive),
    onUpdate: s => {
      if (!RM) skew(clamp(-7, 7, s.getVelocity() / -420));
      pbar.style.transform = `scaleX(${s.progress.toFixed(3)})`;
      let best = 0, bd = Infinity; const mid = innerWidth / 2;
      cards.forEach((c, i) => { const r = c.getBoundingClientRect(), d = Math.abs(r.left + r.width / 2 - mid); if (d < bd){ bd = d; best = i; } });
      if (best !== lastI){ lastI = best; pi.textContent = cards[best].dataset.i; pname.textContent = cards[best].dataset.name; }
    } } });
  cards.forEach(card => {
    const ph = card.querySelector('.ph'), img = card.querySelector('img'), p = card.querySelector('.rstrike path'), rt = card.querySelector('.rt');
    gsap.fromTo(ph, { clipPath: 'inset(100% 0% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', ease: 'none',
      scrollTrigger: { trigger: card, containerAnimation: run, start: 'left 102%', end: 'left 60%', scrub: true } });
    gsap.fromTo(card.querySelector('.cinfo'), { y: 40, autoAlpha: 0 }, { y: 0, autoAlpha: 1, ease: 'none',
      scrollTrigger: { trigger: card, containerAnimation: run, start: 'left 90%', end: 'left 58%', scrub: true } });
    if (!RM) gsap.fromTo(img, { xPercent: -5 }, { xPercent: 5, ease: 'none',
      scrollTrigger: { trigger: card, containerAnimation: run, start: 'left right', end: 'right left', scrub: true } });
    // the rule gets sprayed out as the card reaches the middle of the screen
    gsap.timeline({ scrollTrigger: { trigger: card, containerAnimation: run, start: 'left 62%', end: 'left 34%', scrub: true } })
      .fromTo(p, { strokeDashoffset: () => p._L }, { strokeDashoffset: 0, ease: 'power1.inOut' })
      .to(rt, { opacity: .55, ease: 'none' }, 0);
  });
  gsap.from('.intro > *', { y: 50, autoAlpha: 0, stagger: .08, duration: 1.1, ease: 'power3.out', scrollTrigger: { trigger: '#pieces', start: 'top 70%' } });
}

/* ---------- splotch buttons, painted by the same generator as the hero's O ---------- */
const btnSplotches = [];
function makeBtnSplotch(btn, color, seed){
  const cv = btn.querySelector('canvas');
  const S = makeSplotch({ seed, w: 1.9, cx: .95, cy: .5, rx: .86, ry: .4, rot: -.05, wobble: .08, bumps: 5, edge: .06, halo: .14, grain: .006, color,
    drips: [[-.42, .36, .05, 0], [.12, .2, .04, 300], [.5, .3, .045, 150]] });
  const o = { btn, cv, S, t0: null };
  btnSplotches.push(o); return o;
}
function paintBtns(){ btnSplotches.forEach(o => { renderBase(o.S, o.cv); drawSplotch(o.S, o.cv, o.t0 === null ? 0 : Infinity); }); }
function runDrips(o){
  if (o.t0 !== null) return; o.t0 = performance.now();
  const step = () => { const t = performance.now() - o.t0; drawSplotch(o.S, o.cv, t); if (t < 4200) requestAnimationFrame(step); };
  requestAnimationFrame(step);
}
function buildBtns(){
  makeBtnSplotch($('.outro .splotch-btn'), [0, 19, 255], 41);
  makeBtnSplotch($('.rform .splotch-btn'), [255, 255, 255], 23);
  paintBtns();
  btnSplotches.forEach(o => {
    const inTrack = !!o.btn.closest('.htrack');
    ScrollTrigger.create({ trigger: o.btn, once: true, ...(inTrack ? { containerAnimation: runTween, start: 'left 85%' } : { start: 'top 92%' }),
      onEnter: () => { o.btn.animate([{ scale: .2, opacity: 0 }, { scale: 1.08, opacity: 1, offset: .6 }, { scale: 1, opacity: 1 }], { duration: 650, easing: 'cubic-bezier(.2,.8,.2,1)', fill: 'both' }); runDrips(o); } });
  });
}

/* ---------- 03 · how a suit breaks: FOUND rises, RIPPED tears in two, REWORN is sprayed back on ---------- */
function tearPaths(){
  const R = mulberry(9), pts = [];
  for (let x = 100; x >= 0; x -= 2 + R() * 3.5) pts.push([x, 52 + (R() - .5) * 13 + (R() < .15 ? (R() - .5) * 14 : 0)]);
  pts.push([0, 50]);
  const P = a => a.map(([x, y]) => `${x.toFixed(1)}% ${y.toFixed(1)}%`).join(',');
  $('.rip.top').style.clipPath = `polygon(0% -20%,100% -20%,${P(pts)})`;
  $('.rip.bot').style.clipPath = `polygon(${P(pts.slice().reverse())},100% 120%,0% 120%)`;
}
// a ripped-paper outline: every edge jitters; the photo sits a little inside so a white paper fringe shows
function tornPoly(R, inset, amp){
  const pts = [], edge = (x0, y0, x1, y1, ax, ay) => {
    for (let t = 0; t < 1; t += .025 + R() * .045){
      const j = (R() - .5) * 2 + (R() < .12 ? (R() - .5) * 2.4 : 0);
      pts.push([x0 + (x1 - x0) * t + ax * j * amp, y0 + (y1 - y0) * t + ay * j * amp]);
    }
  };
  const a = inset, b = 100 - inset;
  edge(a, a, b, a, 0, .8); edge(b, a, b, b, 1, 0); edge(b, b, a, b, 0, .8); edge(a, b, a, a, 1, 0);
  return `polygon(${pts.map(([x, y]) => `${x.toFixed(2)}% ${y.toFixed(2)}%`).join(',')})`;
}
function buildScraps(){
  $$('.scrap').forEach((sc, i) => {
    const R = mulberry(50 + i * 7);
    sc.querySelectorAll('.paper').forEach(p => { p.style.clipPath = tornPoly(mulberry(60 + i), 1.2, 1.1); });
    sc.querySelectorAll('.paper img').forEach(im => { im.style.clipPath = tornPoly(mulberry(70 + i), 4.2, 1.4); });
    // where this scrap will tear when it is ripped off the wall
    const tear = []; let y = -10;
    while (y < 110){ tear.push([46 + (R() - .5) * 14, y]); y += 3 + R() * 6; }
    tear.push([50 + (R() - .5) * 10, 112]);
    const P = a => a.map(([x, yy]) => `${x.toFixed(1)}% ${yy.toFixed(1)}%`).join(',');
    sc.querySelector('.half.a').style.clipPath = `polygon(-30% -20%,${P(tear)},-30% 120%)`;
    sc.querySelector('.half.b').style.clipPath = `polygon(130% -20%,${P(tear)},130% 120%)`;
    sc.style.rotate = ['-3deg', '2.4deg', '-1.6deg'][i];
  });
}
function buildProcess(){
  tearPaths(); buildScraps();
  gsap.set('#process .pw1 .ch', { yPercent: 105 });
  const step = $('.js-step');
  const tl = gsap.timeline({ scrollTrigger: { trigger: '#process', start: 'top top', end: () => '+=' + innerHeight * (isMob() ? 2.4 : 2.8),
    pin: '.pwrap', scrub: .7, anticipatePin: 1, invalidateOnRefresh: true,
    onUpdate: s => { step.textContent = s.progress < .37 ? '01' : s.progress < .7 ? '02' : '03'; } } });
  const show = (sel, at) => tl.fromTo(sel, { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: .22, ease: 'power2.out' }, at);
  const hide = (sel, at) => tl.to(sel, { autoAlpha: 0, y: -24, duration: .18, ease: 'power2.in' }, at);
  // a scrap is slapped onto the wall… and later ripped off it in two pieces
  const slap = (sel, at) => tl.fromTo(sel, { autoAlpha: 0, scale: 1.18, rotate: 7 }, { autoAlpha: 1, scale: 1, rotate: 0, duration: .2, ease: 'back.out(1.6)' }, at);
  const rip = (sel, at) => {
    tl.to(sel + ' .half.a', { xPercent: -5, rotate: -4, duration: .08, ease: 'power1.out' }, at)
      .to(sel + ' .half.b', { xPercent: 5, rotate: 4, duration: .08, ease: 'power1.out' }, at)
      .to(sel + ' .half.a', { xPercent: -26, yPercent: 60, rotate: -24, autoAlpha: 0, duration: .26, ease: 'power2.in' }, at + '+=.08')
      .to(sel + ' .half.b', { xPercent: 30, yPercent: 70, rotate: 28, autoAlpha: 0, duration: .26, ease: 'power2.in' }, at + '+=.08');
  };
  tl.fromTo('#process .pw1 .ch', { yPercent: 105 }, { yPercent: 0, stagger: .05, duration: .3, ease: 'power3.out' }, 0);
  slap('.scrap.s1', 0); show('.steps .s1', .1);
  tl.to({}, { duration: .35 })
    .to('#process .pw1 .ch', { yPercent: -105, stagger: .035, duration: .25, ease: 'power2.in' }, 'b');
  hide('.steps .s1', 'b'); rip('.scrap.s1', 'b');
  tl.fromTo('#process .pw2 .rip', { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: .22, ease: 'power3.out' }, 'b+=.4');
  slap('.scrap.s2', 'b+=.28'); show('.steps .s2', 'b+=.32');
  tl.to('#process .pw2 .rip.top', { yPercent: -10, xPercent: -1.4, rotate: -2.4, duration: .35, ease: 'power2.out' }, 'b+=.5')
    .to('#process .pw2 .rip.bot', { yPercent: 9, xPercent: 1.6, rotate: 1.8, duration: .35, ease: 'power2.out' }, 'b+=.5')
    .to({}, { duration: .3 })
    .to('#process .pw2 .rip', { autoAlpha: 0, duration: .18 }, 'c');
  hide('.steps .s2', 'c'); rip('.scrap.s2', 'c');
  tl.fromTo('#process .pw3 .fi', { '--sx': '-12%' }, { '--sx': '135%', duration: .45, ease: 'power1.inOut' }, 'c+=.2');
  slap('.scrap.s3', 'c+=.3'); show('.steps .s3', 'c+=.25');
  tl.to({}, { duration: .4 });
}

/* ---------- 04 · the drop ---------- */
function layoutHowLine(){
  const how = $('.how'), lis = $$('.how li'), p = $('.js-howline path'), svg = $('.js-howline');
  if (isMob()) return;
  const hr = how.getBoundingClientRect(), a = lis[0].querySelector('.hn').getBoundingClientRect(), b = lis[2].querySelector('.hn').getBoundingClientRect();
  svg.setAttribute('viewBox', `0 0 ${hr.width.toFixed(0)} ${svg.getBoundingClientRect().height.toFixed(0)}`);
  const h = svg.getBoundingClientRect().height;
  p.setAttribute('d', wobblyLine(a.left - hr.left + 4, h * .5, b.right - hr.left + innerWidth * .12, h * .4, h * .35, mulberry(77)));
  p.style.strokeWidth = Math.max(2.5, innerWidth / 640).toFixed(1);
  primePath(p);
}
function buildDrop(){
  gsap.from('.droptitle .fi', { yPercent: 105, stagger: .12, ease: 'power3.out', duration: 1.1, scrollTrigger: { trigger: '.droptitle', start: 'top 85%' } });
  gsap.from('.how li', { y: 60, autoAlpha: 0, stagger: .14, duration: 1, ease: 'power3.out', scrollTrigger: { trigger: '.how', start: 'top 80%' } });
  gsap.fromTo('.js-howline path', { strokeDashoffset: () => $('.js-howline path')._L || 0 }, { strokeDashoffset: 0, ease: 'none',
    scrollTrigger: { trigger: '.how', start: 'top 75%', end: 'top 30%', scrub: true, invalidateOnRefresh: true } });
  gsap.from('.cta > *', { y: 60, autoAlpha: 0, stagger: .12, duration: 1, ease: 'power3.out', scrollTrigger: { trigger: '.cta', start: 'top 85%' } });
}

/* ---------- live countdown everywhere (bar, big clock); evergreen: always the next Friday 18:00 Berlin ---------- */
const fmtDay = at => {
  const off = berlinOffsetMin(at), b = new Date(at + off * 60000);
  const wd = b.toLocaleDateString('en-GB', { timeZone: 'UTC', weekday: 'long' }), dd = String(b.getUTCDate()).padStart(2, '0'), mo = String(b.getUTCMonth() + 1).padStart(2, '0');
  return { long: `${wd} ${dd}.${mo}, 18:00 ${off === 60 ? 'CET' : 'CEST'}`, short: `${wd.slice(0, 3)} ${dd}.${mo} · 18:00` };
};
function tickAll(){
  const st = dropState(), f = fmtCD(st.ms), day = fmtDay(st.at);
  $('.js-cd').textContent = st.live ? 'Live now' : f.text;
  $('.js-dropday').textContent = day.short + (berlinOffsetMin(st.at) === 60 ? ' CET' : ' CEST');
  $('.js-dropday2').textContent = day.long;
  $('.js-dropday3').textContent = day.long;
  $('.js-cdlab').textContent = st.live ? 'Doors are open' : 'Doors open in';
  $('.js-cdd').textContent = String(f.d).padStart(2, '0'); $('.js-cdh').textContent = f.hh; $('.js-cdm').textContent = f.mm; $('.js-cds').textContent = f.ss;
}
tickAll(); setInterval(tickAll, 1000);

/* ---------- reserve form (front-end only: nothing is sent anywhere) ---------- */
(function form(){
  const f = $('#reserveForm'), fine = $('.js-fine'), btn = f.querySelector('.splotch-btn span');
  f.addEventListener('submit', e => {
    e.preventDefault();
    if (f.classList.contains('done')) return;
    const email = f.email.value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)){
      f.classList.add('err'); fine.textContent = 'That email doesn’t look right. One more try?'; f.email.focus(); return;
    }
    f.classList.remove('err'); f.classList.add('done');
    const opt = f.piece.selectedOptions[0], piece = f.piece.value === 'any' ? 'any piece' : opt.textContent.replace(/^\d+ — /, 'the ');
    btn.textContent = 'You’re in';
    fine.textContent = `You’re on the list for ${piece}, size ${f.size.value}. The early link lands in your inbox Friday at 17:30, half an hour before the doors open.`;
    const sb = f.querySelector('.splotch-btn'); sb.animate([{ scale: 1 }, { scale: .86, offset: .25 }, { scale: 1.12, offset: .6 }, { scale: 1 }], { duration: 700, easing: 'ease-out' });
    $('.bar-cta-l').textContent = 'Reserved ✓';
    try { const r = $('#reserve .fit'); r.textContent = 'You’re in'; fitText(); } catch (err) {}
  });
  f.email.addEventListener('input', () => { if (f.classList.contains('err')){ f.classList.remove('err'); fine.textContent = 'No spam. One email per drop. Reserving is free and doesn’t oblige you to buy.'; } });
})();

/* ---------- footer: the wordmark runs ---------- */
let wm = null;
function layoutWordmark(){
  const cv = $('.wmdrips'), w = $('.wm'), fi = $('.wordmark .fi');
  // offsets, not client rects: the wordmark may be mid-entrance (translated) when this runs
  const dpr = Math.min(2, devicePixelRatio || 1), wr = { width: w.offsetWidth }, em = parseFloat($('.wordmark').style.fontSize) || 100;
  const fr = { left: fi.offsetLeft, width: fi.offsetWidth, bottom: fi.offsetTop + fi.offsetHeight }, wrTop = 0;
  const Hc = fr.bottom + em * .6;
  cv.style.height = Hc + 'px'; cv.width = Math.round(wr.width * dpr); cv.height = Math.round(Hc * dpr);
  const R = mulberry(3), f = glyphFeet('OHSTA', em, -.05 * em);
  const pts = feetToBox(f, pickFeet(f, isMob() ? 5 : 7, em * .09, 3), em, .78, fr.width);
  const maxL = .42;
  w.style.paddingBottom = (em * (maxL + .08)).toFixed(0) + 'px';
  wm = { cv, em: em * dpr, runs: pts.map(p => ({ x: (fr.left + p.x) / em, y: (fi.offsetTop + p.y) / em - .045,
    L: .14 + R() * (maxL - .14), w: .022 + R() * .02, wob: R() * 6.28, d: R() * 900 })), t0: wm && wm.t0 };
  drawWordmark(wm.t0 ? performance.now() - wm.t0 : 0);
}
function drawWordmark(t){
  if (!wm) return;
  const ctx = wm.cv.getContext('2d'); ctx.clearRect(0, 0, wm.cv.width, wm.cv.height);
  wm.runs.forEach(r => {
    const tt = Math.max(0, t - r.d) / 1000; if (tt <= 0) return;
    const len = r.L * (1 - Math.exp(-tt / (.4 + r.L * .9)));
    drawRun(ctx, v => v * wm.em, v => v * wm.em, wm.em, r.x, r.y, Math.max(.01, len), r.L, r.w, r.wob, [255, 255, 255], false);
  });
}
function buildFooter(){
  gsap.from('.wordmark .fi', { yPercent: 40, autoAlpha: 0, duration: 1.2, ease: 'power3.out', scrollTrigger: { trigger: '.wm', start: 'top 92%' } });
  ScrollTrigger.create({ trigger: '.wm', start: 'top 70%', once: true, onEnter: () => {
    wm.t0 = performance.now();
    const step = () => { const t = performance.now() - wm.t0; drawWordmark(t); if (t < 6000) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  } });
}

/* ---------- boot ---------- */
function layout(){ fitFills(); layoutRule(); layoutCardStrikes(); layoutHowLine(); layoutWordmark(); paintBtns(); }
(async () => {
  try { await Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 2500))]); } catch (e) {}
  fitFills(); layoutRule(); layoutCardStrikes();
  buildHandoff(); buildBar(); buildRule(); buildTapes(); buildPieces(); buildBtns(); buildProcess(); buildDrop(); buildFooter();
  layoutHowLine(); layoutWordmark();
  ScrollTrigger.refresh();
  let rz, lastW = innerWidth;
  addEventListener('resize', () => {
    if (isMob() && innerWidth === lastW) return;     // phones fire resize when the address bar moves; only width matters
    lastW = innerWidth; clearTimeout(rz);
    rz = setTimeout(() => { layout(); ScrollTrigger.refresh(); }, 160);
  });
})();
})();
