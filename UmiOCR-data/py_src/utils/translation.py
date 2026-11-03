"""Free online translation adapters. No additional runtime dependencies."""

import html
import base64
import json
import re
import sys
import time
from collections import OrderedDict
from fnmatch import fnmatchcase
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, unquote, urlsplit
from urllib.request import (
    Request, ProxyHandler, build_opener, getproxies,
    proxy_bypass_environment, _parse_proxy,
)


LANGUAGES = {"auto", "en", "zh-CN", "zh-TW", "ja", "ko", "fr", "de",
             "es", "ru", "pt", "it", "ar", "vi", "th"}

_cache = OrderedDict()
_cache_lock = Lock()
_CACHE_TTL = 600
_CACHE_SIZE = 128


class _WindowsProxyHandler(ProxyHandler):
    """Avoid CPython 3.8's reverse DNS lookup for every Windows proxy check.

    Match explicit host/port and <local> exceptions without resolving the target.
    IP exceptions only match literal IP destinations, not resolved hostnames.
    """

    def __init__(self, proxies):
        super().__init__(proxies)
        self._exceptions = []
        if "no" not in proxies:
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion\Internet Settings") as key:
                    self._exceptions = winreg.QueryValueEx(key, "ProxyOverride")[0].split(";")
            except OSError:
                pass

    def _bypass(self, host):
        if "no" in self.proxies:
            return proxy_bypass_environment(host, self.proxies)
        hostname = urlsplit("//" + host).hostname or host
        for pattern in self._exceptions:
            pattern = pattern.strip().lower()
            if pattern == "<local>":
                if "." not in hostname and ":" not in hostname:
                    return True
            elif pattern and (fnmatchcase(host.lower(), pattern)
                              or fnmatchcase(hostname.lower(), pattern)):
                return True
        return False

    def proxy_open(self, req, proxy, type):
        # Same proxy/tunnel/auth handling as urllib, using hostname-only bypass.
        orig_type = req.type
        proxy_type, user, password, hostport = _parse_proxy(proxy)
        proxy_type = proxy_type or orig_type
        if req.host and self._bypass(req.host):
            return None
        if user and password:
            credentials = (unquote(user) + ":" + unquote(password)).encode()
            req.add_header("Proxy-authorization", "Basic " + base64.b64encode(credentials).decode("ascii"))
        req.set_proxy(unquote(hostport), proxy_type)
        if orig_type == proxy_type or orig_type == "https":
            return None
        return self.parent.open(req, timeout=req.timeout)


def urlopen(request, timeout):
    # Scope the workaround to translation; keep TLS verification and OS proxies.
    proxies = getproxies()
    handler = _WindowsProxyHandler(proxies) if sys.platform == "win32" else ProxyHandler(proxies)
    return build_opener(handler).open(request, timeout=timeout)


class TranslationError(Exception):
    pass


def split_text(text, max_bytes):
    """Split at sentence/word boundaries where possible, within UTF-8 limits."""
    while text:
        if len(text.encode("utf-8")) <= max_bytes:
            yield text
            return
        end = len(text.encode("utf-8")[:max_bytes].decode("utf-8", "ignore"))
        boundaries = list(re.finditer(r"[\n。！？.!?\s]+", text[:end]))
        if boundaries and boundaries[-1].end() >= end // 2:
            end = boundaries[-1].end()
        yield text[:end]
        text = text[end:]


def _get_json(url, params, timeout):
    request = Request(url + "?" + urlencode(params), headers={
        "User-Agent": "Umi-OCR/2 Translation", "Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read(2 * 1024 * 1024 + 1)
            if len(raw) > 2 * 1024 * 1024:
                raise TranslationError("翻译服务返回的数据过大。")
            return json.loads(raw.decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 429:
            raise TranslationError("翻译服务请求过于频繁，请稍后重试或切换服务。") from exc
        raise TranslationError("翻译服务 HTTP 错误：%s" % exc.code) from exc
    except (URLError, OSError, ValueError) as exc:
        raise TranslationError("无法连接翻译服务或响应无效，请检查网络后重试。") from exc


def translate(text, source="en", target="zh-CN", provider="google", cancelled=None, use_cache=True):
    if source not in LANGUAGES or target not in LANGUAGES - {"auto"}:
        raise TranslationError("不支持所选语言。")
    if provider not in {"google", "mymemory"}:
        raise TranslationError("未知翻译服务。")
    if provider == "mymemory" and source == "auto":
        raise TranslationError("MyMemory 不支持自动检测，请指定源语言或切换 Google。")
    if not text.strip() or source == target:
        return text
    if len(text) > 20000:
        raise TranslationError("单次最多翻译 20000 个字符，请分段识别。")
    if cancelled and cancelled.is_set():
        raise TranslationError("翻译已取消。")
    cache_key = (provider, source, target, text)
    if use_cache:
        with _cache_lock:
            cached = _cache.get(cache_key)
            if cached and time.monotonic() - cached[0] < _CACHE_TTL:
                _cache.move_to_end(cache_key)
                return cached[1]
            _cache.pop(cache_key, None)
    deadline = time.monotonic() + 60
    result = []
    for chunk in split_text(text, 450 if provider == "mymemory" else 3500):
        if cancelled and cancelled.is_set():
            raise TranslationError("翻译已取消。")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TranslationError("翻译超时，请缩短文本或稍后重试。")
        if not chunk.strip():
            result.append(chunk)
            continue
        leading = chunk[:len(chunk) - len(chunk.lstrip())]
        trailing = chunk[len(chunk.rstrip()):]
        content = chunk.strip()
        if provider == "google":
            data = _get_json("https://translate.googleapis.com/translate_a/single", {
                "client": "gtx", "sl": source, "tl": target, "dt": "t", "q": content,
            }, min(12, remaining))
            try:
                translated = "".join(part[0] for part in data[0] if part[0])
            except (TypeError, IndexError, KeyError):
                raise TranslationError("Google 翻译响应格式异常。")
        else:
            data = _get_json("https://api.mymemory.translated.net/get", {
                "q": content, "langpair": source + "|" + target,
            }, min(12, remaining))
            if not isinstance(data, dict):
                raise TranslationError("MyMemory 翻译响应格式异常。")
            if data.get("quotaFinished") or str(data.get("responseStatus")) != "200":
                raise TranslationError("MyMemory 额度不足或请求失败，请稍后重试或切换服务。")
            response_data = data.get("responseData")
            if not isinstance(response_data, dict):
                raise TranslationError("MyMemory 翻译响应格式异常。")
            translated = response_data.get("translatedText")
            if isinstance(translated, str):
                translated = html.unescape(translated)
        if not isinstance(translated, str) or not translated.strip():
            raise TranslationError("翻译服务未返回有效译文。")
        result.append(leading + translated + trailing)
    translated_text = "".join(result)
    if cancelled and cancelled.is_set():
        raise TranslationError("翻译已取消。")
    with _cache_lock:
        _cache[cache_key] = (time.monotonic(), translated_text)
        _cache.move_to_end(cache_key)
        while len(_cache) > _CACHE_SIZE:
            _cache.popitem(last=False)
    return translated_text
