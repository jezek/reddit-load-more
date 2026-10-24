const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../extension/gate.js'), 'utf8');

function fixture({page = '/', src = '/svc/shreddit/feeds/popular-feed?after=cursor',
                  slot = 'load-after', feed = true, existing = true, load} = {}) {
  const wrappers = [];
  let requests = 0;
  class Element {
    constructor(name) { this.localName = name; this.attrs = {}; this.children = []; this.listeners = {}; this.isConnected = true; }
    setAttribute(k, v) { this.attrs[k] = v; }
    getAttribute(k) { return this.attrs[k] ?? null; }
    closest() { return feed ? {} : null; }
    before(node) { wrappers.push(node); }
    append(...nodes) { this.children.push(...nodes); }
    addEventListener(k, fn) { this.listeners[k] = fn; }
    click(trusted = true) { return this.listeners.click({isTrusted: trusted}); }
  }
  class Partial extends Element {
    constructor() { super('faceplate-partial'); this.attrs = {slot, src}; }
    _loadContent(...args) { requests++; return load ? load(...args) : Promise.resolve('<article>batch</article>'); }
  }
  const registry = {ctor: existing ? Partial : null, get() { return this.ctor; },
    define(name, ctor) { this.ctor = ctor; this.upgrade?.(new ctor()); }};
  vm.runInNewContext(source, {window: {customElements: registry},
    location: new URL(page, 'https://www.reddit.com'), URL,
    document: {createElement(name) { return new Element(name); }}});
  if (!existing) registry.define('faceplate-partial', Partial);
  return {Partial, registry, wrappers, requests: () => requests,
    button: () => wrappers.at(-1).children[1], status: () => wrappers.at(-1).children[0]};
}

test('no native request until trusted choice; duplicate calls/clicks admit one batch', async () => {
  const f = fixture(); const p = new f.Partial();
  const wait = p._loadContent();
  assert.equal(wait, p._loadContent());
  assert.equal(f.wrappers.length, 1); assert.equal(f.requests(), 0);
  await f.button().click(false); assert.equal(f.requests(), 0);
  const one = f.button().click(); const two = f.button().click();
  await Promise.all([one, two]);
  assert.equal(await wait, '<article>batch</article>'); assert.equal(f.requests(), 1);
  assert.equal(f.button().hidden, true);
  new f.Partial()._loadContent();
  assert.equal(f.requests(), 1); assert.equal(f.wrappers.length, 2);
});

test('only supported feed cursor partials are paused; unrelated requests preserve return', async () => {
  const cases = [
    {name: 'home', page: '/', paused: true},
    {name: 'subreddit', page: '/r/aww/', src: '/svc/shreddit/community-more-posts/best/?after=c', paused: true},
    {name: 'sorted subreddit', page: '/r/aww/top/', paused: true},
    {name: 'comment page', page: '/r/aww/comments/abc/title/'},
    {name: 'sidebar', src: '/svc/shreddit/feeds/subreddit-right-rail?after=c'},
    {name: 'initial batch', src: '/svc/shreddit/feeds/popular-feed'},
    {name: 'empty cursor', src: '/svc/shreddit/feeds/popular-feed?after='},
    {name: 'other origin', src: 'https://other.example/svc/shreddit/feeds/popular-feed?after=c'},
    {name: 'not feed slot', slot: 'load-before'},
    {name: 'not feed descendant', feed: false},
    {name: 'login partial', src: '/svc/shreddit/partial/id/login?after=c'},
    {name: 'media', src: '/image.png?after=c'},
  ];
  for (const c of cases) {
    const f = fixture(c); const result = new f.Partial()._loadContent();
    assert.equal(f.requests(), c.paused ? 0 : 1, c.name);
    if (!c.paused) assert.equal(await result, '<article>batch</article>', c.name);
  }
});

test('failed response is retryable without rejecting the waiting native loader', async () => {
  let attempt = 0;
  const f = fixture({load: () => {if (++attempt === 1) throw Error('offline'); return 'recovered';}});
  const waiting = new f.Partial()._loadContent();
  await f.button().click();
  assert.equal(f.button().disabled, false); assert.match(f.status().textContent, /retry/);
  await f.button().click(); assert.equal(await waiting, 'recovered'); assert.equal(f.requests(), 2);
});

test('late definition is patched before native upgrade calls the loader', () => {
  const f = fixture({existing: false});
  f.registry.upgrade = p => {p._loadContent();};
  // A second ctor, defined after script registration, simulates a new page bundle.
  class Later extends f.Partial { _loadContent() { return super._loadContent(); } }
  f.registry.define('faceplate-partial', Later);
  assert.equal(f.requests(), 0); assert.equal(f.wrappers.length, 1);
});

test('detached gate cannot load after navigation', async () => {
  const f = fixture(); const p = new f.Partial(); p._loadContent(); p.isConnected = false;
  await f.button().click(); assert.equal(f.requests(), 0);
});
