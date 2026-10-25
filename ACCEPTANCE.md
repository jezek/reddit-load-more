# Accepted live scope — 2026-10-25 UTC


## Observed result

System Firefox 158.0.1 with temporary add-on `reddit-load-more@jezbot.local`; ordinary no-add-on baseline and subsequent add-on phase both accessed home and r/aww. Baseline navigation returned200 with rendered posts and normal `navigator.webdriver=true`. Same session/profile/preferences/network between phases. Headless, autoplay policy5, disabled accelerated layers/WebGL remained unchanged; this is not a complete ordinary-human-profile simulation.

Cumulative IDs at initial / scroll / click / pause / Enter / pause:

- Home: **3 / 3 / 28 / 28 / 53 / 53**.
- r/aww: **3 / 3 / 27 / 27 / 52 / 52**.
- Completed feed-cursor requests on each: **0 / 0 / 1 / 1 / 2 / 2**.

Pauses preserved exact identity sets and request records. Each trusted activation added novel IDs and exactly one distinct next-cursor request. Native DOM removal was allowed, not mistaken for lost pagination. Home used `/svc/shreddit/feeds/popular-feed`; r/aww used `/svc/shreddit/community-more-posts/best/`. Four actual paused/after-keyboard screenshots independently viewed; all owned workers/browser/driver closed. Optional Google login suggestion on subreddit did not prevent interaction; no login action occurred.

## Evidence and limits

Private original result/screenshots/logs: workspace `runtime/reddit-load-more-20261024-2202/identity-check/`. Independent saved-evidence acceptance receipt: workspace `runtime/reddit-load-more-20261025-0002/acceptance.json`. Portable private copies: this project's ignored `runtime/qualification/20261025/`. None is in public Git/source/XPI archives.

Public source runner: `tests/firefox_live.py` from commit `3801ba4`, SHA256 `bfd5f7f9e54885252c2224054a05421acf1e5a014b8cab46175870399c61d0b2`. Product remains `d6eb1bb`; XPI unchanged. Prior five offline behavior groups and packaging proof were reused, not rerun merely for final filing. Independent result/source/archive checks are not additional product test runs.

Historical access-denial cause remains unknown. No bypass, identity masking or network change was needed for the successful trial; phase order/time/cookie carryover limits causal conclusions. No claim of all browsers, all communities/sorts, logged-in/old/mobile Reddit, a full accessibility audit, permanent installation or Mozilla signing. See README for usage, removal and source restoration.
