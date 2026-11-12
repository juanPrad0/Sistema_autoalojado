"""Django settings for the self-hosted personal dashboard."""

import ipaddress
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def env_bool(name: str, default: bool = False) -> bool:
    return env(name, str(default)).lower() in {"1", "true", "yes", "on"}


SECRET_KEY = env("SECRET_KEY", "dev-only-insecure-key-set-SECRET_KEY-in-dotenv")
DEBUG = env_bool("DEBUG", True)

# Django only understands exact hosts and ".domain" suffixes. Entries written as a
# prefix wildcard ("100.*", for the Tailscale range) are kept aside and validated by
# config.middleware.PrefixHostMiddleware, which appends the resolved host at request time.
_raw_hosts = [h.strip() for h in env("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]
ALLOWED_HOSTS = [h for h in _raw_hosts if not h.endswith(".*")]
ALLOWED_HOST_PREFIXES = tuple(h[:-1] for h in _raw_hosts if h.endswith(".*"))
TAILSCALE_CIDR = env("TAILSCALE_CIDR", "100.64.0.0/10")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "portafolio",
    "tareas",
    "horarios",
    "nube",
]

MIDDLEWARE = [
    "config.middleware.PrefixHostMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context.modulos",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Personal cloud storage (module 4). Every path is validated against this root.
NUBE_ROOT_DIR = Path(env("NUBE_ROOT_DIR", str(BASE_DIR / "almacenamiento_nube")))

# Finnhub free tier: 60 HTTP requests per minute; the service caches in memory.
FINNHUB_API_KEY = env("FINNHUB_API_KEY")

_csrf = [o.strip() for o in env("CSRF_TRUSTED_ORIGINS").split(",") if o.strip()]
CSRF_TRUSTED_ORIGINS = _csrf or [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# The Tailscale range is private; keeping DEBUG on a personal LAN is a decision the
# operator makes in .env, never an implicit default in production.
if not DEBUG:
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", False)
    CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", False)


def _tailscale_network() -> ipaddress.IPv4Network | ipaddress.IPv6Network | None:
    try:
        return ipaddress.ip_network(TAILSCALE_CIDR, strict=False)
    except ValueError:
        return None


TAILSCALE_NETWORK = _tailscale_network()
