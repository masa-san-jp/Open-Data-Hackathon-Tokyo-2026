import { access, copyFile, cp, mkdir, rm } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const projectRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const publicRoot = join(projectRoot, "cloudflare", "public");
const appNames = ["guest", "counter", "admin"];

for (const appName of appNames) {
  await access(join(projectRoot, "apps", appName, "dist", "index.html"));
}

await rm(publicRoot, { force: true, recursive: true });
await mkdir(publicRoot, { recursive: true });
await copyFile(join(projectRoot, "index.html"), join(publicRoot, "index.html"));

for (const appName of appNames) {
  await cp(
    join(projectRoot, "apps", appName, "dist"),
    join(publicRoot, appName),
    { recursive: true },
  );
}
