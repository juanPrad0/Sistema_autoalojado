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
