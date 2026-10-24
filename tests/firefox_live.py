#!/usr/bin/env python3
"""Read-only Reddit acceptance in a disposable system Firefox; no third-party modules."""
import argparse
import base64
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import time
import urllib.error
import urllib.request

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--evidence', type=Path, required=True)
parser.add_argument('--pages', nargs='+', choices=['home', 'subreddit'], default=['home', 'subreddit'])
args = parser.parse_args()
evidence = args.evidence.resolve()
evidence.mkdir(mode=0o700, parents=True, exist_ok=False)
os.umask(0o077)

def interrupted(_signum, _frame):
    raise RuntimeError('bounded-test-interrupted')

signal.signal(signal.SIGTERM, interrupted)
signal.signal(signal.SIGALRM, interrupted)
signal.alarm(150)
sock = socket.socket()
sock.bind(('127.0.0.1', 0))
port = sock.getsockname()[1]
sock.close()
base = f'http://127.0.0.1:{port}'
log = (evidence / 'geckodriver.log').open('w')
driver = subprocess.Popen(['/usr/bin/geckodriver', '--allow-system-access', '--host',
                           '127.0.0.1', '--port', str(port)], stdout=log, stderr=subprocess.STDOUT)
sid = None
result = {'ok': False, 'requestedPages': args.pages, 'fullTargetCovered': False, 'pages': {}, 'driverPID': driver.pid}

def request(method, path, body=None, timeout=65):
    data = None if body is None else json.dumps(body).encode()
    query = urllib.request.Request(base + path, data, {'Content-Type': 'application/json'}, method=method)
    try:
        with urllib.request.urlopen(query, timeout=timeout) as response:
            value = json.load(response)['value']
    except urllib.error.HTTPError as error:
        raise RuntimeError(error.read().decode()) from error
    if isinstance(value, dict) and value.get('error'):
        raise RuntimeError(value)
    return value

def post(path, body):
    return request('POST', '/session/' + sid + path, body)

def js(script):
    return post('/execute/sync', {'script': script, 'args': []})

def snapshot():
    return js("""const feed=document.querySelector('shreddit-feed');
    return {url:location.origin+location.pathname, title:document.title,
      posts:feed?.querySelectorAll('shreddit-post').length || 0,
      buttons:[...document.querySelectorAll('.reddit-load-more-button')].filter(b=>!b.hidden).length,
      requests:performance.getEntriesByType('resource').filter(e=> {
        const u=new URL(e.name);return u.origin===location.origin &&
        (u.pathname.includes('/feeds/') || u.pathname.includes('/community-more-posts/')) && u.searchParams.has('after');
      }).map(e=>({path:new URL(e.name).pathname,duration:e.duration})),
      status:[...document.querySelectorAll('.reddit-load-more-boundary [role=status]')].map(x=>x.textContent)}""")

def get_button():
    element = js("""const b=[...document.querySelectorAll('.reddit-load-more-button')].find(b=>!b.hidden&&!b.disabled);
    if(b)b.scrollIntoView({block:'center'});return b;""")
    assert element, 'no-enabled-load-more-button'
    return element['element-6066-11e4-a52e-4f735466cecf']

def screen(name):
    (evidence / (name + '.png')).write_bytes(base64.b64decode(request('GET', '/session/' + sid + '/screenshot')))

