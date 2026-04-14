# OCR engine on-demand installer for macOS
# Downloads and installs rapidocr + onnxruntime into site-packages.

import os
import sys
import subprocess

from umi_log import logger
from ..event_bus.pubsub_service import PubSubService


def is_ocr_installed():
    """Check if the OCR engine dependencies are importable."""
    try:
        import rapidocr  # noqa: F401
        import onnxruntime  # noqa: F401
        return True
    except ImportError:
        return False


def install_ocr_engine():
    """Install OCR dependencies via pip into the app's site-packages.

    Publishes events:
      - "ocr_install_progress": (message_str,)
      - "ocr_install_done": (success_bool, message_str)
    """
    try:
        # Find site-packages directory
        sp_dir = None
        for p in sys.path:
            if p.endswith("site-packages") and os.path.isdir(p):
                sp_dir = p
                break

        if not sp_dir:
            sp_dir = os.path.join(os.getcwd(), "site-packages")

        # Find requirements-ocr.txt
        req_file = None
        # Check in Resources/ (app bundle layout)
        for candidate in [
            os.path.join(os.getcwd(), "..", "requirements-ocr.txt"),
            os.path.join(os.getcwd(), "requirements-ocr.txt"),
        ]:
            if os.path.isfile(candidate):
                req_file = os.path.abspath(candidate)
                break

        PubSubService.publish(
            "ocr_install_progress",
            "正在下载 OCR 引擎...\nDownloading OCR engine..."
        )
        logger.info(f"Installing OCR engine to {sp_dir}")

        # Build pip command
        packages = ["rapidocr>=2.0.0", "onnxruntime>=1.17.0"]
        cmd = [
            sys.executable, "-m", "pip", "install",
            "--target", sp_dir,
            "--upgrade",
        ]

        if req_file:
            cmd += ["-r", req_file]
        else:
            cmd += packages

        # Ensure the subprocess can find pip in the bundled Python's own site-packages.
        # The bundled Python's pip lives at <PYTHONHOME>/lib/pythonX.Y/site-packages/
        env = os.environ.copy()
        python_home = os.path.dirname(os.path.dirname(sys.executable))
        py_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"
        bundled_sp = os.path.join(python_home, "lib", py_ver, "site-packages")
        if os.path.isdir(bundled_sp):
            existing = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = bundled_sp + (":" + existing if existing else "")
        env["PYTHONHOME"] = python_home

        logger.info(f"Running: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
            env=env,
        )

        if result.returncode == 0:
            logger.info("OCR engine installed successfully")
            PubSubService.publish(
                "ocr_install_done",
                True,
                "OCR 引擎安装成功！请重启应用。\nOCR engine installed! Please restart the app."
            )
        else:
            err = result.stderr[-500:] if result.stderr else "Unknown error"
            logger.error(f"pip install failed: {err}")
            PubSubService.publish(
                "ocr_install_done",
                False,
                f"安装失败 / Install failed:\n{err}"
            )

    except subprocess.TimeoutExpired:
        logger.error("OCR install timed out")
        PubSubService.publish(
            "ocr_install_done",
            False,
            "安装超时，请检查网络连接。\nInstall timed out. Check your network."
        )
    except Exception as e:
        logger.error(f"OCR install error: {e}", exc_info=True)
        PubSubService.publish(
            "ocr_install_done",
            False,
            f"安装出错 / Install error:\n{e}"
        )
