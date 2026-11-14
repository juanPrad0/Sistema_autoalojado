from django.test import TestCase, override_settings

from config.middleware import _hostname


class HostnameTests(TestCase):
    def test_hostname_quita_puerto(self):
        self.assertEqual(_hostname("localhost:8000"), "localhost")
        self.assertEqual(_hostname("[::1]:8000"), "::1")
        self.assertEqual(_hostname("100.101.102.103"), "100.101.102.103")


@override_settings(ALLOWED_HOSTS=["localhost", "127.0.0.1"])
class PrefixHostMiddlewareTests(TestCase):
    def test_tailscale_100_aceptado(self):
        response = self.client.get("/", SERVER_NAME="100.101.102.103")
        self.assertEqual(response.status_code, 200)

    def test_host_ajeno_rechazado(self):
        response = self.client.get("/", SERVER_NAME="203.0.113.9")
        self.assertEqual(response.status_code, 400)

    def test_localhost_aceptado(self):
        response = self.client.get("/", SERVER_NAME="localhost")
        self.assertEqual(response.status_code, 200)


class PwaTests(TestCase):
    def test_desarrollo_no_registra_el_service_worker(self):
        response = self.client.get("/")
        self.assertContains(response, "sw-limpio")
        self.assertNotContains(response, "serviceWorker.register")
        self.assertContains(response, "css/app.css?v=")

    @override_settings(PWA_ENABLED=True)
    def test_la_bandera_activa_el_registro(self):
        response = self.client.get("/")
        self.assertContains(response, "serviceWorker.register")
        self.assertNotContains(response, "sw-limpio")
