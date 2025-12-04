#!/usr/bin/env node

import { spawn, execSync } from "node:child_process";
import { homedir } from "node:os";
import { join } from "node:path";
import { tmpdir } from "node:os";
import puppeteer from "puppeteer-core";

const BROWSER_URL = "http://localhost:9222";

// CLI Help
function showHelp() {
  console.log(`
web.js - Browser automation via Chrome DevTools Protocol

USAGE:
  ./web.js <command> [options]

COMMANDS:
  start [--profile]           Start Chrome with remote debugging
  nav <url> [--new]          Navigate to URL
  eval '<code>'              Evaluate JavaScript in active tab
  screenshot                 Capture screenshot of current page
  pick "<message>"           Interactive element picker
  stop                       Stop Chrome instance
  help                       Show this help

EXAMPLES:
  ./web.js start
  ./web.js nav https://example.com
  ./web.js eval 'document.title'
  ./web.js screenshot
  ./web.js pick "Select the button"
  ./web.js stop

OPTIONS:
  start --profile            Copy your Chrome profile (cookies, logins)
  nav --new                  Open URL in new tab
  `);
}

// Start Chrome
async function startChrome(useProfile = false) {
  const homeDir = homedir();
  const cacheDir = join(homeDir, ".cache", "scraping");
  const chromeProfileDir = join(
    homeDir,
    "Library",
    "Application Support",
    "Google",
    "Chrome",
  );

  // Kill existing Chrome
  try {
    execSync("killall 'Google Chrome'", { stdio: "ignore" });
    await new Promise((r) => setTimeout(r, 1000));
  } catch {}

  // Setup profile directory
  execSync(`mkdir -p "${cacheDir}"`, { stdio: "ignore" });

  if (useProfile) {
    console.log("Copying Chrome profile...");
    execSync(`rsync -a --delete "${chromeProfileDir}/" "${cacheDir}/"`, {
      stdio: "pipe",
    });
  }

  // Start Chrome in background
  spawn(
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ["--remote-debugging-port=9222", `--user-data-dir=${cacheDir}`],
    { detached: true, stdio: "ignore" },
  ).unref();

  // Wait for Chrome to be ready
  let connected = false;
  for (let i = 0; i < 30; i++) {
    try {
      const browser = await puppeteer.connect({
        browserURL: BROWSER_URL,
        defaultViewport: null,
      });
      await browser.disconnect();
      connected = true;
      break;
    } catch {
      await new Promise((r) => setTimeout(r, 500));
    }
  }

  if (!connected) {
    console.error("✗ Failed to connect to Chrome");
    process.exit(1);
  }

  console.log(
    `✓ Chrome started on :9222${useProfile ? " with profile" : ""}`,
  );
}

// Navigate
async function navigate(url, newTab = false) {
  if (!url) {
    console.error("Error: URL required");
    console.log("Usage: ./web.js nav <url> [--new]");
    process.exit(1);
  }

  try {
    const b = await puppeteer.connect({
      browserURL: BROWSER_URL,
      defaultViewport: null,
    });

    if (newTab) {
      const p = await b.newPage();
      await p.goto(url, { waitUntil: "domcontentloaded" });
      console.log("✓ Opened:", url);
    } else {
      const pages = await b.pages();
      const p = pages.at(-1) || (await b.newPage());
      await p.goto(url, { waitUntil: "domcontentloaded" });
      console.log("✓ Navigated to:", url);
    }

    await b.disconnect();
  } catch (error) {
    console.error("✗ Navigation failed:", error.message);
    console.log("\nEnsure Chrome is running: ./web.js start");
    process.exit(1);
  }
}

// Evaluate JavaScript
async function evaluate(code) {
  if (!code) {
    console.error("Error: Code required");
    console.log("Usage: ./web.js eval '<code>'");
    process.exit(1);
  }

  try {
    const b = await puppeteer.connect({
      browserURL: BROWSER_URL,
      defaultViewport: null,
    });

    const p = (await b.pages()).at(-1);

    if (!p) {
      console.error("✗ No active tab found");
      console.log("Navigate to a page first: ./web.js nav <url>");
      process.exit(1);
    }

    const result = await p.evaluate((c) => {
      const AsyncFunction = (async () => {}).constructor;
      return new AsyncFunction(`return (${c})`)();
    }, code);

    // Format output
    if (Array.isArray(result)) {
      for (let i = 0; i < result.length; i++) {
        if (i > 0) console.log("");
        for (const [key, value] of Object.entries(result[i])) {
          console.log(`${key}: ${value}`);
        }
      }
    } else if (typeof result === "object" && result !== null) {
      for (const [key, value] of Object.entries(result)) {
        console.log(`${key}: ${value}`);
      }
    } else {
      console.log(result);
    }

    await b.disconnect();
  } catch (error) {
    console.error("✗ Evaluation failed:", error.message);
    console.log("\nEnsure Chrome is running: ./web.js start");
    process.exit(1);
  }
}

