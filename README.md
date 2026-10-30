# Reddit Load more for Firefox

Pause automatic pagination on Reddit feeds and choose when to load the next batch.
At the feed boundary, select **Load more** with a mouse or focus it and press Enter.
Each activation admits one batch chosen by Reddit; subsequent batches wait again.

## Installation for testing

1. Clone or download this repository.
2. In Firefox, open `about:debugging#/runtime/this-firefox`.
3. Select **Load Temporary Add-on** and choose `extension/manifest.json`.
4. Refresh any open Reddit tabs and scroll to the end of the loaded feed.

Alternatively, build an XPI with `python3 tools/package.py` and select
`dist/reddit-load-more-0.1.0.xpi`. The package is unsigned: temporary add-ons
are removed when Firefox restarts. Permanent installation requires Mozilla signing.
To remove it sooner, disable or remove the add-on in Firefox and refresh Reddit.

## Verification and limitations

The add-on was tested on modern Reddit home and r/aww in Firefox 158.0.1,
using a logged-out session. Both feeds paused without automatic cursor requests;
a trusted click and then a focused Enter each loaded one batch, followed by
another stable pause. The test and its limits are described in [ACCEPTANCE.md](ACCEPTANCE.md).
The manifest requires Firefox 140 or newer; other versions, logged-in feeds,
old/mobile Reddit and all communities or sort modes have not all been tested.
Mouse and keyboard activation were tested, but this is not a full accessibility audit.

Reddit can change its internal components at any time. The add-on is a browsing
aid, not a security boundary, and automatic loading may resume if Reddit changes.
It has no telemetry, external dependencies, remotely loaded extension code or
account credentials. It does not globally block media or network requests.

## Development

The Manifest V3 content script runs in the page MAIN world at document start.
It intercepts the native `faceplate-partial._loadContent` feed-pagination seam
only on recognized feed routes and cursor requests, then allows one native batch
per activation. Unrelated partials pass through.

Run the offline behavior checks with Node.js:

```sh
node --test tests/gate.test.cjs
```

Build an unsigned XPI with Python 3's standard library:

```sh
python3 tools/package.py
```

The optional live test uses a locally installed Firefox and geckodriver and
writes evidence only to the directory you specify:

```sh
python3 -I -B tests/firefox_live.py --baseline-first --evidence /absolute/new/private/evidence-directory
```

The live runner is environment-specific and uses a disposable browser session;
read its options before running it. No personal Firefox profile is required.

## License

[MIT](LICENSE)
