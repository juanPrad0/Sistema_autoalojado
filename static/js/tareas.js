/* Bottom sheet for creating a task on a phone (under 768px).
   On a desktop the same form is inline and none of this runs. */
(function () {
  var panel = document.querySelector("[data-hoja-tarea]");
  var trigger = document.querySelector("[data-abrir-hoja]");
  if (!panel || !trigger) return;

  var sheet = panel.querySelector(".task-compose__sheet");
  var query = window.matchMedia("(min-width: 768px)");
  var isOpen = function () {
    return panel.classList.contains("is-abierta");
  };
  var input = function () {
    return panel.querySelector('input[name="titulo"]');
  };

  function open() {
    panel.classList.add("is-abierta");
    sheet.setAttribute("role", "dialog");
    sheet.setAttribute("aria-modal", "true");
    trigger.setAttribute("aria-expanded", "true");
    document.body.classList.add("hoja-abierta");
    var field = input();
    if (field) field.focus({ preventScroll: true });
  }

  function close(returnFocus) {
    if (!isOpen()) return;
    panel.classList.remove("is-abierta");
    sheet.removeAttribute("role");
    sheet.removeAttribute("aria-modal");
    trigger.setAttribute("aria-expanded", "false");
    document.body.classList.remove("hoja-abierta");
    if (returnFocus !== false) trigger.focus({ preventScroll: true });
  }

  function focusables() {
    return Array.prototype.filter.call(
      sheet.querySelectorAll('a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'),
      function (el) {
        return el.offsetParent !== null;
      },
    );
  }

  trigger.addEventListener("click", function () {
    if (isOpen()) close();
    else open();
  });

  // tapping the dimmed background closes it; taps inside the sheet do not
  panel.addEventListener("click", function (event) {
    if (event.target === panel) close();
  });

  Array.prototype.forEach.call(panel.querySelectorAll("[data-cerrar-hoja]"), function (button) {
    button.addEventListener("click", function () {
      close();
    });
  });

  document.addEventListener("keydown", function (event) {
    if (!isOpen()) return;
    if (event.key === "Escape") {
      close();
      return;
    }
    if (event.key !== "Tab") return;
    var items = focusables();
    if (!items.length) return;
    var first = items[0];
    var last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  // the create response carries HX-Trigger: tarea-creada
  document.body.addEventListener("tarea-creada", function () {
    if (isOpen()) close();
    else {
      var field = input();
      if (field) field.focus({ preventScroll: true });
    }
  });

  // a phone rotated into the desktop layout keeps the inline form, not a modal
  var onChange = function (event) {
    if (event.matches) close(false);
  };
  if (query.addEventListener) query.addEventListener("change", onChange);
  else query.addListener(onChange);
})();

/* Background refresh: every 5 seconds the list alone is re-fetched. The response carries an ETag
   built from the rows; if nothing changed the server answers 304 and the DOM is left untouched, so
   there is no flicker. The form is never part of the swap, so a draft in the input survives. */
(function () {
  var lista = document.getElementById("lista-tareas");
  if (!lista) return;
  var url = lista.getAttribute("data-refresh-url");
  if (!url) return;

  var intervalo = 5000;
  var enCurso = false;
  var timer = null;

  function versionActual() {
    var marcador = document.getElementById("lista-version");
    return (marcador && marcador.getAttribute("data-version")) || lista.getAttribute("data-version") || "";
  }

  function guardarVersion(version) {
    if (!version) return;
    lista.setAttribute("data-version", version);
    var marcador = document.getElementById("lista-version");
    if (marcador) marcador.setAttribute("data-version", version);
  }

  async function refrescar() {
    if (enCurso || document.hidden) return;
    // a local create/toggle/delete in flight wins: its fragment already updates the list
    if (document.querySelector(".htmx-request")) return;
    enCurso = true;
    try {
      var version = versionActual();
      var respuesta = await fetch(url, {
        headers: version ? { "If-None-Match": '"' + version + '"' } : {},
        cache: "no-store",
        credentials: "same-origin",
      });
      if (respuesta.status === 304 || !respuesta.ok) return;
      var etag = (respuesta.headers.get("ETag") || "").replace(/"/g, "");
      if (etag && etag === version) return; // same rows: do not touch the DOM
      var html = await respuesta.text();
      lista.innerHTML = html;
      // the injected rows carry hx-* attributes; htmx must bind them or their buttons do nothing
      if (window.htmx) window.htmx.process(lista);
      guardarVersion(etag || version);
    } catch (error) {
      /* offline or the server is resting: keep the list on screen, retry on the next tick */
    } finally {
      enCurso = false;
    }
  }

  function parar() {
    if (timer) {
      window.clearInterval(timer);
      timer = null;
    }
  }

  function arrancar() {
    parar();
    timer = window.setInterval(refrescar, intervalo);
  }

  document.addEventListener("visibilitychange", function () {
    if (document.hidden) parar();
    else {
      refrescar();
      arrancar();
    }
  });

  arrancar();
})();
