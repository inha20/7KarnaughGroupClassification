/* S₄ 궤도 분류 강의 — 상호작용 (일반 스크립트: file:// 에서도 동작) */
(function () {
  'use strict';
  var doc = document, root = doc.documentElement, body = doc.body;
  function $(s, c) { return (c || doc).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); }
  function ls(k, v) { try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { } return null; }
  function fmt(sec) { sec = Math.max(0, Math.round(sec)); var m = Math.floor(sec / 60), s = sec % 60; return m + ':' + (s < 10 ? '0' : '') + s; }
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------- 화면 색상 ---------------- */
  var saved = ls('s4orb-theme');
  if (saved === 'light' || saved === 'dark') root.setAttribute('data-theme', saved);
  function isDark() {
    var t = root.getAttribute('data-theme');
    if (t) return t === 'dark';
    return !!(window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches);
  }
  function syncThemeBtns() { $$('[data-act="theme"]').forEach(function (b) { b.setAttribute('aria-pressed', isDark() ? 'true' : 'false'); }); }
  syncThemeBtns();
  if (window.matchMedia) { try { matchMedia('(prefers-color-scheme: dark)').addEventListener('change', syncThemeBtns); } catch (e) { } }

  /* ---------------- 노트 보이기/숨기기 ---------------- */
  if (ls('s4orb-notes') === 'off') body.classList.add('hide-notes');
  function syncNotesBtns() { $$('[data-act="notes"]').forEach(function (b) { b.setAttribute('aria-pressed', body.classList.contains('hide-notes') ? 'false' : 'true'); }); }
  syncNotesBtns();

  /* ---------------- 차트 툴팁 ---------------- */
  var tipEl = null;
  function tip() { if (!tipEl) { tipEl = doc.createElement('div'); tipEl.className = 'tip'; tipEl.setAttribute('role', 'tooltip'); tipEl.hidden = true; body.appendChild(tipEl); } return tipEl; }
  function showTip(t, x, y) { var el = tip(); el.textContent = t; el.hidden = false; var w = el.offsetWidth, h = el.offsetHeight; var nx = Math.min(Math.max(8, x - w / 2), window.innerWidth - w - 8); var ny = y - h - 12; if (ny < 8) ny = y + 18; el.style.left = nx + 'px'; el.style.top = ny + 'px'; }
  function hideTip() { if (tipEl) tipEl.hidden = true; }
  doc.addEventListener('pointermove', function (e) { var b = e.target.closest && e.target.closest('.cbar'); if (b) showTip(b.getAttribute('data-tip'), e.clientX, e.clientY); else hideTip(); });
  doc.addEventListener('focusin', function (e) { var b = e.target.closest && e.target.closest('.cbar'); if (b) { var r = b.getBoundingClientRect(); showTip(b.getAttribute('data-tip'), r.left + r.width / 2, r.top); } });
  doc.addEventListener('focusout', hideTip);

  /* ---------------- 위젯: 4변수 함수 격자 (슬라이드 5) ---------------- */
  $$('[data-widget="bitgrid"]').forEach(function (box) {
    var cells = $$('.bit', box), out = $('.bitout', box);
    function get() { return cells.map(function (c) { return c.getAttribute('aria-pressed') === 'true' ? 1 : 0; }); }
    function render() {
      var v = get(), str = [], ones = [];
      for (var g = 0; g < 4; g++) str.push(v.slice(g * 4, g * 4 + 4).join(''));
      v.forEach(function (x, i) { if (x) ones.push(i); });
      var name = ones.length === 0 ? '상수 0' : (ones.length === 16 ? '상수 1' : 'm(' + ones.join(', ') + ')');
      out.innerHTML = '현재 함수 <span class="mono">' + str.join(' ') + '</span> = ' + name;
      cells.forEach(function (c, i) { c.setAttribute('aria-label', '입력점 ' + ('0000' + i.toString(2)).slice(-4) + ', 함수값 ' + v[i]); c.firstChild.textContent = v[i]; });
    }
    function set(arr) { cells.forEach(function (c, i) { c.setAttribute('aria-pressed', arr[i] ? 'true' : 'false'); }); render(); }
    cells.forEach(function (c) { c.addEventListener('click', function () { c.setAttribute('aria-pressed', c.getAttribute('aria-pressed') === 'true' ? 'false' : 'true'); render(); }); });
    box.addEventListener('click', function (e) {
      var b = e.target.closest('[data-act]'); if (!b) return; var a = b.getAttribute('data-act');
      if (a === 'xor') set(cells.map(function (_, i) { var n = 0, x = i; while (x) { n += x & 1; x >>= 1; } return n & 1; }));
      if (a === 'zero') set(cells.map(function () { return 0; }));
      if (a === 'rand') set(cells.map(function () { return Math.random() < 0.5 ? 1 : 0; }));
    });
    render();
  });

  /* ---------------- 위젯: 상집합 (슬라이드 28) ---------------- */
  $$('[data-widget="hasse"]').forEach(function (box) {
    var slide = box.closest('.slide') || doc;
    var nodes = $$('.hn', box), msg = $('.hasse-msg', box), rows = $$('#upset-table tbody tr', slide);
    var anc = { a: [], b: ['a'], c: ['b', 'a'], d: ['b', 'a'], e: ['c', 'd', 'b', 'a'], f: ['e', 'c', 'd', 'b', 'a'] };
    var lab = {}; nodes.forEach(function (n) { lab[n.getAttribute('data-node')] = n.getAttribute('aria-label'); });
    function sel() { return nodes.filter(function (n) { return n.classList.contains('on'); }).map(function (n) { return n.getAttribute('data-node'); }); }
    function render() {
      var s = sel(), set = {}; s.forEach(function (k) { set[k] = 1; });
      var missing = {}, firstBad = null;
      s.forEach(function (k) { anc[k].forEach(function (a) { if (!set[a]) { missing[a] = 1; if (!firstBad) firstBad = [k, a]; } }); });
      var ok = Object.keys(missing).length === 0;
      nodes.forEach(function (n) { var k = n.getAttribute('data-node'); n.classList.toggle('bad', !!missing[k]); n.setAttribute('aria-pressed', set[k] ? 'true' : 'false'); });
      rows.forEach(function (r) { r.classList.remove('cur'); });
      if (ok) {
        var sig = s.slice().sort().join(',');
        var hit = rows.filter(function (r) { return r.getAttribute('data-sig') === sig; })[0];
        if (hit) hit.classList.add('cur');
        msg.innerHTML = '<b class="ok">상집합입니다.</b> ' + (hit ? '표의 ' + hit.firstElementChild.textContent + '번에 해당합니다.' : '');
      } else {
        msg.innerHTML = '<b class="no">상집합이 아닙니다.</b> ' + lab[firstBad[0]] + '가 들어 있으면 그보다 큰 ' + lab[firstBad[1]] + '도 들어 있어야 합니다.';
      }
    }
    nodes.forEach(function (n) {
      function tg() { n.classList.toggle('on'); render(); }
      n.addEventListener('click', tg);
      n.addEventListener('keydown', function (e) { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); tg(); } });
    });
    render();
  });

  /* ---------------- 발표 모드 ---------------- */
  var deck = $('#deck');
  var sws = deck ? Array.prototype.slice.call(deck.children).filter(function (c) { return c.classList.contains('sw'); }) : [];
  var P = { on: false, i: 0, step: 0, drawer: false, idleT: 0, timer: null, t0: 0, acc: 0, running: false, total: 0, cum: [], ended: false };
  var hud = null, dial = null, live = null, drawerEl = null, endEl = null, helpEl = null;
  if (deck) {
    var tot = 0;
    sws.forEach(function (s) { tot += +s.getAttribute('data-budget') || 0; P.cum.push(tot); });
    P.total = +deck.getAttribute('data-total') || tot;
  }
  function slideEl(i) { return $('.slide', sws[i]); }
  function maxStep(i) { return +slideEl(i).getAttribute('data-steps') || 0; }
  function elapsed() { return P.acc + (P.running ? (performance.now() - P.t0) / 1000 : 0); }

  function buildHud() {
    hud = doc.createElement('div'); hud.className = 'hud';
    var R = 26, C = 2 * Math.PI * R, ticks = '';
    P.cum.slice(0, -1).forEach(function (c) {
      var a = c / P.total * 2 * Math.PI - Math.PI / 2, x1 = 32 + Math.cos(a) * (R - 5), y1 = 32 + Math.sin(a) * (R - 5), x2 = 32 + Math.cos(a) * (R + 5), y2 = 32 + Math.sin(a) * (R + 5);
      ticks += '<line class="tick" x1="' + x1.toFixed(1) + '" y1="' + y1.toFixed(1) + '" x2="' + x2.toFixed(1) + '" y2="' + y2.toFixed(1) + '"/>';
    });
    var title = deck.getAttribute('data-title') || '';
    hud.innerHTML =
      '<div class="hud-top"><div class="hud-title">' + title + '</div>' +
      '<button type="button" class="dial" aria-label="타이머. 누르면 멈춤 또는 다시 시작"><svg viewBox="0 0 64 64" aria-hidden="true"><circle class="track" cx="32" cy="32" r="' + R + '"/>' + ticks +
      '<circle class="prog" cx="32" cy="32" r="' + R + '" stroke-dasharray="' + C.toFixed(2) + '" stroke-dashoffset="' + C.toFixed(2) + '"/><circle class="dotp" r="4.5" cx="32" cy="6"/><text class="t" x="32" y="36" text-anchor="middle">0:00</text></svg><small></small></button></div>' +
      '<div class="hud-bar" role="toolbar" aria-label="발표 조작">' +
      '<button type="button" class="btn" data-hud="prev" aria-label="이전">◀</button><span class="pos" aria-hidden="true"></span><button type="button" class="btn" data-hud="next" aria-label="다음">▶</button>' +
      '<button type="button" class="btn" data-hud="notes" aria-pressed="false">노트</button>' +
      '<button type="button" class="btn" data-hud="fs">전체화면</button>' +
      '<button type="button" class="btn" data-hud="help" aria-label="단축키">?</button>' +
      '<button type="button" class="btn" data-hud="exit">종료</button></div>' +
      '<div class="sr" aria-live="polite" id="live"></div>';
    body.appendChild(hud);
    dial = $('.dial', hud); live = $('#live', hud);
    hud.addEventListener('click', function (e) {
      var d = e.target.closest('.dial'); if (d) { toggleTimer(); return; }
      var b = e.target.closest('[data-hud]'); if (!b) return; var a = b.getAttribute('data-hud');
      if (a === 'prev') prev(); else if (a === 'next') next(); else if (a === 'notes') toggleDrawer(); else if (a === 'fs') fullscreen(); else if (a === 'help') toggleHelp(); else if (a === 'exit') exitPresent();
    });
  }
  function toggleTimer() { if (P.running) { P.acc = elapsed(); P.running = false; } else { P.t0 = performance.now(); P.running = true; } paintDial(); }
  function paintDial() {
    if (!dial) return;
    var t = elapsed(), R = 26, C = 2 * Math.PI * R, f = Math.min(t / P.total, 1);
    $('.prog', dial).setAttribute('stroke-dashoffset', (C * (1 - f)).toFixed(2));
    var a = f * 2 * Math.PI - Math.PI / 2;
    var dp = $('.dotp', dial); dp.setAttribute('cx', (32 + Math.cos(a) * R).toFixed(1)); dp.setAttribute('cy', (32 + Math.sin(a) * R).toFixed(1));
    var left = P.total - t;
    $('.t', dial).textContent = (left < 0 ? '+' : '') + fmt(Math.abs(left));
    var goal = P.cum[P.i] || P.total, diff = t - goal;
    $('small', dial).textContent = '목표 ' + fmt(goal) + (diff > 5 ? ' · +' + fmt(diff) : '');
    dial.classList.toggle('over', t > P.total || (diff > 5 && P.i === sws.length - 1));
    dial.classList.toggle('paused', !P.running);
  }

  function layout() {
    if (!P.on) return;
    var dw = P.drawer ? Math.min(420, window.innerWidth * 0.92) : 0;
    var s = Math.min((window.innerWidth - dw) / 1280, window.innerHeight / 720);
    root.style.setProperty('--sc', Math.max(0.15, s).toFixed(4));
    root.style.setProperty('--dx', dw + 'px');
  }
  function setCur(i, step) {
    P.i = Math.max(0, Math.min(sws.length - 1, i)); P.step = step || 0; P.ended = false;
    sws.forEach(function (s, k) { s.classList.toggle('cur', k === P.i); });
    applySteps(); layout(); fitSlide(slideEl(P.i)); paintDial();
    var sl = slideEl(P.i), ms = maxStep(P.i);
    var pos = $('.pos', hud); if (pos) pos.textContent = (P.i + 1) + ' / ' + sws.length + (ms ? ' · ' + P.step + '/' + ms : '');
    if (live) live.textContent = '슬라이드 ' + sl.getAttribute('data-n') + ', ' + $('.s-title', sl).textContent + (ms ? ', 단계 ' + P.step + ' / ' + ms : '');
    if (P.drawer) fillDrawer();
    try { history.replaceState(null, '', '#present-' + sl.id); } catch (e) { }
  }
  /* 슬라이드 글자 크기 자동 맞춤: 1280×720 무대에 내용이 다 들어가는 가장 큰 글자 크기를 고른다 */
  var FIT_MIN = 14, FIT_LIMIT = 686;
  function fitSlide(sl, force) {
    if (!sl) return;
    if (force) { sl.removeAttribute('data-fit'); }
    var saved = sl.getAttribute('data-fit');
    if (saved) { sl.style.fontSize = saved + 'px'; return; }
    sl.style.fontSize = '';
    var base = parseFloat(getComputedStyle(sl).fontSize) || 22;
    var box = $('.s-body', sl);
    function over() {
      var r = sl.getBoundingClientRect(); if (!r.height) return false;
      var sc = r.height / 720, b = box.getBoundingClientRect();
      return (b.bottom - r.top) / sc > FIT_LIMIT;
    }
    if (!over()) { sl.setAttribute('data-fit', base); return; }
    var lo = FIT_MIN, hi = base;
    for (var k = 0; k < 8; k++) { var mid = (lo + hi) / 2; sl.style.fontSize = mid.toFixed(2) + 'px'; if (over()) hi = mid; else lo = mid; }
    sl.style.fontSize = lo.toFixed(2) + 'px'; sl.setAttribute('data-fit', lo.toFixed(2));
  }
  if (doc.fonts && doc.fonts.ready) { doc.fonts.ready.then(function () { if (P.on) fitSlide(slideEl(P.i), true); }); }
  function applySteps() {
    var sl = slideEl(P.i);
    $$('[data-step]', sl).forEach(function (n) { n.classList.toggle('later', (+n.getAttribute('data-step')) > P.step); });
  }
  function next() {
    if (!P.on) return;
    if (endEl) { return; }
    var ms = maxStep(P.i);
    if (P.step < ms) { P.step++; applySteps(); updatePos(); return; }
    if (P.i < sws.length - 1) setCur(P.i + 1, 0); else showEnd();
  }
  function prev() {
    if (!P.on) return;
    if (endEl) { closeEnd(); return; }
    if (P.step > 0) { P.step--; applySteps(); updatePos(); return; }
    if (P.i > 0) setCur(P.i - 1, maxStep(P.i - 1));
  }
  function updatePos() { var ms = maxStep(P.i), pos = $('.pos', hud); if (pos) pos.textContent = (P.i + 1) + ' / ' + sws.length + (ms ? ' · ' + P.step + '/' + ms : ''); if (live) live.textContent = '단계 ' + P.step + ' / ' + ms; }
  function enterPresent(i) {
    if (!deck || P.on) return;
    if (!hud) buildHud();
    P.on = true; body.classList.add('present'); hud.classList.remove('idle');
    P.acc = 0; P.t0 = performance.now(); P.running = true;
    setCur(i || 0, 0);
    clearInterval(P.timer); P.timer = setInterval(paintDial, 500);
    wake();
  }
  function exitPresent() {
    if (!P.on) return;
    var id = slideEl(P.i).id;
    closeEnd(); closeHelp(); closeDrawer();
    P.on = false; body.classList.remove('present'); clearInterval(P.timer); P.running = false;
    root.style.removeProperty('--sc'); root.style.removeProperty('--dx');
    if (doc.fullscreenElement && doc.exitFullscreen) { try { var fr = doc.exitFullscreen(); if (fr && fr.catch) fr.catch(function () { }); } catch (e) { } }
    try { history.replaceState(null, '', '#' + id); } catch (e) { }
    var el = doc.getElementById(id); if (el) el.scrollIntoView({ block: 'start' });
  }
  function fullscreen() {
    try {
      var r = doc.fullscreenElement ? doc.exitFullscreen() : (root.requestFullscreen ? root.requestFullscreen() : null);
      if (r && r.catch) r.catch(function () { });   /* 전체화면이 막힌 환경(iframe 등)에서는 조용히 무시 */
    } catch (e) { }
  }
  function fillDrawer() {
    var n = $('.notes', sws[P.i]);
    drawerEl.innerHTML = '<h3>발표자 노트 · 슬라이드 ' + slideEl(P.i).getAttribute('data-n') + '</h3>' + (n ? n.innerHTML.replace(/^\s*<h3>.*?<\/h3>/, '') : '<p>이 슬라이드에는 노트가 없습니다.</p>');
  }
  function toggleDrawer() { if (P.drawer) closeDrawer(); else openDrawer(); }
  function openDrawer() { if (!drawerEl) { drawerEl = doc.createElement('aside'); drawerEl.className = 'drawer'; drawerEl.setAttribute('aria-label', '발표자 노트'); body.appendChild(drawerEl); } P.drawer = true; drawerEl.hidden = false; fillDrawer(); var b = $('[data-hud="notes"]', hud); if (b) b.setAttribute('aria-pressed', 'true'); layout(); }
  function closeDrawer() { if (!P.drawer) return; P.drawer = false; if (drawerEl) drawerEl.hidden = true; var b = hud && $('[data-hud="notes"]', hud); if (b) b.setAttribute('aria-pressed', 'false'); layout(); }
  function showEnd() {
    if (endEl) return;
    var t = elapsed(); P.ended = true;
    var q = deck.getAttribute('data-q') || '', a = deck.getAttribute('data-a') || '', nx = deck.getAttribute('data-next') || '', nxt = deck.getAttribute('data-next-title') || '';
    endEl = doc.createElement('div'); endEl.className = 'overlay'; endEl.setAttribute('role', 'dialog'); endEl.setAttribute('aria-modal', 'true'); endEl.setAttribute('aria-label', '발표 끝');
    endEl.innerHTML = '<div class="ov-card"><h2>발표 끝</h2><p class="stats">걸린 시간 ' + fmt(t) + ' · 계획 ' + fmt(P.total) + '</p>' +
      '<div class="qa"><p><span class="tag">질문</span><span class="q">' + q + '</span></p><p class="a"><span class="tag">답</span><span>' + a + '</span></p></div>' +
      '<div class="ov-actions"><button type="button" class="btn" data-ov="again">처음부터 다시</button>' +
      (nx ? '<a class="btn primary" href="' + nx + '#present">다음 발표: ' + nxt + '</a>' : '') +
      '<button type="button" class="btn" data-ov="exit">발표 종료</button></div></div>';
    body.appendChild(endEl);
    endEl.addEventListener('click', function (e) { var b = e.target.closest('[data-ov]'); if (!b) return; if (b.getAttribute('data-ov') === 'again') { closeEnd(); P.acc = 0; P.t0 = performance.now(); P.running = true; setCur(0, 0); } else { exitPresent(); } });
    var f = $('.btn', endEl); if (f) f.focus();
    P.acc = t; P.running = false; paintDial();
  }
  function closeEnd() { if (endEl) { endEl.remove(); endEl = null; P.ended = false; } }
  function toggleHelp() { if (helpEl) closeHelp(); else openHelp(); }
  function openHelp() {
    helpEl = doc.createElement('div'); helpEl.className = 'overlay'; helpEl.setAttribute('role', 'dialog'); helpEl.setAttribute('aria-modal', 'true'); helpEl.setAttribute('aria-label', '단축키');
    helpEl.innerHTML = '<div class="ov-card"><h2>단축키</h2><div class="keytable">' +
      '<span><kbd>→</kbd> <kbd>Space</kbd> <kbd>PageDown</kbd></span><span>다음 단계 또는 다음 슬라이드</span>' +
      '<span><kbd>←</kbd> <kbd>PageUp</kbd></span><span>이전 단계 또는 이전 슬라이드</span>' +
      '<span><kbd>Home</kbd> <kbd>End</kbd></span><span>처음 / 끝 슬라이드</span>' +
      '<span><kbd>N</kbd></span><span>발표자 노트 열기·닫기</span>' +
      '<span><kbd>P</kbd></span><span>타이머 멈춤·재개 (원 모양 시계를 눌러도 됩니다)</span>' +
      '<span><kbd>F</kbd></span><span>전체화면</span>' +
      '<span><kbd>Esc</kbd></span><span>발표 종료</span></div>' +
      '<div class="ov-actions"><button type="button" class="btn primary" data-ov="close">닫기</button></div></div>';
    body.appendChild(helpEl);
    helpEl.addEventListener('click', function (e) { if (e.target === helpEl || e.target.closest('[data-ov="close"]')) closeHelp(); });
    $('.btn', helpEl).focus();
  }
  function closeHelp() { if (helpEl) { helpEl.remove(); helpEl = null; } }
  function wake() { if (!hud) return; hud.classList.remove('idle'); clearTimeout(P.idleT); P.idleT = setTimeout(function () { if (P.on && !hud.contains(doc.activeElement)) hud.classList.add('idle'); }, 3200); }

  /* ---------------- 입력 ---------------- */
  doc.addEventListener('click', function (e) {
    var a = e.target.closest('[data-act]');
    if (a) {
      var act = a.getAttribute('data-act');
      if (act === 'theme') { var d = !isDark(); root.setAttribute('data-theme', d ? 'dark' : 'light'); ls('s4orb-theme', d ? 'dark' : 'light'); syncThemeBtns(); }
      else if (act === 'notes') { body.classList.toggle('hide-notes'); ls('s4orb-notes', body.classList.contains('hide-notes') ? 'off' : 'on'); syncNotesBtns(); }
      else if (act === 'present') { enterPresent(0); }
      else if (act === 'present-here') { var sw = a.closest('.sw'); enterPresent(sws.indexOf(sw)); }
    }
  });
  doc.addEventListener('keydown', function (e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    var tag = (e.target.tagName || '').toLowerCase();
    var k = e.key;
    if (!P.on) {
      if ((k === 'p' || k === 'P') && deck && tag !== 'input' && tag !== 'textarea') { enterPresent(0); e.preventDefault(); }
      return;
    }
    wake();
    if (helpEl) { if (k === 'Escape' || k === '?') { closeHelp(); e.preventDefault(); } return; }
    if (k === 'Escape') { if (endEl) { closeEnd(); } else if (P.drawer) { closeDrawer(); } else { exitPresent(); } e.preventDefault(); return; }
    var onBtn = tag === 'button' || tag === 'a' || tag === 'summary';
    if (k === 'ArrowRight' || k === 'ArrowDown' || k === 'PageDown' || (k === ' ' && !onBtn)) { next(); e.preventDefault(); }
    else if (k === 'ArrowLeft' || k === 'ArrowUp' || k === 'PageUp' || k === 'Backspace') { prev(); e.preventDefault(); }
    else if (k === 'Home') { closeEnd(); setCur(0, 0); e.preventDefault(); }
    else if (k === 'End') { closeEnd(); setCur(sws.length - 1, maxStep(sws.length - 1)); e.preventDefault(); }
    else if (k === 'n' || k === 'N') { toggleDrawer(); }
    else if (k === 'p' || k === 'P') { toggleTimer(); }
    else if (k === 'f' || k === 'F') { fullscreen(); }
    else if (k === '?') { toggleHelp(); }
  });
  doc.addEventListener('mousemove', function () { if (P.on) wake(); });
  var tx = null, ty = null;
  doc.addEventListener('touchstart', function (e) { if (!P.on || e.touches.length !== 1) return; tx = e.touches[0].clientX; ty = e.touches[0].clientY; }, { passive: true });
  doc.addEventListener('touchend', function (e) {
    if (!P.on || tx === null) return;
    var dx = e.changedTouches[0].clientX - tx, dy = e.changedTouches[0].clientY - ty; tx = null;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) { if (dx < 0) next(); else prev(); }
  }, { passive: true });
  window.addEventListener('resize', layout);
  doc.addEventListener('fullscreenchange', layout);

  /* ---------------- 주소 해시 ---------------- */
  function route() {
    var h = location.hash || '';
    if (!deck) return;
    var m = /^#present(?:-(s\d+))?$/.exec(h);
    if (m) {
      var idx = 0;
      if (m[1]) sws.forEach(function (s, k) { if (slideEl(k).id === m[1]) idx = k; });
      if (P.on) setCur(idx, 0); else enterPresent(idx);
    } else if (P.on && h) {
      exitPresent();
    }
  }
  window.addEventListener('hashchange', route);
  route();
})();
