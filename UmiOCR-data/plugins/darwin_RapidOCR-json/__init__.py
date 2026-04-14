# darwin_RapidOCR-json — macOS OCR plugin using RapidOCR + ONNX Runtime (CoreML EP)
#
# Uses RapidOCR with PP-OCRv4 ONNX models. On Apple Silicon Macs, enables
# CoreML Execution Provider for GPU/Neural Engine acceleration.
# Falls back to CPU on Intel Macs or if CoreML EP is unavailable.

from .rapid_ocr_api import RapidOcrApi

# Plugin info registered by the plugin controller
PluginInfo = {
    "group": "ocr",
    "api_class": RapidOcrApi,
    # Global options: shown in the global settings panel under OCR API
    "global_options": {
        "title": "RapidOCR (macOS)",
        "type": "group",
        "use_coreml": {
            "title": "GPU加速 (CoreML)",
            "toolTip": "使用 Apple CoreML 加速推理（Apple Silicon 上启用 GPU / Neural Engine）。Intel Mac 自动回退到 CPU。",
            "default": True,
        },
        "model_type": {
            "title": "模型规格",
            "toolTip": "mobile 模型速度更快，server 模型精度更高。",
            "optionsList": [
                ["mobile", "mobile（轻量，推荐）"],
                ["server", "server（高精度）"],
            ],
            "default": "mobile",
        },
    },
    # Local options: shown per-task in each tab page's settings
    "local_options": {
        "title": "文字识别",
        "type": "group",
        "language": {
            "title": "识别语言",
            "toolTip": "选择要识别的文字语言。",
            "optionsList": [
                ["ch", "简体中文+英文"],
                ["ch_cht", "繁體中文+英文"],
                ["en", "English"],
                ["japan", "日本語"],
                ["korean", "한국어"],
            ],
            "default": "ch",
        },
    },
}
