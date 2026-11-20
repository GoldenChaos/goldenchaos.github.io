import { spawn } from "node:child_process";
import path from "node:path";

const projectRoot = path.resolve(import.meta.dirname, "..");
const eleventy = path.join(projectRoot, "node_modules", "@11ty", "eleventy", "cmd.js");

const child = spawn(process.execPath, [
  eleventy,
  "--serve",
  "--port=8082",
  "--pathprefix=/dotti-and-skratchi/"
], {
  cwd: projectRoot,
  env: {
    ...process.env,
    ELEVENTY_INCLUDE_ADMIN: "true"
  },
  stdio: "inherit"
});

child.on("exit", (code) => process.exit(code ?? 0));

