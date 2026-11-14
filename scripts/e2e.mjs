// End-to-end check of the tasks module in a real browser: create, toggle and delete through HTMX,
// with no full page reload. Usage:
//   CHROME_PATH=/path/to/chrome node scripts/e2e.mjs [base-url]
import { chromium } from "playwright-core";

const base = process.argv[2] || "http://127.0.0.1:8765";
const chrome = process.env.CHROME_PATH;
if (!chrome) {
  console.error("CHROME_PATH is not set");
  process.exit(2);
}

const browser = await chromium.launch({ executablePath: chrome, headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));
page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
page.on("dialog", (d) => d.accept());

const failures = [];
const check = (ok, label) => {
  console.log(`${ok ? "ok  " : "FAIL"} ${label}`);
  if (!ok) failures.push(label);
};

try {
  await page.goto(`${base}/tareas/`, { waitUntil: "networkidle" });
  await page.evaluate(() => (window.__noReload = true));

  const title = `Tarea e2e ${Date.now()}`;
  await page.fill('input[name="titulo"]', title);
  await page.selectOption('select[name="prioridad"]', "A");
  await page.fill('input[name="fecha_limite"]', "2026-12-31");
  await page.click('button[type="submit"]');
  const item = page.locator("li.task-item", { hasText: title }).first();
  await item.waitFor({ state: "visible", timeout: 5000 });
  check(true, "crear: la tarea aparece sin recargar");
  check(await page.evaluate(() => window.__noReload === true), "crear: la página no se recargó");
  check((await page.inputValue('input[name="titulo"]')) === "", "crear: el formulario quedó vacío");
  check((await page.locator(".task-item--done", { hasText: title }).count()) === 0, "crear: nace pendiente");

  const before = await page.locator("#contadores-tareas").innerText();
  await item.locator("button.task-item__toggle").click();
  const done = page.locator("li.task-item.task-item--done", { hasText: title }).first();
  await done.waitFor({ state: "visible", timeout: 5000 });
  const pressed = await done.locator("button.task-item__toggle").getAttribute("aria-pressed");
  check(pressed === "true", "alternar: la tarea queda completada y aria-pressed=true");
  const after = await page.locator("#contadores-tareas").innerText();
  check(before !== after, "alternar: los contadores se actualizan");
  check(await page.evaluate(() => window.__noReload === true), "alternar: la página no se recargó");

  await done.locator("button.task-item__toggle").click();
  await page.locator("li.task-item:not(.task-item--done)", { hasText: title }).first().waitFor({ state: "visible", timeout: 5000 });
  check(true, "alternar de vuelta: queda pendiente");

  await page.locator("li.task-item", { hasText: title }).first().locator("button.task-item__delete").click();
  await page.locator("li.task-item", { hasText: title }).waitFor({ state: "detached", timeout: 5000 });
  check(true, "eliminar: la fila sale de la lista");
  check(await page.evaluate(() => window.__noReload === true), "eliminar: la página no se recargó");

  // an empty title is refused with the message under the field
  await page.fill('input[name="titulo"]', "   ");
  await page.click('button[type="submit"]');
  const error = page.locator(".field__error").first();
  await error.waitFor({ state: "visible", timeout: 5000 });
  check((await error.innerText()).includes("Escribí"), "validación: el error se lee bajo el campo");

  // the home page shows the module and the mobile bar is there at 390
  await page.goto(`${base}/`, { waitUntil: "networkidle" });
  check((await page.locator("h1").innerText()).includes("Panel personal"), "inicio: el h1 se lee");
  await page.setViewportSize({ width: 390, height: 844 });
  const barVisible = await page.locator("nav.tabbar").isVisible();
  const railHidden = await page.locator("aside.rail").isVisible();
  check(barVisible && !railHidden, "móvil: barra inferior visible y rail oculto");
  check((await page.locator("nav.tabbar a").count()) === 5, "móvil: cinco destinos en la barra");

  // the phone creates through the bottom sheet, not the inline form
  await page.goto(`${base}/tareas/`, { waitUntil: "networkidle" });
  const fab = page.locator("[data-abrir-hoja]");
  const sheetForm = page.locator("#form-tarea");
  check(await fab.isVisible(), "móvil: el botón + está visible");
  check(!(await sheetForm.isVisible()), "móvil: el formulario fijo está oculto (la lista va arriba)");
  const fabBox = await fab.boundingBox();
  const barBox = await page.locator("nav.tabbar").boundingBox();
  check(fabBox && barBox && fabBox.y + fabBox.height <= barBox.y, "móvil: el + queda por encima de la barra");
  const listTop = (await page.locator("#lista-tareas").boundingBox()).y;
  const countersBottom = (await page.locator("#contadores-tareas").boundingBox()).y + (await page.locator("#contadores-tareas").boundingBox()).height;
  check(listTop - countersBottom < 80, "móvil: la lista arranca debajo de los contadores");

  await fab.click();
  await sheetForm.waitFor({ state: "visible", timeout: 5000 });
  check((await page.locator(".task-compose__sheet").getAttribute("role")) === "dialog", "hoja: abre como diálogo");
  const sheetTitle = `Hoja e2e ${Date.now()}`;
  await page.fill('input[name="titulo"]', sheetTitle);
  await page.selectOption('select[name="prioridad"]', "M");
  await page.click('button[type="submit"]');
  await page.locator("li.task-item", { hasText: sheetTitle }).first().waitFor({ state: "visible", timeout: 5000 });
  await sheetForm.waitFor({ state: "hidden", timeout: 5000 });
  check(true, "hoja: al crear la tarea se cierra sola");
  check((await fab.getAttribute("aria-expanded")) === "false", "hoja: el botón vuelve a aria-expanded=false");

  await fab.click();
  await sheetForm.waitFor({ state: "visible", timeout: 5000 });
  await page.mouse.click(6, 6);
  await sheetForm.waitFor({ state: "hidden", timeout: 5000 });
  check(true, "hoja: tocar fuera la cierra");

  // leave the development database as it was found
  const created = page.locator("li.task-item", { hasText: sheetTitle }).first();
  await created.locator("button.task-item__delete").click();
  await created.waitFor({ state: "detached", timeout: 5000 });

  check(errors.length === 0, `consola sin errores${errors.length ? ": " + errors.slice(0, 3).join(" | ") : ""}`);

  // background refresh: another device adds a task; this page picks it up without touching the form
  const deviceA = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  deviceA.on("dialog", (d) => d.accept());
  await deviceA.goto(`${base}/tareas/`, { waitUntil: "networkidle" });
  await deviceA.evaluate(() => (window.__sinRecarga = true));
  await deviceA.fill('input[name="titulo"]', "borrador sin guardar");
  const mutaciones = await deviceA.evaluate(
    () =>
      new Promise((resolve) => {
        let n = 0;
        const obs = new MutationObserver((lista) => {
          n += lista.length;
        });
        obs.observe(document.getElementById("lista-tareas"), {
          childList: true,
          subtree: true,
          characterData: true,
          attributes: true,
        });
        setTimeout(() => {
          obs.disconnect();
          resolve(n);
        }, 6000);
      }),
  );
  check(mutaciones === 0, "refresco: sin cambios no toca el DOM (sin parpadeo)");
  check(await deviceA.evaluate(() => window.__sinRecarga === true), "refresco: la página no se recargó");

  const deviceB = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  deviceB.on("dialog", (d) => d.accept());
  await deviceB.goto(`${base}/tareas/`, { waitUntil: "networkidle" });
  const remota = `Remota ${Date.now()}`;
  await deviceB.fill('input[name="titulo"]', remota);
  await deviceB.click('button[type="submit"]');
  await deviceB.locator("li.task-item", { hasText: remota }).first().waitFor({ state: "visible", timeout: 5000 });

  const remotaEnA = deviceA.locator("li.task-item", { hasText: remota }).first();
  await remotaEnA.waitFor({ state: "visible", timeout: 9000 });
  check(true, "refresco: la tarea cargada en otro dispositivo aparece sola");
  check((await deviceA.inputValue('input[name="titulo"]')) === "borrador sin guardar", "refresco: no borra lo que se está escribiendo");
  check(await deviceA.evaluate(() => window.__sinRecarga === true), "refresco: sigue sin recargar la página");

  await remotaEnA.locator("button.task-item__delete").click();
  await remotaEnA.waitFor({ state: "detached", timeout: 5000 });
  await deviceA.close();
  await deviceB.close();
} finally {
  await browser.close();
}

if (failures.length) {
  console.error(`\n${failures.length} failure(s)`);
  process.exit(1);
}
console.log("\ne2e: ok");
