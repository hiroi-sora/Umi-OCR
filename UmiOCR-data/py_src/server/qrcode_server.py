import json
import base64
from io import BytesIO

from .bottle import request
from ..mission.mission_qrcode import MissionQRCode


# 从base64识别二维码图片。传入base64字符串，返回字典 {"code", "data"}
def base2text(base64):
    res = MissionQRCode.addMissionWait({}, [{"base64": base64}])
    return res[0]["result"]


# 从文本生成base64。传入data指令字典 {"text","xxx"}
# 返回  {"code", "data"}
def text2base(data):
    text = data["text"]
    opt = data.get("options", {})
    format = opt.get("format", "QRCode")
    w = opt.get("w", 0)
    h = opt.get("h", 0)
    quiet_zone = opt.get("quiet_zone", -1)
    ec_level = opt.get("ec_level", -1)
    try:
        pil = MissionQRCode.createImage(text, format, w, h, quiet_zone, ec_level)
        buffered = BytesIO()
        pil.save(buffered, format="JPEG")
        b64 = base64.b64encode(buffered.getvalue()).decode("ascii")
        res = {"code": 100, "data": b64}
    except Exception as e:
        res = {"code": 200, "data": f"[Error] {str(e)}"}
    return res


# 路由函数
def init(UmiWeb):

    @UmiWeb.route("/api/qrcode", method="POST")
    def _qrcode():
        try:
            data = request.json
        except Exception as e:
            return json.dumps({"code": 800, "data": f"请求无法解析为json。"})
        if not data:
            return json.dumps({"code": 801, "data": f"请求为空。"})

        if "base64" in data:
            return json.dumps(base2text(data["base64"]))
        elif "text" in data:
            return json.dumps(text2base(data))
        return json.dumps({"code": 802, "data": '指令中不存在 "base64" 或 "text"'})


"""
// 文本 → 二维码base64
const url = "http://127.0.0.1:1224/api/qrcode";
const text = "测试文本";
const data = {
    // 必填
    "text": text,
    // 选填
    "options": {
        "format": "QRCode", // 码类型
        "w": 0, // 图像宽度，0为自动设为最小宽度
        "h": 0, // 图像高度
        "quiet_zone": -1, // 码四周的空白边缘宽度，-1为自动
        "ec_level": -1, // 纠错等级，-1为自动
    }
};

fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if(data.code === 100) {
            console.log("生成二维码base64：", data.data);
        }
        else {
            console.log("生成二维码base64失败！错误码：", data.code, " 错误信息：", data.data);
        }
    })
    .catch(error => {
        console.error(error);
    });


// 二维码base64 → 文本
const url = "http://127.0.0.1:1224/api/qrcode";
const base64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAAdAB0BAREA/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/9oACAEBAAA/APU/GfjM+EjAzW9o0DW8txNPdXEkSxKkkMYAEcUjMS069hjBrn3+K0yi3B0/RozO52y3OtG3gaPy7WRWV5IVJO27DFSoIEbYycCrF18Sb2z1a20u70rTbO8uLiKzigutRl3NcNDBIyAxW7rhTcIu4sAcE8Cu00LU/wC2/D2mat5Pk/brSK58rdu2b0Dbc4GcZxnAri/iSdPGs6AuqySW+nzpcW11dg27xwIzQspkimikDIZUiG/5QhK5PzCuPI1qz8ISalajUtNu1czLGsxnt7tHhhhiijNmkSF22W8aFeFWZ2RjIjeVXvrq0t/EWmaTpq3d9rTXFpCqpa2iRW92sCJOUP2WZYjEsNszrG7Bd/GNhr2zQtP/ALI8PaZpuMfY7SK3x5nmY2IF+9tXd067Vz6DpXH/ABK1LVrN7SLTIr6622k159isYYnknkjuLVUI8yGXGzzWfhc5UHPFeeSyav4dtI9R8O+Ho5dYS4WNrSK1EV2sb29ncFJY7aOPzIkkYhjhSGaME7WdHy72y8NWthbfDxrrfDDdpdXH2eVvtIu/IcStcOUaCGFMqGKNKUELZDEsU+g/DUcMXhXSI7cRrAllCsYjIKhQgxgh3BGP9t/95upk1PQtH1vyv7W0qxv/ACc+X9rt0l2ZxnG4HGcDp6Co7Xw1oNiipaaJptuiPvVYbVEAbcjZGB13RxnPqin+EYksdC0fTIo4rDSrG0jjlM6JBbpGFkKlC4AHDFSVz1wcdKuQQQ2tvFb28UcMESBI441CqigYAAHAAHGK/9k="
const data = { "base64": base64 };

fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if(data.code === 100) {
            console.log("识别二维码成功！图片中的二维码数量：", data.data.length);
            console.log("所有码的内容：");
            for (let d of data.data) {
                console.log("    文本：", d.text);
                console.log("    格式：", d.format);
                console.log("    方向：", d.orientation);
                console.log("    ====");
            }
        }
        else {
            console.log("识别二维码失败！错误码：", data.code, " 错误信息：", data.data);
        }
    })
    .catch(error => {
        console.error(error);
    });
"""
