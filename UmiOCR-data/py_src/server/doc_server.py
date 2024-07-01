import os
import json
import time
import shutil
from uuid import uuid4
from PySide2.QtCore import QMutex

from .bottle import request
from .ocr_server import get_ocr_options
from ..ocr.output import Output
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


# 异常类
class DocUnitError(Exception):
    def __init__(self, data):
        self.data = data


# 单个任务单元
class _DocUnit:
    def __init__(self, dir_id, dir_path, origin_path, origin_name, options):
        # 提取文档信息
        doc_info = MissionDOC.getDocInfo(origin_path)
        if "error" in doc_info.keys():
            raise DocUnitError({"code": 201, "data": doc_info["error"]})

        # 补充缺失的默认参数
        default = get_doc_options()
        for key in default:
            if key not in options:
                options[key] = default[key]["default"]

        # 提取参数
        page_range = [options["pageRangeStart"], options["pageRangeEnd"]]  # 识别范围
        page_list = options["pageList"]  # 页数列表
        if page_list:  # 下标起始由1转为0
            page_list = [x - 1 for x in page_list]
        password = options["password"]  # 密码
        if not password and doc_info["is_encrypted"]:
            raise DocUnitError(
                {
                    "code": 202,
                    "data": "The doc is encrypted, please fill in the password.",
                }
            )

        # 从 options 中提取一些条目，组装 docArgd 作为 MissionDoc 任务参数字典
        prefixes = ["ocr.", "doc.", "tbpu."]  # 要提取的条目前缀
        doc_argd = {}
        for k, v in options.items():
            for prefix in prefixes:
                if k.startswith(prefix):
                    doc_argd[k] = v
                    break

        # 任务信息
        msnInfo = {
            "onStart": self._onStart,
            "onGet": self._onGet,
            "onEnd": self._onEnd,
            "argd": doc_argd,
        }

        # 提交任务
        self.msnID = ""
        msg = MissionDOC.addMission(
            msnInfo, origin_path, page_range, page_list, password
        )
        if not msg:
            raise DocUnitError({"code": 203, "data": "addMission unknow."})
        if msg.startswith("["):
            raise DocUnitError({"code": 204, "data": msg})
        page_list = msnInfo["pageList"]

        self.password = password
        self.dir_id = dir_id
        self.dir_path = dir_path
        self.origin_name = origin_name
        self.origin_path = origin_path
        self.msnID = msg  # 任务ID
        self.results = {}  # 任务结果原始字典，键为页数
        self.pages_count = len(page_list)  # 任务总页数
        self.processed_count = 0  # 已处理的页数
        self.unread_list = []  # 未读的任务列表
        self.is_done = False  #  当前任务是否完成
        self.state = "waiting"  # 任务状态， waiting running success failure
        self.message = ""  # 如果任务失败，则记录失败信息
        self.start_timestamp = time.time()  # 开始时间戳
        self._mutex = QMutex()  # 主锁

    # ========================= 【获取接口】 =========================

    # 获取结果
    def get_result(
        self,
        is_data=False,  # True 时返回识别内容data
        format="dict",  # 识别内容格式， "dict", "text"
        is_unread=False,  # True 时只返回未读过的识别内容
    ):
        self._mutex.lock()
        data = {
            "code": 100,
            "processed_count": self.processed_count,  # 已处理的数量
            "pages_count": self.pages_count,  # 总页数
            "is_done": self.is_done,  # 是否已结束
            "state": self.state,  # 任务状态
            "data": [],  # 结果
        }
        if self.state == "failure":
            data["message"] = self.message
        # 需要返回识别内容
        if is_data:
            datas = []
            # 增量式
            if is_unread:
                for page in self.unread_list:
                    datas.append(self.results[page])
                self.unread_list = []
            # 全量式
            else:
                for _, res in self.results.items():
                    datas.append(res)
            # 需要转为纯文本
            if format == "text":
                datas_text = ""
                for res in datas:
                    if res["code"] == 100:
                        datas_text += getDataText(res["data"])
                datas = datas_text
            data["data"] = datas
        self._mutex.unlock()
        return data

    # 获取文件
    def get_files(
        self,
        file_types=["pdfLayered"],  # 输出文件类型，可选：
        # txt, txtPlain, jsonl, csv, pdfLayered, pdfOneLayer
        ingore_blank=True,  # 忽略空白页数
    ):
        if not self.is_done:
            return {"code": 201, "data": f"{self.msnID} 任务尚未结束，无法获取文件"}
        if not self.state == "success":
            return {"code": 201, "data": f"{self.msnID} 任务处理失败，无法获取文件"}
        if not isinstance(file_types, list) or not isinstance(ingore_blank, bool):
            return {
                "code": 202,
                "data": f"参数类型错误： file_types={file_types} , ingore_blank={ingore_blank}",
            }
        # 准备参数
        startDatetime = time.strftime(  # 日期时间字符串（标准格式）
            r"%Y-%m-%d %H:%M:%S", time.localtime(self.start_timestamp)
        )
        outputArgd = {
            "outputDir": self.dir_path,  # 输出路径
            "outputDirType": "specify",
            "outputFileName": "[OCR]_" + self.origin_name,  # 输出文件名（前缀）
            "startDatetime": startDatetime,  # 开始日期
            "ingoreBlank": ingore_blank,  # 忽略空白页数
            "originPath": self.origin_path,  # 原始文件
            "password": self.password,  # 文档密码
        }

        # 创建输出器
        output = []
        try:
            for f in file_types:
                output.append(Output[f](outputArgd))
        except Exception as e:
            return {"code": 203, "data": f"初始化输出器失败。{e}"}

        # 输出
        for o in output:
            for _, res in self.results.items():
                try:
                    o.print(res)
                except Exception as e:
                    return {"code": 204, "data": f"输出失败：{o}\n{e}"}
            try:
                o.onEnd()  # 保存
            except Exception as e:
                return {"code": 205, "data": f"保存失败：{o}\n{e}"}

        # 打包

        return {"code": 100, "data": f"Success"}

    # ========================= 【任务控制器的异步回调】 =========================

    def _onStart(self, msnInfo):  # 一个文档 开始
        self.state = "running"

    def _onGet(self, msnInfo, page, res):  # 一个文档的一页 获取结果
        page += 1
        res["page"] = page
        res["path"] = f"{self.origin_name} - {page}"
        res["fileName"] = f"{self.origin_name} - {page}"

        # 记录信息
        self._mutex.lock()
        self.results[page] = res
        self.processed_count += 1
        self.unread_list.append(page)
        self._mutex.unlock()

    def _onEnd(self, msnInfo, msg):  # 一个文档处理完毕
        # msg: [Success] [Warning] [Error]

        # 记录信息
        self._mutex.lock()
        self.is_done = True
        if msg == "[Success]":
            self.state = "success"
        else:
            self.state = "failure"
            self.message = msg
        self._mutex.unlock()


