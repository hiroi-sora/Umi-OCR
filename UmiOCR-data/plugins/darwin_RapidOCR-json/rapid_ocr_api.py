# RapidOCR API implementation for macOS with CoreML EP support

import os
import sys
import base64
import io

from umi_log import logger


class RapidOcrApi:
    def __init__(self, argd):
        self.argd = argd
        self.engine = None
        self._coreml_available = False
        self._patched = False

    def start(self, argd):
        """Initialize or reconfigure the RapidOCR engine."""
        try:
            use_coreml = argd.get("use_coreml", True)
            lang = argd.get("language", "ch")
            model_type = argd.get("model_type", "mobile")

            # Check if engine needs to be recreated
            need_recreate = (
                self.engine is None
                or self.argd.get("language") != lang
                or self.argd.get("model_type") != model_type
                or self.argd.get("use_coreml") != use_coreml
            )
            self.argd = argd

            if not need_recreate:
                return "[Success]"

            # Stop existing engine
            if self.engine is not None:
                self.stop()

            # Apply CoreML EP monkey-patch before importing rapidocr
            if use_coreml and sys.platform == "darwin":
                self._apply_coreml_patch()
            elif self._patched:
                self._remove_coreml_patch()

            try:
                from rapidocr import RapidOCR, EngineType, LangDet, LangRec, ModelType
            except ImportError:
                msg = (
                    "OCR engine not installed.\n"
                    "OCR 引擎未安装。\n\n"
                    "Please run install_ocr.command in the app bundle to install,\n"
                    "or run in Terminal:\n"
                    "  pip install rapidocr onnxruntime\n\n"
                    "请双击 .app 包中的 install_ocr.command 安装 OCR 引擎。"
                )
                logger.error(msg)
                return f"[Error] {msg}"

            # Map UI language key to RapidOCR enums
            det_lang_map = {
                "ch": LangDet.CH,
                "en": LangDet.EN,
                "ch_cht": LangDet.CH,
                "japan": LangDet.MULTI,
                "korean": LangDet.MULTI,
            }
            rec_lang_map = {
                "ch": LangRec.CH,
                "en": LangRec.EN,
                "ch_cht": LangRec.CHINESE_CHT,
                "japan": LangRec.JAPAN,
                "korean": LangRec.KOREAN,
            }

            # Build params dict
            params = {
                "Det.engine_type": EngineType.ONNXRUNTIME,
                "Cls.engine_type": EngineType.ONNXRUNTIME,
                "Rec.engine_type": EngineType.ONNXRUNTIME,
                "Det.lang_type": det_lang_map.get(lang, LangDet.CH),
                "Rec.lang_type": rec_lang_map.get(lang, LangRec.CH),
            }

            # Set model type (mobile = faster, server = more accurate)
            mt = ModelType.SERVER if model_type == "server" else ModelType.MOBILE
            params["Det.model_type"] = mt
            params["Rec.model_type"] = mt

            self.engine = RapidOCR(params=params)

            ep_info = "CoreML EP" if self._coreml_available else "CPU"
            logger.info(f"RapidOCR engine started: lang={lang}, model={model_type}, backend={ep_info}")
            return "[Success]"

        except Exception as e:
            logger.error(f"Failed to start RapidOCR: {e}", exc_info=True)
            return f"[Error] Failed to initialize RapidOCR engine: {e}"

    def stop(self):
        """Stop the OCR engine and clean up resources."""
        self.engine = None
        if self._patched:
            self._remove_coreml_patch()

    def runPath(self, img_path):
        """Run OCR on an image file path."""
        if not self.engine:
            return {"code": 901, "data": "[Error] Engine not initialized"}
        try:
            result = self.engine(img_path)
            return self._format_result(result)
        except Exception as e:
            logger.error(f"runPath failed: {e}", exc_info=True)
            return {"code": 902, "data": f"[Error] OCR failed: {e}"}

    def runBytes(self, img_bytes):
        """Run OCR on raw image bytes."""
        if not self.engine:
            return {"code": 901, "data": "[Error] Engine not initialized"}
        try:
            result = self.engine(img_bytes)
            return self._format_result(result)
        except Exception as e:
            logger.error(f"runBytes failed: {e}", exc_info=True)
            return {"code": 902, "data": f"[Error] OCR failed: {e}"}

    def runBase64(self, img_base64):
        """Run OCR on a base64-encoded image string."""
        if not self.engine:
            return {"code": 901, "data": "[Error] Engine not initialized"}
        try:
            img_bytes = base64.b64decode(img_base64)
            result = self.engine(img_bytes)
            return self._format_result(result)
        except Exception as e:
            logger.error(f"runBase64 failed: {e}", exc_info=True)
            return {"code": 902, "data": f"[Error] OCR failed: {e}"}

    def _format_result(self, result):
        """Convert RapidOCR result to Umi-OCR format.

        RapidOCR result has:
          result.boxes  - numpy array (N, 4, 2) or None
          result.txts   - tuple of strings or None
          result.scores - tuple of floats or None

        Umi-OCR expects:
          {"code": 100, "data": [{"text", "score", "box", "end"}, ...]}
        """
        if result is None or result.boxes is None or len(result.boxes) == 0:
            return {"code": 100, "data": []}

        data = []
        boxes = result.boxes
        txts = result.txts
        scores = result.scores

        for i in range(len(txts)):
            # box: numpy array (4, 2) -> list of [x, y] pairs
            box = boxes[i].tolist() if hasattr(boxes[i], "tolist") else list(boxes[i])
            data.append(
                {
                    "text": txts[i],
                    "score": float(scores[i]),
                    "box": box,
                    "end": "",
                }
            )

        return {"code": 100, "data": data}

    def _apply_coreml_patch(self):
        """Monkey-patch onnxruntime.InferenceSession to use CoreML EP on macOS."""
        if self._patched:
            return
        try:
            import onnxruntime as ort

            if "CoreMLExecutionProvider" not in ort.get_available_providers():
                logger.info("CoreML EP not available, using CPU only")
                self._coreml_available = False
                return

            self._coreml_available = True
            self._original_session_init = ort.InferenceSession.__init__

            coreml_providers = [
                (
                    "CoreMLExecutionProvider",
                    {
                        "ModelFormat": "MLProgram",
                        "MLComputeUnits": "ALL",
                    },
                ),
                "CPUExecutionProvider",
            ]

            original_init = self._original_session_init

            def patched_init(session_self, *args, **kwargs):
                # Inject CoreML providers if not explicitly set
                if "providers" not in kwargs or kwargs["providers"] is None:
                    kwargs["providers"] = coreml_providers
                return original_init(session_self, *args, **kwargs)

            ort.InferenceSession.__init__ = patched_init
            self._patched = True
            logger.info("CoreML EP patch applied for GPU/ANE acceleration")

        except ImportError:
            logger.warning("onnxruntime not found, CoreML EP unavailable")
            self._coreml_available = False

    def _remove_coreml_patch(self):
        """Remove the CoreML EP monkey-patch."""
        if not self._patched:
            return
        try:
            import onnxruntime as ort

            if hasattr(self, "_original_session_init"):
                ort.InferenceSession.__init__ = self._original_session_init
            self._patched = False
            logger.info("CoreML EP patch removed")
        except ImportError:
            pass
