"""
aurea.core.http_client — Unified HTTP client with rate limiting, retry, and SSL.
"""

import json
import ssl
import time
import urllib.error
import urllib.request
from typing import Any



# --- Rate Limiting (Token Bucket per domain) ---

_rate_limits: dict[str, dict] = {}
_DEFAULT_RATE = {"max_per_min": 45, "interval": 60.0}

# Custom limits for known APIs
_DOMAIN_LIMITS = {
    "ip-api.com": {"max_per_min": 40, "interval": 60.0},
    "ipapi.co": {"max_per_min": 30, "interval": 60.0},
    "api.macvendors.com": {"max_per_min": 2, "interval": 1.0},
    "api.bgpkit.com": {"max_per_min": 60, "interval": 60.0},
}


def _get_domain(url: str) -> str:
    """Extract domain from URL."""
    url = url.split("://", 1)[-1]
    return url.split("/", 1)[0].split(":")[0]


def _check_rate_limit(domain: str) -> bool:
    """
    Check if we can make a request to this domain.
    Returns True if allowed, False if rate limited.
    """
    limits = _DOMAIN_LIMITS.get(domain, _DEFAULT_RATE)

    if domain not in _rate_limits:
        _rate_limits[domain] = {
            "count": 0,
            "last_reset": time.time(),
        }

    bucket = _rate_limits[domain]
    now = time.time()

    # Reset counter if interval has passed
    if now - bucket["last_reset"] >= limits["interval"]:
        bucket["count"] = 0
        bucket["last_reset"] = now

    if bucket["count"] >= limits["max_per_min"]:
        return False

    bucket["count"] += 1
    return True


# --- SSL Context ---

_ssl_context: ssl.SSLContext | None = None


def _get_ssl_context() -> ssl.SSLContext:
    """Get a secure SSL context (cached)."""
    global _ssl_context
    if _ssl_context is None:
        try:
            _ssl_context = ssl.create_default_context()
        except Exception:
            # Fallback for environments with broken cert stores
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            _ssl_context = ctx
    return _ssl_context


# --- Public API ---

USER_AGENT = "AureaTools/2.0 (NetworkDiag; +https://github.com/js-victr/aurea-tools)"


def _safe_urlopen(req, **kwargs):
    """Perform urlopen with automatic unverified SSL context fallback on cert verify failure."""
    try:
        return urllib.request.urlopen(req, **kwargs)
    except urllib.error.URLError as e:
        # Check if the failure is due to certificate verification issues
        if hasattr(e, "reason") and "CERTIFICATE_VERIFY_FAILED" in str(e.reason):
            unverified_ctx = ssl._create_unverified_context()
            kwargs["context"] = unverified_ctx
            return urllib.request.urlopen(req, **kwargs)
        raise e
    except Exception as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            unverified_ctx = ssl._create_unverified_context()
            kwargs["context"] = unverified_ctx
            return urllib.request.urlopen(req, **kwargs)
        raise e


def fetch_json(
    url: str,
    *,
    timeout: float = 5.0,
    retries: int = 2,
    headers: dict[str, str] | None = None,
    user_agent: str | None = None,
) -> dict[str, Any] | list | None:
    """
    Fetch JSON from a URL with rate limiting, retry, and SSL.

    Returns parsed JSON (dict or list), or None on failure.
    """
    domain = _get_domain(url)

    try:
        from aurea.core.ui import verbose
        verbose(f"Preparando requisição HTTP GET (JSON) para: {url} (Domínio: {domain})")
    except Exception:
        pass

    if not _check_rate_limit(domain):
        try:
            from aurea.core.ui import verbose
            verbose(f"RESTRITO: Requisição de API para '{domain}' bloqueada localmente pelo limitador de taxa (Rate Limiter).")
        except Exception:
            pass
        return None

    req_headers = {"User-Agent": user_agent or USER_AGENT}
    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(url, headers=req_headers)
    ctx = _get_ssl_context() if url.startswith("https") else None

    last_error = None
    for attempt in range(retries + 1):
        try:
            kwargs = {"timeout": timeout}
            if ctx:
                kwargs["context"] = ctx
            try:
                from aurea.core.ui import verbose
                verbose(f"Efetuando tentativa de download {attempt + 1}/{retries + 1} de {domain}...")
            except Exception:
                pass
            with _safe_urlopen(req, **kwargs) as res:
                data = json.loads(res.read().decode("utf-8"))
                try:
                    verbose(f"Sucesso: Dados JSON baixados com êxito de {domain} ({len(str(data))} caracteres).")
                except Exception:
                    pass
                return data

        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = min(2 ** attempt, 10)
                try:
                    from aurea.core.ui import verbose
                    verbose(f"SERVIDOR RETORNOU 429 (Rate Limit): Aguardando {wait}s antes de re-tentar...")
                except Exception:
                    pass
                time.sleep(wait)
                last_error = e
                continue
            last_error = e
            try:
                from aurea.core.ui import verbose
                verbose(f"ERRO HTTP {e.code}: Falha permanente ao requisitar {url}.")
            except Exception:
                pass
            break  # Don't retry other HTTP errors

        except Exception as e:
            last_error = e
            try:
                from aurea.core.ui import verbose
                verbose(f"ERRO DE CONEXÃO: {e} na tentativa {attempt + 1}. Tentando novamente...")
            except Exception:
                pass
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
            continue

    return None


