import tempfile
from pathlib import Path

from django.test import SimpleTestCase, TestCase, override_settings

from nube import services


class ResolverTests(SimpleTestCase):
    def test_resolver_acepta_la_raiz_y_sus_hijos(self):
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(NUBE_ROOT_DIR=Path(tmp)):
                raiz = services.raiz()
                self.assertEqual(services.resolver(""), raiz)
                (raiz / "carpeta").mkdir()
                self.assertEqual(services.resolver("carpeta"), (raiz / "carpeta").resolve())

    def test_resolver_bloquea_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "nube"
            with override_settings(NUBE_ROOT_DIR=root):
                services.raiz()
                for ruta in ("../", "../../etc/passwd", "carpeta/../../fuera"):
                    with self.assertRaises(services.RutaInsegura):
                        services.resolver(ruta)

    def test_contar_archivos(self):
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(NUBE_ROOT_DIR=Path(tmp)):
                raiz = services.raiz()
                (raiz / "a.txt").write_text("uno", encoding="utf-8")
                (raiz / "sub").mkdir()
                (raiz / "sub" / "b.txt").write_text("dos", encoding="utf-8")
                self.assertEqual(services.contar_archivos(), 2)


class NubeVistaTests(TestCase):
    def test_index_responde(self):
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(NUBE_ROOT_DIR=Path(tmp)):
                response = self.client.get("/nube/")
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Nube")
                self.assertContains(response, "archivos")
