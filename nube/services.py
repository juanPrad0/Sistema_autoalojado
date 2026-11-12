"""Safe access to the personal cloud folder.

Every path that reaches the module is resolved and checked to be a strict child of
settings.NUBE_ROOT_DIR, so a request can never escape the storage folder (RNF-06).
"""

from pathlib import Path

from django.conf import settings


class RutaInsegura(Exception):
    """Raised when a requested path resolves outside the cloud root."""


def raiz() -> Path:
    root = Path(settings.NUBE_ROOT_DIR).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def resolver(relativa: str = "") -> Path:
    root = raiz()
    candidata = (root / relativa).resolve() if relativa else root
    if candidata != root and root not in candidata.parents:
        raise RutaInsegura(f"La ruta sale de {root.name}/: {relativa!r}")
    return candidata


def listar(relativa: str = "") -> list[Path]:
    destino = resolver(relativa)
    if not destino.is_dir():
        raise NotADirectoryError(relativa)
    return sorted(destino.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))


def contar_archivos() -> int:
    return sum(1 for ruta in raiz().rglob("*") if ruta.is_file())
