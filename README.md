# Reddit Load more — Firefox extension


## Latest diagnostic — ordinary access succeeded, live checks remain open

The controlled trial rendered both ordinary feeds with HTTP200 and normal webdriver exposure, then both installed-add-on feeds, without any network or identity change. This demonstrates variability, not a known denial cause. Native scrolling can remove older post DOM: the live runner now audits cumulative unique post IDs plus exact cursor requests, rather than assuming DOM post counts always grow. The corrected bounded run is pending inspection; no full live pass is claimed.

## Target

Replace Reddit feed auto-pagination with an explicit, keyboard-operable **Load more** button. Each activation admits one native batch; the next batch waits again. Cover the modern Reddit home and subreddit feed. Keep login, comments, voting, media lazy loading and other requests untouched. No telemetry, account credentials, external packages or remote extension code.

## Current work — controlled availability comparison reopened


The bundles/source zip under `dist/` remain the preserved `4b2aeb5` checkpoint, not the latest diagnostic-runner source. The unsigned XPI is unchanged. Use current Git source for the new flag; refresh handoff archives only after a later accepted milestone.

### Earlier blocked checkpoint (2026-10-24 16:02 UTC)

The candidate is implemented and offline behavior checks pass, but it is **not fully verified or ready for acceptance**. Reddit repeatedly returned its own “You've been blocked by network security” page on home and, in the latest targeted attempt, on r/aww. No bypass, proxy, user-agent spoofing, login or CAPTCHA workaround was attempted. All recorded test workers, Firefox sessions and drivers have stopped; no job is pending.

Partial real home evidence exists: scroll without choice held at3posts/zero cursor requests; one trusted click loaded28posts/exactly one request. Full repeated click/Enter/pause behavior on both live routes remains unverified. Mocked groups, packaging, or a scoped result must not be reported as complete live acceptance. Resume when ordinary permitted Firefox access to both assigned feeds is available; retain the original target and rerun the actual behavior check then. No repeated blocked-site probing is scheduled.

## Verification plan

Observe native pagination before implementation; verify batch count and requests stay constant while scrolling without activation, grow after one click, then stop again. Repeat through keyboard activation, navigation and subreddit feeds. Keep a narrow DOM/API match and test that unrelated lazy-loaded content is not intercepted. Test Firefox with a temporary extension install and disposable profile, never the personal profile.

## References

- [Mozilla content script environments](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/content_scripts)
- [Mozilla blocking request API](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/webRequest/onBeforeRequest) (alternative evaluated; prefer narrower DOM pagination seam if available).

## Current implementation (candidate)

Firefox Manifest V3 with a `document_start` **MAIN-world** content script and CSS, no background worker or privileged API permissions. It wraps only `faceplate-partial._loadContent` for a `slot="load-after"` descendant of `shreddit-feed`, on home/sorted home/subreddit feed URLs, with a same-origin recognized feed endpoint and nonempty `after` cursor. The native request/rendering pipeline is held before its request, not fetched then hidden. Login, media, comments and sidebar partials pass through. One trusted click or keyboard activation releases one batch; the following native partial waits again. Failed requests expose a retry instead of silently unpausing. Page scripts can inspect/change MAIN-world code: this is a browsing aid, not a security boundary.

Observed before extension installation on 2026-10-24: scrolling increased home posts28→53 and r/aww posts3→27. Reddit requested `/svc/shreddit/feeds/popular-feed?after=…` and `/svc/shreddit/community-more-posts/best/?after=…`. Both use the native programmatic `faceplate-partial` seam. The script patches the class before custom-element upgrade to avoid the initial-prefetch race. It does not globally alter fetch, IntersectionObserver, networking or scroll events.

## Build and temporary install

No package installation needed. Python3 stdlib builds the unsigned XPI:

```sh
python3 tools/package.py
```

In Firefox open `about:debugging#/runtime/this-firefox` → **Load Temporary Add-on** → select `dist/reddit-load-more-0.1.0.xpi` (or `extension/manifest.json`). Refresh already-open Reddit tabs. Scroll until **Load more**, then click or use Tab/Enter/Space. Disable/remove the add-on and refresh to restore native behavior. Temporary installation ends when Firefox restarts. Normal permanent Firefox installation requires Mozilla signing; that is not performed or claimed here.

The single batch size is chosen by Reddit, not a fixed post/screen count. Modern desktop `www.reddit.com` and the apex redirect are in scope. Old Reddit, mobile variants, logged-in personalized feeds and future DOM changes are not yet verified. If Reddit renames the native class/method/route, matching may stop and native auto-loading may resume; do not treat this as a guaranteed universal traffic blocker.

## Checks

```sh
node --test tests/gate.test.cjs
python3 tools/package.py
python3 -I -B tests/firefox_live.py --evidence /absolute/new/private/evidence-directory
```

Five Node built-in behavior groups pass: delayed native requests/duplicate choices, narrow matching with12cases, retry, pre-upgrade hooking, detached navigation. No npm or third-party modules. The live runner uses the installed `/usr/lib/firefox/firefox` binary behind the system launcher and geckodriver, not a personal profile. Geckodriver's own `--allow-system-access` option enables temporary add-on installation; Firefox rejects supplying its corresponding flag via WebDriver capabilities. The runner has a150-second alarm and cleanup-finally; it reads public pages, declines optional cookies if shown, and never performs account actions or bypasses a challenge.



## Candidate handoff (not an accepted release)

The standalone repository includes its local history and can be uploaded later by its owner; no remote or GitHub repository was created. `dist/reddit-load-more-0.1.0.xpi` remains the unsigned temporary-install candidate. The source zip and Git bundle under `dist/` preserve the public source and local commit history without runtime/browser evidence, personal profiles or secrets. To restore the bundle into a new directory:

```sh
git clone /absolute/path/reddit-load-more-candidate.bundle reddit-load-more
```

The live runner defaults to both routes. `--pages subreddit` or `--pages home` is an explicit narrow diagnostic; `fullTargetCovered` remains false unless both requested routes pass. Ordinary document redirects are handled by bounded readiness reattachment, without reloading or bypassing a refusal.
