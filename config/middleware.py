"""Host validation for entries Django cannot express as ALLOWED_HOSTS patterns.

Django accepts exact hosts and ".domain" suffixes only. A self-hosted panel reached
through Tailscale gets a 100.x address that can change, so the operator writes "100.*"
in .env. This middleware validates that prefix (and an optional CIDR) before any view
calls get_host(), then adds the resolved host to the allowed list.
"""

import ipaddress

from django.conf import settings


def _hostname(raw: str) -> str:
    raw = raw.strip().lower()
    if raw.startswith("["):
        end = raw.find("]")
        return raw[1:end] if end != -1 else raw
    if raw.count(":") == 1:
        return raw.split(":", 1)[0]
    return raw


def _raw_host(request) -> str:
    """HTTP_HOST, or the test client's SERVER_NAME:PORT (the same host get_host() will validate)."""
    host = request.META.get("HTTP_HOST")
    if host:
        return host
    name = request.META.get("SERVER_NAME", "")
    port = request.META.get("SERVER_PORT", "")
    return f"{name}:{port}" if name and port else name


def _address(hostname: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(hostname)
    except ValueError:
        return None


class PrefixHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.prefixes = tuple(getattr(settings, "ALLOWED_HOST_PREFIXES", ()))
        self.network = getattr(settings, "TAILSCALE_NETWORK", None)

    def __call__(self, request):
        hostname = _hostname(_raw_host(request))
        if hostname and self._permitted(hostname):
            if hostname not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append(hostname)
        return self.get_response(request)

    def _permitted(self, hostname: str) -> bool:
        if hostname in settings.ALLOWED_HOSTS:
            return True
        address = _address(hostname)
        if address is None:
            return False
        if any(hostname.startswith(prefix) for prefix in self.prefixes):
            return True
        if self.network is not None and address in self.network:
            return True
        return False
