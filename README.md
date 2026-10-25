# Reddit Load more — Firefox extension



## What it does

Feed auto-pagination waits for an explicit **Load more** button. Click it, or focus it with Tab and press Enter, to admit **one Reddit-sized batch**. The next batch waits again, including when you keep scrolling. Reddit chooses the batch size; this is not a fixed post/screen limit.

The initial page still loads normally. The extension has no telemetry, external packages, remote extension code or account credentials. It does not globally block networking or media loading.

## Temporary installation and removal

1. Open Firefox `about:debugging#/runtime/this-firefox`.
2. Choose **Load Temporary Add-on** and select `dist/reddit-load-more-0.1.0.xpi`, or `extension/manifest.json` from this repository.
3. Refresh already-open Reddit tabs. Scroll to the feed boundary and use **Load more**.
4. To restore native behavior, remove/disable the add-on and refresh those tabs.

The XPI is **unsigned** and is for temporary installation, which ends when Firefox restarts. Normal permanent installation requires Mozilla signing; that is outside this handoff.

Build the same XPI with Python 3's standard library, without installing dependencies:

```sh
python3 tools/package.py
```

Verified XPI: 2463 bytes, SHA256 `205b376012f867909f14c3ec941141084eb7dd9f9fc2fa6a30f3b13a6027e337`. Its only files are `manifest.json`, `gate.js`, and `gate.css`.

## Actual verification

A disposable system Firefox session first opened both feeds **without** the add-on: each rendered three posts, with navigation HTTP200 and ordinary WebDriver exposure. The unchanged XPI was then installed in the same profile, with the same browser preferences and network identity.

| Observed phase | Home unique posts / cursor requests | r/aww unique posts / cursor requests |
| --- | --- | --- |
| Initial | 3 / 0 | 3 / 0 |
| Scroll without activation | 3 / 0 | 3 / 0 |
| Trusted click | 28 / 1 | 27 / 1 |
| Scroll and wait again | 28 / 1 | 27 / 1 |
| Focused button + Enter | 53 / 2 | 52 / 2 |
| Scroll and wait a third time | 53 / 2 | 52 / 2 |

Counts are **cumulative unique post IDs**, not simultaneous DOM elements: Reddit virtualizes the feed and removes older elements. Each activation produced exactly one distinct feed-cursor request and new post identities; pauses held both the cumulative identities and request records stable. Four saved screenshots were independently viewed. The test session, Firefox and geckodriver all stopped. See `ACCEPTANCE.md` for limits and evidence locations.

Earlier attempts sometimes received Reddit's explicit network-security refusal. Later ordinary access succeeded **without bypass, proxy, address rotation, user-agent masking, login or challenge manipulation**. The exact historical refusal cause remains unknown; neither a permanent IP ban nor excessive clicking was established. Sequential baseline/add-on comparison has cookie, time and order carryover and is not perfect causal isolation.

## Scope and limitations

- Actual live coverage: modern desktop `https://www.reddit.com/` and `https://www.reddit.com/r/aww/`, logged out, Firefox 158.0.1. Matchers also recognize sorted home/subreddit routes, but those variants are not all live-audited.
- Trusted click and focused Enter were tested. This is **not a full screen-reader/accessibility audit**. Old/mobile Reddit, logged-in personalized feeds, all communities/sorts and future Reddit changes are unverified.
- The script runs in the page's **MAIN** world. Page code can interfere: this is a browsing aid, **not a security or universal traffic-blocking boundary**.
- Reddit's private component API may change. If the native class, method or feed route changes, matching may stop and native automatic loading may resume.
- Unrelated media/login/comments/sidebar partials pass through by design and narrow offline matching checks; this does not claim an exhaustive live regression audit of every Reddit feature.

## Implementation and development

Manifest V3 `document_start` MAIN-world script and CSS; no background worker or privileged API permissions. The hook wraps `faceplate-partial._loadContent` before custom-element upgrade, only for `slot="load-after"` descendants of `shreddit-feed`, supported page URLs and recognized same-origin feed endpoints with a nonempty `after` cursor. It holds the native request before dispatch, preserving native rendering. Duplicate pending calls share one promise; loading is guarded and failures offer retry. No global fetch, IntersectionObserver or scroll hook.

Offline behavior checks use Node's built-in test runner (five previously passed groups, including 12 narrow matching cases):

```sh
node --test tests/gate.test.cjs
```

The optional live acceptance runner needs existing system Firefox and geckodriver, not Selenium or a personal profile:

```sh
python3 -I -B tests/firefox_live.py --baseline-first --evidence /absolute/new/private/evidence-directory
```

It uses `/usr/lib/firefox/firefox` behind the system launcher, geckodriver's `--allow-system-access` option for temporary add-on installation, a 150-second alarm and owned-session cleanup. Both routes are the default. `--pages home` or `--pages subreddit` is diagnostic only; a scoped pass cannot claim full-target coverage. Explicit ordinary access refusal stops baseline-first acceptance; no evasion is attempted.

## Git and portable handoff

The repository is separate from the workspace repository. Git contains public source/docs/tests only; `dist/` and private `runtime/` evidence/profiles are ignored. No remote repository was created.

Current handoff files use commit-specific names:

- `dist/reddit-load-more-history-<commit>.bundle`: complete local Git history.
- `dist/reddit-load-more-source-<commit>.zip`: public tracked source at that commit.
- `dist/reddit-load-more-0.1.0.xpi`: temporary-install add-on.

Restore the current bundle into a new directory (replace `<commit>` with the supplied filename suffix):

```sh
git clone /absolute/path/reddit-load-more-history-<commit>.bundle reddit-load-more
cd reddit-load-more
python3 tools/package.py
```

The older `reddit-load-more-candidate.bundle` and `reddit-load-more-candidate-source.zip` deliberately preserve the historical blocked `4b2aeb5` checkpoint; they are **not** the current runner/docs. Current archive identities and restore verification are recorded in the final workspace report. MIT license; unrelated Reddit content is not part of the source package.