try:
    for _ in range(50):
        try:
            request('GET', '/status', timeout=1)
            break
        except OSError:
            time.sleep(.1)
    session = request('POST', '/session', {'capabilities': {'alwaysMatch': {
        'browserName': 'firefox', 'pageLoadStrategy': 'eager',
        'moz:firefoxOptions': {'binary': '/usr/lib/firefox/firefox', 'args': ['-headless'],
            'prefs': {'media.autoplay.default': 5, 'layers.acceleration.disabled': True, 'webgl.disabled': True}}
    }}})
    sid = session['sessionId']
    result['browserVersion'] = session['capabilities']['browserVersion']
    result['browserPID'] = session['capabilities'].get('moz:processID')
    post('/timeouts', {'pageLoad': 60000, 'script': 30000})
    post('/window/rect', {'width': 1280, 'height': 1000})
    addon = root / 'dist/reddit-load-more-0.1.0.xpi'
    result['addon'] = post('/moz/addon/install', {'path': str(addon), 'temporary': True})
    routes = {'home': 'https://www.reddit.com/', 'subreddit': 'https://www.reddit.com/r/aww/'}
    for name in args.pages:
        url = routes[name]
        try:
            post('/url', {'url': url})
            # Ordinary site redirects can unload an async readiness wait.
            # Reattach to the new document; never reload/bypass a refused page.
            for navigation_try in range(4):
                try:
                    availability = post('/execute/async', {'script': """
                      const done=arguments[arguments.length-1]; let finished=false;
                      const finish=value=>{if(finished)return;finished=true;observer.disconnect();clearTimeout(timer);done(value)};
                      const inspect=()=>{
                        const text=document.body?.innerText || '';
                        if(text.includes("You've been blocked by network security"))finish({blocked:true,reason:'Reddit network-security block'});
                        else if(document.querySelector('shreddit-feed shreddit-post'))finish({blocked:false,feedReady:true});
                      };
                      const observer=new MutationObserver(inspect);observer.observe(document,{childList:true,subtree:true});
                      const timer=setTimeout(()=>finish({blocked:false,feedReady:false,reason:'Feed not ready within 12 seconds'}),12000);
                      inspect();
                    """, 'args': []})
                    break
                except RuntimeError as error:
                    if 'Document was unloaded' not in str(error) or navigation_try == 3:
                        raise
                    time.sleep(.5)
            result['pages'][name] = {'availability': availability, 'navigationWaitRetries': navigation_try}
            assert not availability.get('blocked'), availability['reason'] if availability.get('blocked') else ''
            assert availability.get('feedReady'), availability.get('reason')
            time.sleep(2)
            # Decline optional cookies only; never account actions or CAPTCHA bypass.
            js("""for(const b of document.querySelectorAll('button')) {
              if(/^(reject (all|optional cookies)|continue without accepting)$/i.test(b.textContent.trim()))b.click();
            } return true;""")
            initial = snapshot()
            result['pages'][name]['initial'] = initial
            assert initial['posts'] > 0, ('initial-feed-missing', initial)
            assert len(initial['requests']) == 0, ('auto-prefetched-before-choice', initial)
            js('window.scrollTo(0,document.documentElement.scrollHeight);return true')
            time.sleep(3)
            before = snapshot()
            result['pages'][name]['scrolledWithoutClick'] = before
            assert len(before['requests']) == 0, ('automatic-batch-request', before)
            assert before['posts'] == initial['posts'], ('automatic-post-growth', before)
            assert before['buttons'] == 1, ('boundary-gate-missing', before)
            button = get_button()
            screen(name + '-paused')
            post('/element/' + button + '/click', {})
            time.sleep(4)
            after = snapshot()
            result['pages'][name]['afterClick'] = after
            assert len(after['requests']) == 1 and after['posts'] > before['posts'], ('click-did-not-load-exactly-one', after)
            # Native pagination requests the next partial only near its boundary.
            # A gate need not exist while the newly loaded batch is still below us.
            js('window.scrollTo(0,document.documentElement.scrollHeight);return true')
            time.sleep(3)
            stopped = snapshot()
            result['pages'][name]['stoppedAgain'] = stopped
            assert len(stopped['requests']) == 1 and stopped['posts'] == after['posts'], ('second-batch-auto-loaded', stopped)
            assert stopped['buttons'] == 1, ('next-boundary-gate-missing', stopped)
            button = get_button()
            post('/element/' + button + '/value', {'text': '\ue007', 'value': ['\ue007']})
            time.sleep(4)
            keyboard = snapshot()
            result['pages'][name]['afterEnter'] = keyboard
            assert len(keyboard['requests']) == 2 and keyboard['posts'] > stopped['posts'], ('enter-did-not-load-exactly-one', keyboard)
            screen(name + '-after-keyboard')
            js('window.scrollTo(0,document.documentElement.scrollHeight);return true')
            time.sleep(3)
            final = snapshot()
            result['pages'][name]['stoppedAfterEnter'] = final
            assert len(final['requests']) == 2 and final['posts'] == keyboard['posts'] and final['buttons'] == 1, ('third-batch-not-paused', final)
        except Exception as error:
            result['pages'].setdefault(name, {})['error'] = str(error)
            screen(name + '-failure')
            (evidence / (name + '-failure-source.html')).write_text(request('GET', '/session/' + sid + '/source'))
            if 'bounded-test-interrupted' in str(error):
                raise
    result['ok'] = len(result['pages']) == len(args.pages) and all('error' not in page for page in result['pages'].values())
    result['fullTargetCovered'] = result['ok'] and set(args.pages) == {'home', 'subreddit'}
except Exception as error:
    result['error'] = str(error)
    if sid:
        try:
            screen('failure')
            (evidence / 'failure-source.html').write_text(request('GET', '/session/' + sid + '/source'))
        except Exception:
            pass
finally:
    signal.alarm(0)
    if sid:
        try:
            request('DELETE', '/session/' + sid, timeout=10)
            result['sessionDeleted'] = True
        except Exception as error:
            result['cleanupError'] = str(error)
    driver.terminate()
    try:
        driver.wait(timeout=10)
    except subprocess.TimeoutExpired:
        driver.kill()
        driver.wait()
    result['driverStopped'] = driver.poll() is not None
    (evidence / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    log.close()
print(json.dumps({'ok': result['ok'], 'evidence': str(evidence), 'error': result.get('error')}))
raise SystemExit(0 if result['ok'] else 1)