// Screenshot
async function screenshot() {
  try {
    const b = await puppeteer.connect({
      browserURL: BROWSER_URL,
      defaultViewport: null,
    });

    const p = (await b.pages()).at(-1);

    if (!p) {
      console.error("✗ No active tab found");
      console.log("Navigate to a page first: ./web.js nav <url>");
      process.exit(1);
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    const filename = `screenshot-${timestamp}.png`;
    const filepath = join(tmpdir(), filename);

    await p.screenshot({ path: filepath });
    console.log(filepath);

    await b.disconnect();
  } catch (error) {
    console.error("✗ Screenshot failed:", error.message);
    console.log("\nEnsure Chrome is running: ./web.js start");
    process.exit(1);
  }
}

// Pick Elements
async function pick(message) {
  if (!message) {
    console.error("Error: Message required");
    console.log('Usage: ./web.js pick "Select an element"');
    process.exit(1);
  }

  try {
    const b = await puppeteer.connect({
      browserURL: BROWSER_URL,
      defaultViewport: null,
    });

    const p = (await b.pages()).at(-1);

    if (!p) {
      console.error("✗ No active tab found");
      console.log("Navigate to a page first: ./web.js nav <url>");
      process.exit(1);
    }

    // Inject pick() helper
    await p.evaluate(() => {
      if (!window.pick) {
        window.pick = async (message) => {
          if (!message) {
            throw new Error("pick() requires a message parameter");
          }
          return new Promise((resolve) => {
            const selections = [];
            const selectedElements = new Set();

            const overlay = document.createElement("div");
            overlay.style.cssText =
              "position:fixed;top:0;left:0;width:100%;height:100%;z-index:2147483647;pointer-events:none";

            const highlight = document.createElement("div");
            highlight.style.cssText =
              "position:absolute;border:2px solid #3b82f6;background:rgba(59,130,246,0.1);transition:all 0.1s";
            overlay.appendChild(highlight);

            const banner = document.createElement("div");
            banner.style.cssText =
              "position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#1f2937;color:white;padding:12px 24px;border-radius:8px;font:14px sans-serif;box-shadow:0 4px 12px rgba(0,0,0,0.3);pointer-events:auto;z-index:2147483647";

            const updateBanner = () => {
              banner.textContent = `${message} (${selections.length} selected, Cmd/Ctrl+click to add, Enter to finish, ESC to cancel)`;
            };
            updateBanner();

            document.body.append(banner, overlay);

            const cleanup = () => {
              document.removeEventListener("mousemove", onMove, true);
              document.removeEventListener("click", onClick, true);
              document.removeEventListener("keydown", onKey, true);
              overlay.remove();
              banner.remove();
              selectedElements.forEach((el) => {
                el.style.outline = "";
              });
            };

            const onMove = (e) => {
              const el = document.elementFromPoint(e.clientX, e.clientY);
              if (!el || overlay.contains(el) || banner.contains(el)) return;
              const r = el.getBoundingClientRect();
              highlight.style.cssText = `position:absolute;border:2px solid #3b82f6;background:rgba(59,130,246,0.1);top:${r.top}px;left:${r.left}px;width:${r.width}px;height:${r.height}px`;
            };

            const buildElementInfo = (el) => {
              const parents = [];
              let current = el.parentElement;
              while (current && current !== document.body) {
                const parentInfo = current.tagName.toLowerCase();
                const id = current.id ? `#${current.id}` : "";
                const cls = current.className
                  ? `.${current.className.trim().split(/\s+/).join(".")}`
                  : "";
                parents.push(parentInfo + id + cls);
                current = current.parentElement;
              }

              return {
                tag: el.tagName.toLowerCase(),
                id: el.id || null,
                class: el.className || null,
                text: el.textContent?.trim().slice(0, 200) || null,
                html: el.outerHTML.slice(0, 500),
                parents: parents.join(" > "),
              };
            };

            const onClick = (e) => {
              if (banner.contains(e.target)) return;
              e.preventDefault();
              e.stopPropagation();
              const el = document.elementFromPoint(e.clientX, e.clientY);
              if (!el || overlay.contains(el) || banner.contains(el)) return;

              if (e.metaKey || e.ctrlKey) {
                if (!selectedElements.has(el)) {
                  selectedElements.add(el);
                  el.style.outline = "3px solid #10b981";
                  selections.push(buildElementInfo(el));
                  updateBanner();
                }
              } else {
                cleanup();
                const info = buildElementInfo(el);
                resolve(selections.length > 0 ? selections : info);
              }
            };

            const onKey = (e) => {
              if (e.key === "Escape") {
                e.preventDefault();
                cleanup();
                resolve(null);
              } else if (e.key === "Enter" && selections.length > 0) {
                e.preventDefault();
                cleanup();
                resolve(selections);
              }
            };

            document.addEventListener("mousemove", onMove, true);
            document.addEventListener("click", onClick, true);
            document.addEventListener("keydown", onKey, true);
          });
        };
      }
    });

    const result = await p.evaluate((msg) => window.pick(msg), message);

    // Format output
    if (Array.isArray(result)) {
      for (let i = 0; i < result.length; i++) {
        if (i > 0) console.log("");
        for (const [key, value] of Object.entries(result[i])) {
          console.log(`${key}: ${value}`);
        }
      }
    } else if (typeof result === "object" && result !== null) {
      for (const [key, value] of Object.entries(result)) {
        console.log(`${key}: ${value}`);
      }
    } else {
      console.log(result);
    }

    await b.disconnect();
  } catch (error) {
    console.error("✗ Pick failed:", error.message);
    console.log("\nEnsure Chrome is running: ./web.js start");
    process.exit(1);
  }
}

// Stop Chrome
function stopChrome() {
  try {
    execSync("killall 'Google Chrome'", { stdio: "ignore" });
    console.log("✓ Chrome stopped");
  } catch {
    console.log("Chrome not running");
  }
}

// Main CLI Router
const [, , command, ...args] = process.argv;

switch (command) {
  case "start":
    await startChrome(args.includes("--profile"));
    break;

  case "nav":
    await navigate(args[0], args.includes("--new"));
    break;

  case "eval":
    await evaluate(args.join(" "));
    break;

  case "screenshot":
    await screenshot();
    break;

  case "pick":
    await pick(args.join(" "));
    break;

  case "stop":
    stopChrome();
    break;

  case "help":
  case "--help":
  case "-h":
    showHelp();
    break;

  default:
    console.error(`Unknown command: ${command || "(none)"}`);
    showHelp();
    process.exit(1);
}

