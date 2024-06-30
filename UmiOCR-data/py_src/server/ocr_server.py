import json

from .bottle import request
from ..mission.mission_ocr import MissionOCR
from ..utils.utils import initConfigDict
from ..ocr.output.tools import getDataText


# 获取ocr配置字典。 is_format=False 时不含 format 选项。
def get_ocr_options(is_format=True):
    opts = {}
    # OCR 的参数
    ocr_opts = MissionOCR.getLocalOptions()
    for key in ocr_opts:
        opts[f"ocr.{key}"] = ocr_opts[key]
    # 排版解析的参数
    opts["tbpu.parser"] = {
        "title": "排版解析方案",
        "toolTip": "按什么方式，解析和排序图片中的文字块",
        "default": "multi_para",
        "optionsList": [
            ["multi_para", "多栏-按自然段换行"],
            ["multi_line", "多栏-总是换行"],
            ["multi_none", "多栏-无换行"],
            ["single_para", "单栏-按自然段换行"],
            ["single_line", "单栏-总是换行"],
            ["single_none", "单栏-无换行"],
            ["single_code", "单栏-保留缩进"],
            ["none", "不做处理"],
        ],
    }
    # 忽略区域
    opts["tbpu.ignoreArea"] = {
        "title": "忽略区域",
        "toolTip": "数组，每一项为[[左上角x,y],[右下角x,y]]。",
        "default": [],
        "type": "var",
    }
    # 输出格式
    if is_format:
        opts["data.format"] = {
            "title": "数据返回格式",
            "toolTip": '返回值字典中，["data"] 按什么格式表示OCR结果数据',
            "default": "dict",
            "optionsList": [
                ["dict", "含有位置等信息的原始字典"],
                ["text", "纯文本"],
            ],
        }
    opts = initConfigDict(opts)  # 格式化
    return opts


# 检查ocr参数字典，返回修改后字典
def check_ocr_options(opts):
    # 检查忽略区域参数
    if opts["tbpu.ignoreArea"]:
        new_ia = []
        ia = opts["tbpu.ignoreArea"]
        for a in ia:
            if (
                not isinstance(a, list)
                or len(a) != 2
                or not isinstance(a[0], list)
                or len(a[0]) != 2
                or not isinstance(a[1], list)
                or len(a[1]) != 2
                or not all(
                    isinstance(x, (int, float))
                    for x in [a[0][0], a[0][1], a[1][0], a[1][1]]
                )
            ):
                raise Exception(
                    f"tbpu.ignoreArea 中，每一项的格式必须是 [[x1,y1],[x2,y2]] 。当前值不合法： {ia}"
                )
            new_ia.append([[a[0][0], a[0][1]], [], [a[1][0], a[1][1]], []])
        opts["tbpu.ignoreArea"] = new_ia
    return opts


# 路由函数
def init(UmiWeb):
    @UmiWeb.route("/api/ocr/get_options")
    def _get_options_json():
        opts = get_ocr_options()
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
        try:
            data = request.json
        except Exception as e:
            return json.dumps({"code": 800, "data": f"请求无法解析为json。"})
        if not data:
            return json.dumps({"code": 801, "data": f"请求为空。"})
        if "base64" not in data:
            return json.dumps({"code": 802, "data": f"请求中缺少 base64 字段。"})
        if "options" not in data:
            data["options"] = {}
        elif not type(data["options"]) is dict:
            return json.dumps({"code": 803, "data": f"请求中 options 字段必须为字典。"})
        try:
            # 补充缺失的默认参数
            opt = data["options"]
            default = get_ocr_options()
            for key in default:
                if key not in opt:
                    opt[key] = default[key]["default"]
            # 检查OCR参数
            check_ocr_options(opt)
        except Exception as e:
            return json.dumps({"code": 804, "data": f"options 解释失败。 {e}"})
        # 同步执行
        resList = MissionOCR.addMissionWait(opt, {"base64": data["base64"]})
        res = resList[0]["result"]
        if opt["data.format"] == "text":  # 转纯文本
            if res["code"] == 100:
                res["data"] = getDataText(res["data"])
        res = json.dumps(res)
        return res


"""
const url = "http://127.0.0.1:1224/api/ocr";
const data = {
    // 必填
    "base64": "iVBORw0KGgoAAAANSUhEUgAAAC4AAAAXCAIAAAD7ruoFAAAACXBIWXMAABnWAAAZ1gEY0crtAAAAEXRFWHRTb2Z0d2FyZQBTbmlwYXN0ZV0Xzt0AAAHjSURBVEiJ7ZYrcsMwEEBXnR7FLuj0BPIJHJOi0DAZ2qSsMCxEgjYrDQqJdALrBJ2ASndRgeNI8ledutOCLrLl1e7T/mRkjIG/IXe/DWBldRTNEoQSpgNURe5puiiaJehrMuJSXSTgbaby0A1WzLrCCQCmyn0FwoN0V06QONWAt1nUxfnjHYA8p65GjhDKxcjedVH6JOejBPwYh21eE0Wzfe0tqIsEkGXcVcpoMH4CRZ+P0lsQp/pWJ4ripf1XFDFe8GHSHlYcSo9Es31t60RdFlN1RUmrma5oTzTVB8ZUaeeYEC9GmL6kNkDw9BANAQYo3xTNdqUkvHq+rYhDKW0Bj3RSEIpmyWyBaZaMTCrCK+tJ5Jsa07fs3E7esE66HzralRLgJKp0/BD6fJRSxvmDsb6joqkcFXGqMVVFFEHDL2gTxwCAaTabnkFUWhDCHTd9iYrGcAL1ZnqIp5Vpiqh7bCfua7FA4qN0INMcN1+cgCzj+UFxtbmvwdZvGIrI41JiqhZBWhhF8WxorkYPpQwJiWYJeA3rXE4hzcwJ+B96F9zCFHC0FcVegghvFul7oeEE8PvHeJqC0w0AUbbFIT8JnEwGbPKcS2OxU3HMTqD0r4wgEIuiKJ7i4MS16+og8/+bPZRPLa+6Ld2DSzcAAAAASUVORK5CYII=",
    "options": {
        "ocr.angle": false,
        "ocr.language": "简体中文",
        "ocr.maxSideLen": 1024,
        "tbpu.parser": "multi_para",
        "data.format": "text",
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
        console.log(data);
    })
    .catch(error => {
        console.error(error);
    });



const url = "http://127.0.0.1:1224/api/ocr/get_options";
fetch(url, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
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
