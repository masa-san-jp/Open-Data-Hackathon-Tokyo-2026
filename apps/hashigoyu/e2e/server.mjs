import { createReadStream } from "node:fs";
import { stat } from "node:fs/promises";
import { createServer } from "node:http";
import { extname, join, normalize, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(fileURLToPath(new URL("..", import.meta.url)));
const apps = new Map([
  ["guest", join(root, "apps/guest/dist")],
  ["counter", join(root, "apps/counter/dist")],
  ["admin", join(root, "apps/admin/dist")],
]);
const legacyPaths = new Map([
  ["/kyaku.html", "/guest/"],
  ["/bandai.html", "/counter/"],
  ["/kanri.html", "/admin/"],
]);
const mimeTypes = new Map([
  [".html", "text/html; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".css", "text/css; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".svg", "image/svg+xml"],
]);

function fileForRequest(pathname) {
  if (pathname === "/") {
    return { appRoot: root, candidate: join(root, "index.html") };
  }
  const [, appName, ...parts] = pathname.split("/");
  const appRoot = apps.get(appName);
  if (!appRoot) return null;
  const relative = parts.length > 0 ? parts.join("/") : "index.html";
  const candidate = normalize(join(appRoot, relative));
  if (!candidate.startsWith(`${appRoot}/`) && candidate !== appRoot) return null;
  return { appRoot, candidate };
}

const server = createServer(async (request, response) => {
  const pathname = new URL(request.url ?? "/", "http://127.0.0.1").pathname;
  const legacyDestination = legacyPaths.get(pathname);
  if (legacyDestination) {
    response.writeHead(308, { location: legacyDestination });
    response.end();
    return;
  }
  const target = fileForRequest(pathname);
  if (!target) {
    response.writeHead(404);
    response.end("Not found");
    return;
  }

  let filePath = target.candidate;
  try {
    const fileStat = await stat(filePath);
    if (!fileStat.isFile()) filePath = join(target.appRoot, "index.html");
  } catch {
    filePath = join(target.appRoot, "index.html");
  }

  response.writeHead(200, {
    "content-type": mimeTypes.get(extname(filePath)) ?? "application/octet-stream",
  });
  createReadStream(filePath).pipe(response);
});

server.listen(4173, "127.0.0.1");
