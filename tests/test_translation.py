import importlib.util
from pathlib import Path
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError


path = Path(__file__).resolve().parents[1] / "UmiOCR-data/py_src/utils/translation.py"
spec = importlib.util.spec_from_file_location("translation", path)
translation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(translation)


class TranslationTests(unittest.TestCase):
    def setUp(self):
        translation._cache.clear()

    def test_repeated_text_uses_cache(self):
        with patch.object(translation, "_get_json", return_value=[[["你好"]]]) as request:
            self.assertEqual(translation.translate("Hello"), "你好")
            self.assertEqual(translation.translate("Hello"), "你好")
            self.assertEqual(request.call_count, 1)

    def test_cache_separates_languages_and_provider(self):
        def respond(url, params, timeout):
            if "mymemory" in url:
                return {"responseStatus": 200, "responseData": {"translatedText": "译文"}}
            return [[["译文"]]]
        with patch.object(translation, "_get_json", side_effect=respond) as request:
            translation.translate("Hello")
            translation.translate("Hello", source="auto")
            translation.translate("Hello", target="ja")
            translation.translate("Hello", provider="mymemory")
            self.assertEqual(request.call_count, 4)

    def test_force_refresh_bypasses_and_updates_cache(self):
        with patch.object(translation, "_get_json", side_effect=[[[["旧译文"]]], [[["新译文"]]]]) as request:
            self.assertEqual(translation.translate("Hello"), "旧译文")
            self.assertEqual(translation.translate("Hello", use_cache=False), "新译文")
            self.assertEqual(translation.translate("Hello"), "新译文")
            self.assertEqual(request.call_count, 2)

    def test_expired_cache_is_refreshed(self):
        with patch.object(translation, "_get_json", return_value=[[["译文"]]]) as request:
            translation.translate("Hello")
            key = ("google", "en", "zh-CN", "Hello")
            translation._cache[key] = (translation.time.monotonic() - translation._CACHE_TTL - 1, "过期译文")
            self.assertEqual(translation.translate("Hello"), "译文")
            self.assertEqual(request.call_count, 2)

    def test_cache_size_is_bounded(self):
        with patch.object(translation, "_CACHE_SIZE", 2), patch.object(translation, "_get_json", return_value=[[["译文"]]]):
            translation.translate("One")
            translation.translate("Two")
            translation.translate("One")
            translation.translate("Three")
            self.assertEqual(len(translation._cache), 2)
            self.assertNotIn(("google", "en", "zh-CN", "Two"), translation._cache)

    def test_cancelled_request_does_not_return_cached_result(self):
        with patch.object(translation, "_get_json", return_value=[[["你好"]]]):
            translation.translate("Hello")
            cancel = threading.Event()
            cancel.set()
            with self.assertRaises(translation.TranslationError):
                translation.translate("Hello", cancelled=cancel)

    def test_utf8_chunks_are_lossless_and_within_provider_limit(self):
        text = ("这是中文。Hello world!\n日本語 테스트 😀 " * 70) + "尾"
        chunks = list(translation.split_text(text, 450))
        self.assertEqual("".join(chunks), text)
        self.assertTrue(all(len(c.encode("utf-8")) <= 450 for c in chunks))

    def test_unbroken_multibyte_text(self):
        text = "😀" * 500
        chunks = list(translation.split_text(text, 450))
        self.assertEqual("".join(chunks), text)
        self.assertTrue(all(len(c.encode("utf-8")) <= 450 for c in chunks))

    def test_empty_and_same_language_do_not_use_network(self):
        with patch.object(translation, "_get_json") as request:
            self.assertEqual(translation.translate(" \n"), " \n")
            self.assertEqual(translation.translate("Hello", "en", "en"), "Hello")
            request.assert_not_called()

    def test_google_auto_and_multiple_segments(self):
        with patch.object(translation, "_get_json", return_value=[[["你好", "Hello"], ["世界", "world"]]]) as request:
            self.assertEqual(translation.translate("Hello world", "auto"), "你好世界")
            self.assertEqual(request.call_args[0][1]["sl"], "auto")
            self.assertEqual(request.call_args[0][1]["tl"], "zh-CN")

    def test_chunk_whitespace_preserved(self):
        with patch.object(translation, "_get_json", return_value=[[["译文"]]]):
            self.assertEqual(translation.translate("  Hello\n"), "  译文\n")

    def test_mymemory_unescapes_entities(self):
        response = {"responseStatus": 200, "responseData": {"translatedText": "你好 &amp; 世界"}}
        with patch.object(translation, "_get_json", return_value=response) as request:
            self.assertEqual(translation.translate("Hello", provider="mymemory"), "你好 & 世界")
            self.assertEqual(request.call_args[0][1]["langpair"], "en|zh-CN")

    def test_quota_failure_is_not_presented_as_translation(self):
        with patch.object(translation, "_get_json", return_value={"responseStatus": 403, "quotaFinished": True}):
            with self.assertRaises(translation.TranslationError):
                translation.translate("Hello", provider="mymemory")

    def test_invalid_mymemory_responses(self):
        for data in [None, [], {"responseStatus": 200, "responseData": None},
                     {"responseStatus": 200, "responseData": {"translatedText": ""}}]:
            with self.subTest(data=data), patch.object(translation, "_get_json", return_value=data):
                with self.assertRaises(translation.TranslationError):
                    translation.translate("Hello", provider="mymemory")

    def test_invalid_google_responses(self):
        for data in [None, [], {}, [[None]], [[[None]]]]:
            with self.subTest(data=data), patch.object(translation, "_get_json", return_value=data):
                with self.assertRaises(translation.TranslationError):
                    translation.translate("Hello")

    def test_invalid_settings_and_length(self):
        for kwargs in [{"source": "unknown"}, {"target": "auto"}, {"provider": "unknown"},
                       {"provider": "mymemory", "source": "auto"}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(translation.TranslationError):
                translation.translate("Hello", **kwargs)
        with self.assertRaises(translation.TranslationError):
            translation.translate("x" * 20001)

    def test_cancelled_request_does_not_use_network(self):
        cancel = threading.Event()
        cancel.set()
        with patch.object(translation, "_get_json") as request:
            with self.assertRaises(translation.TranslationError):
                translation.translate("Hello", cancelled=cancel)
            request.assert_not_called()

    def test_cancel_between_chunks(self):
        cancel = threading.Event()
        def respond(*args):
            cancel.set()
            return [[["译文"]]]
        with patch.object(translation, "_get_json", side_effect=respond) as request:
            with self.assertRaises(translation.TranslationError):
                translation.translate("x" * 7000, cancelled=cancel)
            self.assertEqual(request.call_count, 1)

    def test_network_errors_are_readable(self):
        for error in [HTTPError("url", 429, "limit", {}, None), URLError("offline"), TimeoutError()]:
            with self.subTest(error=error), patch.object(translation, "urlopen", side_effect=error):
                with self.assertRaises(translation.TranslationError):
                    translation._get_json("https://example.com", {}, 1)


class WindowsProxyTests(unittest.TestCase):
    def handler(self, rules):
        handler = translation._WindowsProxyHandler({"https": "http://127.0.0.1:7897", "no": ""})
        del handler.proxies["no"]
        handler._exceptions = rules
        return handler

    def test_windows_proxy_rules_do_not_trigger_reverse_dns(self):
        handler = self.handler(["<local>", "*.example.com", "localhost", "127.*", "service.test:8443"])
        with patch("socket.getfqdn", side_effect=AssertionError("reverse DNS must not run")), \
                patch("socket.gethostbyaddr", side_effect=AssertionError("reverse DNS must not run")):
            for host in ["intranet", "sub.example.com", "localhost", "127.0.0.1", "service.test:8443"]:
                self.assertTrue(handler._bypass(host), host)
            self.assertFalse(handler._bypass("translate.googleapis.com"))
            self.assertFalse(handler._bypass("service.test:443"))

    def test_environment_no_proxy_is_respected(self):
        handler = translation._WindowsProxyHandler({"https": "http://127.0.0.1:7897", "no": ".example.com"})
        self.assertTrue(handler._bypass("sub.example.com"))
        self.assertFalse(handler._bypass("translate.googleapis.com"))

    def test_https_tunnel_and_proxy_auth_are_preserved(self):
        handler = self.handler([])
        request = translation.Request("https://translate.googleapis.com/translate_a/single")
        handler.proxy_open(request, "http://test:password@127.0.0.1:7897", "https")
        self.assertEqual(request.host, "127.0.0.1:7897")
        self.assertEqual(request._tunnel_host, "translate.googleapis.com")
        self.assertTrue(request.get_header("Proxy-authorization").startswith("Basic "))

    def test_bypassed_host_is_not_tunneled(self):
        handler = self.handler(["*.example.com"])
        request = translation.Request("https://api.example.com/test")
        handler.proxy_open(request, "http://127.0.0.1:7897", "https")
        self.assertEqual(request.host, "api.example.com")
        self.assertIsNone(request._tunnel_host)


if __name__ == "__main__":
    unittest.main()
