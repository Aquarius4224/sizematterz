// ---- opening title: SIZE MATTERZ, from Chiu's layered artwork. It pops in, the I and the snake squirt, then the TT holes clench twice ----
function showTitle(done) {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches, A = TITLE_ART;
  const ov = document.createElement('div'); ov.id = 'titleOv';
  ov.innerHTML = '<div class="tbox"></div><div class="skip">點一下跳過</div>';
  const box = ov.querySelector('.tbox'), P = {};
  const pc = (v, t) => (v / t * 100) + '%';
  for (const l of A.L) {
    const d = document.createElement('div'); d.className = 'tl';
    Object.assign(d.style, { left: pc(l.x, A.W), top: pc(l.y, A.H), width: pc(l.w, A.W), height: pc(l.h, A.H), opacity: 0 });
    const im = new Image(); im.src = l.src; im.alt = ''; im.draggable = false; d.appendChild(im);
    box.appendChild(d); P[l.id] = { el: d, l };
  }
  box.setAttribute('role', 'img'); box.setAttribute('aria-label', 'SIZE MATTERZ');
  // a lid over each hole: a ring of the letter's own rim colour that closes in when the hole clenches
  const lids = {};
  for (const [id, h] of Object.entries(A.holes)) {
    const p = P[id], l = p.l, lid = document.createElement('div'); lid.className = 'lid';
    Object.assign(lid.style, { left: pc(h.x - h.rx - l.x, l.w), top: pc(h.y - h.ry - l.y, l.h), width: pc(2 * h.rx, l.w), height: pc(2 * h.ry, l.h) });
    lid.style.setProperty('--c', h.col); lid.style.setProperty('--r', '100%');
    p.el.appendChild(lid); lids[id] = lid;
  }
  document.body.appendChild(ov);
  // every piece scales about a point given in canvas px
  const piece = (id, ox, oy) => {
    const { el, l } = P[id];
    el.style.transformOrigin = `${pc(ox - l.x, l.w)} ${pc(oy - l.y, l.h)}`;
    return { el, animate: (k, o) => el.animate(k, o) };
  };
  const bottom = id => { const l = P[id].l; return [l.x + l.w / 2, l.y + l.h]; };
  const centre = id => { const l = P[id].l; return [l.x + l.w / 2, l.y + l.h / 2]; };
  const back = piece('back', A.W / 2, A.H / 2);
  const L1 = ['S', 'I', 'Z1', 'E1'].map(n => piece(n, ...bottom(n)));
  const L2 = ['M', 'A', 'T1', 'T2', 'E2', 'R', 'Z2'].map(n => piece(n, ...bottom(n)));
  const snake = piece('snake', 1085, 330);
  const sp = piece('splashP', A.holes.I.x, A.holes.I.y), sb = piece('splashB', 1330, 300);
  const marks = ['mL1', 'mL2', 'mR1', 'mR2'].map(n => piece(n, ...centre(n)));
  let finished = false; const timers = [];
  const finish = () => { if (finished) return; finished = true; timers.forEach(clearTimeout); ov.classList.add('out'); setTimeout(() => ov.remove(), 550); done && done(); };
  ov.addEventListener('click', finish);
  const later = (ms, f) => timers.push(setTimeout(f, ms));
  const squash = (p, ms, delay, amt) => p.animate([{ transform: 'scale(1,1)', opacity: 1 }, { transform: `scale(${1 + amt * .6},${1 - amt})`, opacity: 1, offset: .35 }, { transform: `scale(${1 - amt * .2},${1 + amt * .25})`, opacity: 1, offset: .7 }, { transform: 'scale(1,1)', opacity: 1 }], { duration: ms, delay, easing: 'ease-out', composite: 'replace' });
  const D = reduce ? 0 : 1;
  // 0) the sticker plate swells in
  back.animate([{ transform: 'scale(.82)', opacity: 0 }, { transform: 'scale(1.03)', opacity: 1, offset: .6 }, { transform: 'none', opacity: 1 }], { duration: D ? 420 : 1, easing: 'cubic-bezier(.2,.9,.3,1.2)', fill: 'forwards' });
  // 1) the letters pop in one by one
  [...L1, ...L2].forEach((p, i) => p.animate([
    { transform: 'translateY(40px) scale(0) rotate(-12deg)', opacity: 0 },
    { transform: 'translateY(-16px) scale(1.2) rotate(4deg)', opacity: 1, offset: .55 },
    { transform: 'translateY(5px) scale(.94) rotate(-1deg)', opacity: 1, offset: .78 },
    { transform: 'none', opacity: 1 }], { duration: D ? 520 : 1, delay: D * (160 + i * 85), easing: 'cubic-bezier(.2,.9,.3,1.2)', fill: 'forwards' }));
  snake.animate([{ transform: 'scale(0,.4)', opacity: 0 }, { transform: 'scale(1.08,1.05)', opacity: 1, offset: .65 }, { transform: 'none', opacity: 1 }], { duration: D ? 560 : 1, delay: D * 560, easing: 'cubic-bezier(.2,.9,.3,1.2)', fill: 'forwards' });
  marks.forEach((p, i) => p.animate([{ opacity: 0, transform: 'scale(0)' }, { opacity: 1, transform: 'scale(1.25)', offset: .6 }, { opacity: 1, transform: 'none' }], { duration: 380, delay: D * (950 + i * 60), fill: 'forwards' }));
  // 2) the I and the snake's head squirt together
  later(D * 1250, () => {
    [sp, sb].forEach(p => p.animate([
      { transform: 'scale(0)', opacity: 0 }, { transform: 'scale(.55,1.15)', opacity: 1, offset: .3 },
      { transform: 'scale(1.12,.96)', opacity: 1, offset: .62 }, { transform: 'scale(.97,1.02)', opacity: 1, offset: .82 }, { transform: 'none', opacity: 1 }],
      { duration: D ? 620 : 1, easing: 'cubic-bezier(.2,.8,.3,1)', fill: 'forwards' }));
    [sp, sb].forEach((p, i) => p.animate([{ transform: 'none' }, { transform: 'scale(1.03,.98)' }, { transform: 'none' }], { duration: 700, delay: 640 + i * 120, iterations: Infinity, composite: 'add' }));
    squash(L1[1], 420, 0, .1); squash(snake, 420, 0, .07);
  });
  // 3) the two holes on TT clench twice: the lid ring closes to a pinhole and opens again
  const clench = (lid, ms) => {
    const t0 = performance.now(), K = [[0, 100], [.22, 22], [.45, 104], [.68, 22], [1, 100]];
    const step = now => {
      const t = Math.min(1, (now - t0) / ms); let i = 0; while (K[i + 1][0] < t) i++;
      const u = (t - K[i][0]) / (K[i + 1][0] - K[i][0]), e = u * u * (3 - 2 * u);
      lid.style.setProperty('--r', (K[i][1] + (K[i + 1][1] - K[i][1]) * e) + '%');
      if (t < 1 && !finished) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  later(D * 2050, () => [['T1', L2[2]], ['T2', L2[3]]].forEach(([n, t]) => {
    clench(lids[n], 900);
    squash(t, 450, 0, .06); squash(t, 450, 450, .06);
  }));
  later(reduce ? 1800 : 3900, () => { if (!window.__titleHold) finish(); });
}
