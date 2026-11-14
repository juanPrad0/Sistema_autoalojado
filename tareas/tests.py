from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from tareas.models import Tarea


class TareaModelTests(TestCase):
    def test_defaults(self):
        tarea = Tarea.objects.create(titulo="Revisar el panel")
        self.assertFalse(tarea.completada)
        self.assertEqual(tarea.prioridad, Tarea.Prioridad.MEDIA)
        self.assertIsNone(tarea.fecha_limite)

    def test_vencida_only_when_pending_and_past(self):
        ayer = timezone.localdate() - timedelta(days=1)
        vencida = Tarea.objects.create(titulo="Vieja", fecha_limite=ayer, prioridad="A")
        hecha = Tarea.objects.create(titulo="Hecha", fecha_limite=ayer, completada=True)
        self.assertTrue(vencida.vencida)
        self.assertFalse(hecha.vencida)

    def test_para_hoy(self):
        tarea = Tarea.objects.create(titulo="Hoy", fecha_limite=timezone.localdate())
        self.assertTrue(tarea.para_hoy)


class TareasVistasTests(TestCase):
    def setUp(self):
        self.tarea = Tarea.objects.create(titulo="Configurar Tailscale", prioridad="A")

    def test_index_lista_tareas(self):
        response = self.client.get(reverse("tareas:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Configurar Tailscale")
        self.assertContains(response, 'id="lista-tareas"')

    def test_crear_guarda_y_devuelve_el_fragmento(self):
        response = self.client.post(
            reverse("tareas:crear"),
            {"titulo": "  Cargar la nube  ", "prioridad": "B", "fecha_limite": "2026-12-01"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        tarea = Tarea.objects.get(titulo="Cargar la nube")
        self.assertEqual(tarea.prioridad, "B")
        self.assertEqual(tarea.fecha_limite, date(2026, 12, 1))
        self.assertContains(response, f'id="tarea-{tarea.pk}"')
        self.assertNotContains(response, "<html")
        self.assertContains(response, 'hx-swap-oob="outerHTML"')
        self.assertEqual(response["HX-Trigger"], "tarea-creada")

    def test_crear_vacio_devuelve_el_formulario_con_error(self):
        response = self.client.post(
            reverse("tareas:crear"),
            {"titulo": "   ", "prioridad": "M"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["HX-Retarget"], "#form-tarea")
        self.assertEqual(response["HX-Reswap"], "outerHTML")
        self.assertContains(response, "Escribí qué hay que hacer.")
        self.assertEqual(Tarea.objects.count(), 1)

    def test_alternar_completa_y_devuelve_el_item(self):
        response = self.client.post(
            reverse("tareas:alternar", args=[self.tarea.pk]),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.tarea.refresh_from_db()
        self.assertTrue(self.tarea.completada)
        self.assertContains(response, 'aria-pressed="true"')
        self.assertContains(response, 'id="tarea-%d"' % self.tarea.pk)
        self.assertNotContains(response, "<html")

    def test_eliminar_borra_y_devuelve_los_contadores(self):
        response = self.client.delete(
            reverse("tareas:eliminar", args=[self.tarea.pk]),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Tarea.objects.filter(pk=self.tarea.pk).exists())
        self.assertContains(response, 'id="contadores-tareas"')
        self.assertContains(response, 'id="tareas-vacio"')
        self.assertNotContains(response, "<html")

    def test_toggle_no_acepta_get(self):
        response = self.client.get(reverse("tareas:alternar", args=[self.tarea.pk]))
        self.assertEqual(response.status_code, 405)


class ResumenTests(TestCase):
    def test_resumen_cuenta_pendientes(self):
        Tarea.objects.create(titulo="Una", prioridad="A")
        Tarea.objects.create(titulo="Otra", completada=True)
        response = self.client.get(reverse("resumen"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tareas_pendientes"], 1)
        self.assertEqual(response.context["tareas_completadas"], 1)
        self.assertContains(response, "Panel personal")
