export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const legacyPaths = new Map([
      ["/kyaku.html", "/guest/"],
      ["/bandai.html", "/counter/"],
      ["/kanri.html", "/admin/"],
    ]);
    const legacyDestination = legacyPaths.get(url.pathname);
    if (legacyDestination) {
      return Response.redirect(new URL(legacyDestination, url), 308);
    }

    if (url.pathname === "/") {
      url.pathname = "/index.html";
    }
    if (["/guest", "/guest/", "/counter", "/counter/", "/admin", "/admin/"].includes(url.pathname)) {
      url.pathname = `${url.pathname.replace(/\/$/, "")}/index.html`;
    }
    return env.ASSETS.fetch(new Request(url, request));
  },
};
