/* No browser APIs or privileged data: this deliberately runs in the page world. */
(() => {
  "use strict";
  const registry = window.customElements;
  if (!registry) return;
  const pending = new WeakMap();
  const patched = new WeakSet();

  function isFeedPage() {
    return /^\/(?:|(?:best|hot|new|top|rising|controversial)\/?|r\/[^/]+\/?(?:best|hot|new|top|rising|controversial)?\/?)$/.test(location.pathname);
  }

  function isNextBatch(partial) {
    if (!isFeedPage() || partial.localName !== "faceplate-partial" ||
        partial.getAttribute("slot") !== "load-after" ||
        !partial.closest("shreddit-feed")) return false;
    try {
      const url = new URL(partial.getAttribute("src") || "", location.href);
      return url.origin === location.origin && !!url.searchParams.get("after") &&
        (/^\/svc\/shreddit\/feeds\/[a-z0-9-]+-feed$/.test(url.pathname) ||
         /^\/svc\/shreddit\/community-more-posts\/(?:best|hot|new|top|rising|controversial)\/$/.test(url.pathname));
    } catch { return false; }
  }

  function waitForUser(partial, original, args) {
    const existing = pending.get(partial);
    if (existing) return existing;
    const wrapper = document.createElement("section");
    wrapper.className = "reddit-load-more-boundary";
    wrapper.setAttribute("aria-label", "Reddit feed batch boundary");
    const status = document.createElement("p");
    status.setAttribute("role", "status");
    status.textContent = "Auto-loading paused. Load one more batch when you choose.";
    const button = document.createElement("button");
    button.type = "button";
    button.className = "reddit-load-more-button";
    button.textContent = "Load more";
    wrapper.append(status, button);
    partial.before(wrapper);
    let loading = false;
    const promise = new Promise((resolve) => {
      button.addEventListener("click", async (event) => {
        // A page calling button.click() must not silently re-enable auto-loading.
        if (!event.isTrusted || loading || !partial.isConnected) return;
        loading = true;
        button.disabled = true;
        status.textContent = "Loading one batch…";
        try {
          const result = await Reflect.apply(original, partial, args);
          if (!result) throw new Error("No feed response");
          status.textContent = "Batch loaded. The next batch will wait for Load more.";
          button.hidden = true;
          resolve(result);
        } catch {
          status.textContent = "Could not load this batch. Choose Load more to retry.";
          button.disabled = false;
          loading = false;
        }
      });
    });
    pending.set(partial, promise);
    return promise;
  }

  function patch(ctor) {
    if (!ctor || patched.has(ctor)) return;
    const prototype = ctor.prototype;
    const descriptor = Object.getOwnPropertyDescriptor(prototype, "_loadContent");
    if (!descriptor || typeof descriptor.value !== "function" || !descriptor.configurable) return;
    const original = descriptor.value;
    Object.defineProperty(prototype, "_loadContent", {
      ...descriptor,
      value: function (...args) {
        if (!isNextBatch(this)) return Reflect.apply(original, this, args);
        return waitForUser(this, original, args);
      }
    });
    patched.add(ctor);
  }

  // Patch before define() upgrades existing HTML. whenDefined() alone is too late
  // for a connectedCallback that starts loading synchronously during upgrade.
  const define = registry.define;
  registry.define = function (name, ctor, ...options) {
    if (name === "faceplate-partial") patch(ctor);
    return Reflect.apply(define, this, [name, ctor, ...options]);
  };
  patch(registry.get("faceplate-partial"));
})();