def fetch_text(
    url: str,
    *,
    timeout: float = 5.0,
    headers: dict[str, str] | None = None,
    user_agent: str | None = None,
) -> str | None:
    """
    Fetch raw text from a URL.

    Returns the response body as string, or None on failure.
    """
    domain = _get_domain(url)

    try:
        from aurea.core.ui import verbose
        verbose(f"Preparando requisição HTTP GET (Text) para: {url} (Domínio: {domain})")
    except Exception:
        pass

    if not _check_rate_limit(domain):
        try:
            from aurea.core.ui import verbose
            verbose(f"RESTRITO: Requisição de texto para '{domain}' bloqueada localmente pelo limitador de taxa (Rate Limiter).")
        except Exception:
            pass
        return None

    req_headers = {"User-Agent": user_agent or USER_AGENT}
    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(url, headers=req_headers)
    ctx = _get_ssl_context() if url.startswith("https") else None

    try:
        kwargs = {"timeout": timeout}
        if ctx:
            kwargs["context"] = ctx
        with _safe_urlopen(req, **kwargs) as res:
            text_data = res.read().decode("utf-8")
            try:
                from aurea.core.ui import verbose
                verbose(f"Sucesso: Baixados {len(text_data)} caracteres em texto plano de {domain}.")
            except Exception:
                pass
            return text_data
    except Exception as e:
        try:
            from aurea.core.ui import verbose
            verbose(f"ERRO: Falha ao baixar texto de {url}: {e}")
        except Exception:
            pass
        return None


def fetch_headers(
    url: str,
    *,
    timeout: float = 8.0,
    user_agent: str = "AureaTools/2.0 (SecurityScan)",
) -> tuple[dict[str, str], int] | None:
    """
    Fetch HTTP response headers from a URL.

    Returns (headers_dict, status_code) or None on failure.
    Headers keys are lowercased.
    """
    domain = _get_domain(url)
    try:
        from aurea.core.ui import verbose
        verbose(f"Requisitando apenas cabeçalhos HTTP (HEAD) de: {url}")
    except Exception:
        pass

    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    ctx = _get_ssl_context() if url.startswith("https") else None

    try:
        kwargs = {"timeout": timeout}
        if ctx:
            kwargs["context"] = ctx
        with _safe_urlopen(req, **kwargs) as res:
            headers = {k.lower(): v for k, v in res.headers.items()}
            try:
                from aurea.core.ui import verbose
                verbose(f"Sucesso: {len(headers)} cabeçalhos capturados (HTTP Status: {res.status}).")
            except Exception:
                pass
            return headers, res.status
    except urllib.error.HTTPError as e:
        headers = {k.lower(): v for k, v in e.headers.items()}
        try:
            from aurea.core.ui import verbose
            verbose(f"Retornado erro HTTP {e.code} com {len(headers)} cabeçalhos.")
        except Exception:
            pass
        return headers, e.code
    except Exception as e:
        try:
            from aurea.core.ui import verbose
            verbose(f"ERRO: Falha ao requisitar cabeçalhos de {url}: {e}")
        except Exception:
            pass
        return None
