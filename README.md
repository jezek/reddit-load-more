# Reddit Load more — Firefox extension


## Target

Replace Reddit feed auto-pagination with an explicit, keyboard-operable **Load more** button. Each activation admits one native batch; the next batch waits again. Cover the modern Reddit home and subreddit feed. Keep login, comments, voting, media lazy loading and other requests untouched. No telemetry, account credentials, external packages or remote extension code.

## Work in progress

The live DOM/network seam is being checked in an isolated system Firefox profile. Implementation and real home/subreddit acceptance are not yet complete. This is not a signed AMO release.

## Verification plan

Observe native pagination before implementation; verify batch count and requests stay constant while scrolling without activation, grow after one click, then stop again. Repeat through keyboard activation, navigation and subreddit feeds. Keep a narrow DOM/API match and test that unrelated lazy-loaded content is not intercepted. Test Firefox with a temporary extension install and disposable profile, never the personal profile.

## References

- [Mozilla content script environments](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/content_scripts)
- [Mozilla blocking request API](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/webRequest/onBeforeRequest) (alternative evaluated; prefer narrower DOM pagination seam if available).