# 管理所有任务单元
class _DocUnitManagerClass:
    def __init__(self):
        self.doc_units = {}

    def add(self, id, unit):
        self.doc_units[id] = unit

    def get(self, id):
        if id not in self.doc_units:
            return None
        return self.doc_units[id]

    def remove(self, id):
        if id in self.doc_units:
            del self.doc_units[id]


_DocUnitManager = _DocUnitManagerClass()


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
        origin_name = upload.filename
        _, ext = os.path.splitext(origin_name)
        ext = ext.lower()
        if ext not in DocSuf:
            return {
                "code": 102,
                "data": f"[Error] File extension '{ext}' is not allowed.",
            }

        # 3. 指定文件编号。创建对应目录，保存文件到 ./temp/dir_id/原文件名
        dir_id = str(uuid4())
        dir_path = os.path.join(UPLOAD_DIR, f"{dir_id}")
        dir_path = os.path.abspath(dir_path)  # 将路径转为绝对路径
        file_path = os.path.join(dir_path, origin_name)
        try:
            if os.path.exists(dir_path):  # 如果目录存在，则删除该目录
                shutil.rmtree(dir_path)
            os.makedirs(dir_path)  # 重新创建目录
        except Exception as e:
            return {"code": 103, "data": f"[Error] Failed to create dir_id: {e}"}
        try:
            upload.save(file_path, overwrite=True)  # 保存文件
        except Exception as e:
            return {"code": 104, "data": f"[Error] Failed to save file: {e}"}

        # 4. 提取 options 参数
        options = request.forms.get("json")
        if options:
            try:
                options = json.loads(options)
            except Exception as e:
                shutil.rmtree(dir_path)
                return {
                    "code": 105,
                    "data": f"[Error] Invalid JSON format: {options} | {e}",
                }
        if not isinstance(options, dict):
            options = {}

        # 5. 构造任务对象
        try:
            doc_unit = _DocUnit(dir_id, dir_path, file_path, origin_name, options)
            msnID = doc_unit.msnID
            _DocUnitManager.add(msnID, doc_unit)
            return {"code": 100, "data": msnID}
        except DocUnitError as e:
            shutil.rmtree(dir_path)
            return e.data
        except Exception as e:
            shutil.rmtree(dir_path)
            return {"code": 106, "data": f"[Error] Failed to submit mission: {e}"}

    """
    获取结果，方法：POST
    json参数：
    "id"="",  # 任务ID
    "is_data"=False,  # True 时返回识别内容data
    "format"="dict",  # 识别内容格式， "dict", "text"
    "is_unread"=False,  # True 时只返回未读过的识别内容

    返回值： {}
    """

    @UmiWeb.route("/api/doc/result", method="POST")
    def _result():
        try:
            user_data = request.json
        except Exception as e:
            return {"code": 101, "data": f"请求无法解析为json。"}
        if not user_data or "id" not in user_data:
            return {"code": 102, "data": f"未填写id。"}
        msnID = user_data["id"]
        doc_unit = _DocUnitManager.get(msnID)
        if not doc_unit:
            return {"code": 103, "data": f"任务 {msnID} 不存在。"}
        is_data = user_data.get("is_data", False)
        format = user_data.get("format", "dict")
        is_unread = user_data.get("is_unread", False)
        return doc_unit.get_result(is_data, format, is_unread)

    """
    获取文件，方法：POST
    json参数：
    "id"="",  # 任务ID
    "file_types"=["pdfLayered"],  # 输出文件类型，可选：
    # ["txt", "txtPlain", "jsonl", "csv", "pdfLayered", "pdfOneLayer"]
    "ingore_blank"=True,  # 忽略空白页数

    返回值： {}
    """

    @UmiWeb.route("/api/doc/files", method="POST")
    def _files():
        try:
            user_data = request.json
        except Exception as e:
            return {"code": 101, "data": f"请求无法解析为json。"}
        if not user_data or "id" not in user_data:
            return {"code": 102, "data": f"未填写id。"}
        msnID = user_data["id"]
        doc_unit = _DocUnitManager.get(msnID)
        if not doc_unit:
            return {"code": 103, "data": f"任务 {msnID} 不存在。"}

        file_types = user_data.get("file_types", ["pdfLayered"])
        ingore_blank = user_data.get("ingore_blank", True)

        return doc_unit.get_files(file_types, ingore_blank)
