import json
import time
import threading

from .bottle import request
from ..mission.mission_ocr import MissionOCR


def init(UmiWeb):
    @UmiWeb.route("/api/ocr/get_options")
    def _get_options():
        opts = MissionOCR.getLocalOptions()
        print("=== ", opts)
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
  base64: 'iVBORw0KGgoAAAANSUhEUgAAAG8AAAAeCAIAAACt2ddTAAAACXBIWXMAABnWAAAZ1gEY0crtAAAAEXRFWHRTb2Z0d2FyZQBTbmlwYXN0ZV0Xzt0AAAPESURBVGiB7VkxkqM6EG22/lHQBFM+gXwCtMlETp1BiJLNJnQ2iQhR5tSRk0EngBO4JrC4izaQ7REgCWGY2qpfvMwWtJrX3a9bECmlYMVC+PWvHfhfYWVzSaxsLomVzSVhZ1NkURRlYqbtttg+Y0Zkkf02vz29OhXborWYGfxreOZ7Hiub4swB0rckxEXHxgDQfp6am5kJEBnhgJksB7eJD9pAWg0XDKSVMlGlg796q8vCxmZ7vXRYcPpjujPkHdEGADgJyJBMPAwQDgANRZ01gFuILebc4RQZ4ZC+Itf68rCw2X6emskpBXFem0RLhsGXF1088g0zOTCinSoOfGDNWB8+RbElHAA4RagfAE8E5mHIpvigDWZ/JpJpMQKzrTzQFnvaTAhwW2wRbSzR1NWUvufxMo71MGBTnDnA5mXWbm1x4IDZMZdZWJWPmdtPCbDIIkSbtFJVyolhvi22EeGQVsorvXPQY7MtDnyuybbY00bHPymdxX3T3ACSrp+nxp5O8qux7H7gmElVJpCUkmFOoigTbbGNEG1uC6MwddsAsSm3qRr/dayIDzr0DziJ3BQPlCugyI1CDHi2l7xWOYDIovPb+PWxvvrxQ8IWUYIgdDcAAMBM1s+IgZmbbXHgGA+F/Vt9qnT4s4O79rtxyxIITZM7xJkDJ5b24VAlcRMZRIFJpW5Z+pMtCEw222JPgR3fN+ZynNfK/dBJqZQZQ13jPtyuSCtlj323xJBhLSlVlUJDkV9nr/dB7fx2j3mdx+bIIXcnFKbX0/HNpvwCdpzT60SGaJNWvrFFwzOBOyckANA6CJz4eHi5s1Ym5ghs3HLn1eGDTYuD8c1mUnbTRVj6sVWGtbciI7xzhLHdr7NtygTeRZwfGbYXvPXqRz6+HiZt5OhClth04X7r0evHkmHQooox7qaQUqpM+lVv7+eSYdtMHy75cX5kePK8+OB1dKP2egHPqWOk8ALfIYkM0U1Vv28AYPN+3J32PyflI4jzerR7PepisjjKrwYAv6LnfAthU2QRuZhFHOfH3Qn9YG8MQ3u9OJ78XhcVkLAS7Zrc/X6yfYyxqQ8QadUrkTiv5e6EfqQxLoiu2kh2IX5O9az8NJleNvVoCI7BMM5rHfspjM7qmFZjEw7BI91cv3OadYh3samZ3FR+4U5KFcCo0d0J9x+T3POmxcMDH7w+DXr/ZzjT8ZJw7/QWgn7X6h13JizOhGTYOm8+thv2087VjnHBgyr9NmHZ3emke5dIrd/Tl8P6lW1JrGwuiZXNJbGyuSRWNpfEX+tARcvne0KCAAAAAElFTkSuQmCC',
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
