import os
import json
from uuid import uuid4

from .bottle import request
from .ocr_server import get_ocr_options, check_ocr_options
from ..mission.mission_doc import MissionDOC
from ..utils.utils import initConfigDict, DocSuf
from ..ocr.output.tools import getDataText

UPLOAD_DIR = "./temp"  # 上传文件目录


# 获取参数模板字典
def get_doc_options():
    opts = get_ocr_options(is_format=False)
    opts["tbpu.ignoreRangeStart"] = {
        "title": "忽略区域起始",
        "toolTip": "忽略区域生效的页数范围起始。从1开始。",
        "default": 1,
    }
    opts["tbpu.ignoreRangeEnd"] = {
        "title": "忽略区域结束",
        "toolTip": "忽略区域生效的页数范围结束。可以用负数表示倒数第X页。",
        "default": -1,
    }
    opts["pageRangeStart"] = {
        "title": "OCR页数起始",
        "toolTip": "OCR的页数范围起始。从1开始。",
        "default": 1,
    }
    opts["pageRangeEnd"] = {
        "title": "OCR页数结束",
        "toolTip": "OCR的页数范围结束。可以用负数表示倒数第X页。",
        "default": -1,
    }
    opts["pageList"] = {
        "title": "OCR页数列表",
        "toolTip": "数组，可指定单个或多个页数。例：[1,2,5]表示对第1、2、5页进行OCR。如果与页数范围同时填写，则 pageList 优先。",
        "default": [],
        "type": "var",
    }
    opts["password"] = {
        "title": "密码",
        "toolTip": "如果文档已加密，则填写文档密码。",
        "default": "",
    }
    opts["doc.extractionMode"] = {
        "title": "内容提取模式",
        "toolTip": "若一页文档既存在图片又存在文本，如何进行处理。",
        "default": "",
        "optionsList": [
            ["mixed", "混合OCR/原文本"],
            ["fullPage", "整页强制OCR"],
            ["imageOnly", "仅OCR图片"],
            ["textOnly", "仅拷贝原有文本"],
        ],
    }
    opts = initConfigDict(opts)  # 格式化
    return opts


# 单个任务字典
class _DocUnit:
    def __init__(self, file_path, options):
        # 补充缺失的默认参数
        default = get_doc_options()
        for key in default:
            if key not in options:
                options[key] = default[key]["default"]

        # 提取参数
        pageRange = [options["pageRangeStart"], options["pageRangeEnd"]]  # 识别范围
        pageList = options["pageList"]  # 页数列表
        password = options["password"]  # 密码

        # MissionDoc 任务参数字典
        docArgd = {
            "tbpu.ignoreArea": options["tbpu.ignoreArea"],
            "tbpu.ignoreRangeStart": options["tbpu.ignoreRangeStart"],
            "tbpu.ignoreRangeEnd": options["tbpu.ignoreRangeEnd"],
        }
        for k in options:
            if k.startswith("ocr.") or k.startswith("doc."):
                docArgd[k] = options[k]

        # 任务信息
        msnInfo = {
            "onStart": self._onStart,
            "onReady": self._onReady,
            "onGet": self._onGet,
            "onEnd": self._onEnd,
            "argd": docArgd,
        }

        # 提交任务
        self.msnID = MissionDOC.addMission(
            msnInfo, file_path, pageRange, pageList, password
        )

    # ========================= 【任务控制器的异步回调】 =========================

    def _onStart(self, msnInfo):  # 一个文档 开始
        msnID = msnInfo["msnID"]
        print(f"_onStart: {msnID}")

    def _onReady(self, msnInfo, page):  # 一个文档的一页 准备开始
        msnID = msnInfo["msnID"]
        page += 1
        print(f"_onReady: {msnID} | {page}")

    def _onGet(self, msnInfo, page, res):  # 一个文档的一页 获取结果
        page += 1
        msnID = msnInfo["msnID"]
        res["page"] = page

        print(f"_onGet: {msnID} | {page}")
        # print(res)

    def _onEnd(self, msnInfo, msg):  # 一个文档处理完毕
        # msg: [Success] [Warning] [Error]

        msnID = msnInfo["msnID"]
        print(f"_onEnd: {msnID} | {msg}")


# 路由函数
def init(UmiWeb):
    # 确保上传文件目录存在
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    """
    上传文档，方法：POST
    参数：文档内容
    返回值：
    成功： {"code": 100, "data": "任务id"}
    失败： {"code": 不是100的值, "data": "失败原因"}
    """

    @UmiWeb.route("/api/doc/upload", method="POST")
    def _upload():
        # 1. 获取上传文件
        upload = request.files.get("file")
        if not upload:
            return {"code": 101, "data": "[Error] No file was uploaded."}

        # 2. 检查文件后缀
        name, ext = os.path.splitext(upload.filename)
        ext = ext.lower()
        if ext not in DocSuf:
            return {
                "code": 102,
                "data": f"[Error] File extension '{ext}' is not allowed.",
            }

        # 3. 指定文件编号。保存文件
        file_id = str(uuid4())
        save_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
        try:
            upload.save(save_path, overwrite=True)
        except Exception as e:
            return {"code": 103, "data": f"[Error] Failed to save file: {e}"}

        # 4. 提取 options 参数
        options = request.forms.get("json")
        if options:
            try:
                options = json.loads(options)
            except Exception as e:
                return {
                    "code": 104,
                    "data": f"[Error] Invalid JSON format: {options} | {e}",
                }
        if not isinstance(options, dict):
            options = {}

        # 5. 构造任务对象
        try:
            doc_unit = _DocUnit(save_path, options)
            msnID = doc_unit.msnID
            return {"code": 100, "data": msnID}
        except Exception as e:
            return {"code": 105, "data": f"[Error] Failed to submit mission: {e}"}
