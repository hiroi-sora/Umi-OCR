import json
import time
import threading

from .bottle import request
from ..mission.mission_ocr import MissionOCR


def init(UmiWeb):
    @UmiWeb.route("/api/ocr/get_options")
    def _get_options():
        opts = MissionOCR.getLocalOptions()
        res = json.dumps(opts)
        return res

    """
    执行OCR，方法：POST
    参数：
    "base64": "", # 必填
    "options": {}, # 选填，内容与 _get_options 的对应。
    """

    @UmiWeb.route("/api/ocr", method="POST")
    def _ocr():
        condition = threading.Condition()
        ocrData = None

        def onGet(msnInfo, msn, res):
            nonlocal ocrData
            ocrData = res
            with condition:
                condition.notify()

        def onEnd(msnInfo, msg):
            nonlocal ocrData
            if not ocrData:
                ocrData = {"code": 803, "data": f"未知原因，未获取OCR返回值。{msg}"}
            with condition:
                condition.notify()

        data = request.json
        if not data:
            return json.dumps({"code": 800, "data": f"请求为空。"})
        if "base64" not in data:
            return json.dumps({"code": 801, "data": f"请求中缺少 base64 字段。"})
        if "options" not in data:
            return json.dumps({"code": 802, "data": f"请求中缺少 options 字段。"})
        msnList = [{"base64": data["base64"]}]
        options = data["options"]
        opt = {}
        for k in options:
            if "ocr." not in options:
                opt["ocr." + k] = options[k]
        msnInfo = {"onGet": onGet, "onEnd": onEnd, "argd": opt}
        MissionOCR.addMissionList(msnInfo, msnList)
        with condition:
            condition.wait()
        res = json.dumps(ocrData)
        return res


"""
const url = 'http://127.0.0.1:1224/api/ocr';
const data = {
  base64: 'iVBORw0KGgoAAAANSUhEUgAAAC4AAAAXCAIAAAD7ruoFAAAACXBIWXMAABnWAAAZ1gEY0crtAAAAEXRFWHRTb2Z0d2FyZQBTbmlwYXN0ZV0Xzt0AAAHjSURBVEiJ7ZYrcsMwEEBXnR7FLuj0BPIJHJOi0DAZ2qSsMCxEgjYrDQqJdALrBJ2ASndRgeNI8ledutOCLrLl1e7T/mRkjIG/IXe/DWBldRTNEoQSpgNURe5puiiaJehrMuJSXSTgbaby0A1WzLrCCQCmyn0FwoN0V06QONWAt1nUxfnjHYA8p65GjhDKxcjedVH6JOejBPwYh21eE0Wzfe0tqIsEkGXcVcpoMH4CRZ+P0lsQp/pWJ4ripf1XFDFe8GHSHlYcSo9Es31t60RdFlN1RUmrma5oTzTVB8ZUaeeYEC9GmL6kNkDw9BANAQYo3xTNdqUkvHq+rYhDKW0Bj3RSEIpmyWyBaZaMTCrCK+tJ5Jsa07fs3E7esE66HzralRLgJKp0/BD6fJRSxvmDsb6joqkcFXGqMVVFFEHDL2gTxwCAaTabnkFUWhDCHTd9iYrGcAL1ZnqIp5Vpiqh7bCfua7FA4qN0INMcN1+cgCzj+UFxtbmvwdZvGIrI41JiqhZBWhhF8WxorkYPpQwJiWYJeA3rXE4hzcwJ+B96F9zCFHC0FcVegghvFul7oeEE8PvHeJqC0w0AUbbFIT8JnEwGbPKcS2OxU3HMTqD0r4wgEIuiKJ7i4MS16+og8/+bPZRPLa+6Ld2DSzcAAAAASUVORK5CYII=',
    options: {
        angle: false,
        language: "简体中文(V4)",
        maxSideLen: 1024
    }
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
})
  .then(response => response.json())
  .then(data => {
    console.log(data);
  })
  .catch(error => {
    console.error(error);
  });



const url = 'http://127.0.0.1:1224/api/ocr/get_options';
fetch(url, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  },
})
  .then(response => response.json())
  .then(data => {
    console.log(data);
  })
  .catch(error => {
    console.error(error);
  });
"""
