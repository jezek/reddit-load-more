# Firefox live verification — 2026-10-25

A temporary add-on was tested in Firefox 158.0.1 on modern Reddit home and
r/aww in a logged-out session. Both feeds were first accessible without the
add-on, then tested with it in the same browser session and preferences.

Cumulative unique post IDs at initial / scroll / click / pause / Enter / pause:

- Home: **3 / 3 / 28 / 28 / 53 / 53**.
- r/aww: **3 / 3 / 27 / 27 / 52 / 52**.
- Completed feed-cursor requests for each: **0 / 0 / 1 / 1 / 2 / 2**.

Each trusted activation produced one new cursor request and new posts; waiting
at the boundary did not. Cumulative IDs were used because Reddit virtualizes its
feed and may remove older DOM elements. Mouse and keyboard activation were
checked, but this was not a full accessibility audit.

Earlier attempts sometimes encountered Reddit network-security refusals. The
successful test used ordinary access without a proxy, identity masking or
challenge manipulation. The cause of the earlier refusals was not established.
The sequential baseline and add-on phases can share cookie, timing and order
carryover; they are not a perfect causal isolation experiment.

This is not a claim about logged-in feeds, all communities and sort modes,
old/mobile Reddit, every Firefox version or future Reddit changes. The add-on
is unsigned and was installed temporarily for the test.
