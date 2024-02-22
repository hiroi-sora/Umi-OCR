import json
import os

import unicodedata

from .bottle import request
from ..mission.mission_doc import MissionDOC
from ..mission.mission_ocr import MissionOCR
from ..utils.utils import initConfigDict, DocSuf


# 获取ocr配置字典
def _get_ocr_options():
    opts = {}
    # OCR 的参数
    ocr_opts = MissionOCR.getLocalOptions()
    ocr_opts = initConfigDict(ocr_opts)
    for key in ocr_opts:
        opts[f"ocr.{key}"] = ocr_opts[key]
    # 排版解析的参数
    opts[f"tbpu.parser"] = {  # TODO: 新排版解析的HTTP接口数据
        "title": "排版解析",
        "default": "MergeLine",
        "optionsList": [
            ["MergeLine", "单行"],
            ["MergePara", "多行-自然段"],
            ["MergeParaCode", "多行-代码段"],
            ["MergeLineVrl", "竖排-从右到左"],
            ["MergeLineVlr", "竖排-从左到右"],
            ["None", "不做处理"],
        ],
    }
    return opts


# 路由函数
def init(UmiWeb):
    @UmiWeb.route("/api/ocr/get_options")
    def _get_options_json():
        opts = _get_ocr_options()
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
        # 补充缺失的默认参数
        try:
            opt = data["options"]
            default = _get_ocr_options()
            for key in default:
                if key not in opt:
                    opt[key] = default[key]["default"]
        except Exception as e:
            return json.dumps({"code": 804, "data": f"options 解释失败。 {e}"})
        # 同步执行
        resList = MissionOCR.addMissionWait(opt, {"base64": data["base64"]})
        res = resList[0]["result"]
        res = json.dumps(res)
        return res

    # 设置文件保存目录（请替换为您自己的路径）
    UPLOAD_FOLDER = '/var/www/uploads'

    # 配置上传目录
    UmiWeb.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # 检查文件扩展名是否被允许
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in DocSuf

    def secure_filename(filename):
        r"""Pass it a filename and it will return a secure version of it.  This
        filename can then safely be used for any operation, for example as a target
        for storing the file.  The filename returned is an ASCII only string for
        maximum portability.

        On windows systems the function also makes sure that the file is not named
        after one of the special device files.

        >>> secure_filename("My cool movie.mov")
        'My_cool_movie.mov'
        >>> secure_filename("../../../etc/passwd")
        'etc_passwd'
        >>> secure_filename(u'i contain cool \xfcml\xe4uts.txt')
        'i_contain_cool_umlauts.txt'

        The function might return an empty filename.  It's your responsibility
        to ensure that the filename is unique and that you abort or
        mitigate the effects of collisions.
        """
        if isinstance(filename, str):
            from warnings import warn
            warn(DeprecationWarning('Using safe_join with bytestrings may lead '
                                    'to unexpected results on certain '
                                    'filesystems.'), stacklevel=2)
            filename = filename.encode('utf-8')
        elif isinstance(filename, bytes):
            pass
        else:
            raise TypeError('filename must be a str or bytes')

        # 给文件名进行 Unicode 正规化，并移除非字母数字字符
        filename = (unicodedata.normalize('NFKD', filename)
                    .encode('ascii', 'ignore').decode('ascii'))

        for sep in os.path.sep, os.path.altsep:
            if sep:
                filename = filename.replace(sep, '_')

        # Windows系统中过滤掉设备文件名称
        if os.name == 'nt' and filename and filename[1:3] == ':\\':
            filename = filename[0] + '_' + filename[2:]

        return filename.translate({ord(c): None for c in '\\/:*?"<>|'})

    @UmiWeb.route("/api/doc", method="POST")
    def _doc():
        try:
            data = request.json
        except Exception as e:
            return json.dumps({"code": 800, "data": f"请求无法解析为json。"})
        if not data:
            return json.dumps({"code": 801, "data": f"请求为空。"})
        if "path" not in data:
            return json.dumps({"code": 802, "data": f"请求中缺少 path 字段。"})
        if "options" not in data:
            data["options"] = {}
        elif not type(data["options"]) is dict:
            return json.dumps({"code": 803, "data": f"请求中 options 字段必须为字典。"})
        # 补充缺失的默认参数
        try:
            opt = data["options"]
            default = _get_ocr_options()
            for key in default:
                if key not in opt:
                    opt[key] = default[key]["default"]
        except Exception as e:
            return json.dumps({"code": 804, "data": f"options 解释失败。 {e}"})

        # 获取文件
        file = request.files['file']
        # 检查文件是否存在且合法
        if file and allowed_file(file.filename):
            # 生成安全文件名并保存文件
            filename = secure_filename(file.filename)
            file_path = os.path.join(UmiWeb.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

        pageRange = [int(data["range_start"]), int(data["range_end"])]
        password = data["password"]
        # 任务信息
        msnInfo = { #TODO
            # "onStart": _onStart,
            # "onReady": _onReady,
            # "onGet": _onGet,
            # "onEnd": _onEnd,
            # "argd": docArgd,
            # # 交给 self._onGet 的参数
            # "get_output": output,
            # "get_tbpu": tbpuList,
        }
        msnID = MissionDOC.addMission(msnInfo, file_path, pageRange,
                                      password=password)
        # TODO 文档OCR后路径在哪里

        # 想要将文件返回前台
        # 设置合适的 HTTP 头部（如Content-Disposition），以便浏览器知道这是一个需要下载的文件
        return send_file( # TODO 需引入flask
            file_path,
            as_attachment=True,  # 强制作为附件下载
            attachment_filename=filename,  # 可选：设置下载时显示的文件名
            mimetype='application/octet-stream'  # 根据实际文件类型设置 MIME 类型
        )


"""
const url = "http://127.0.0.1:1224/api/ocr";
const data = {
    // 必填
    "base64": "iVBORw0KGgoAAAANSUhEUgAAAC4AAAAXCAIAAAD7ruoFAAAACXBIWXMAABnWAAAZ1gEY0crtAAAAEXRFWHRTb2Z0d2FyZQBTbmlwYXN0ZV0Xzt0AAAHjSURBVEiJ7ZYrcsMwEEBXnR7FLuj0BPIJHJOi0DAZ2qSsMCxEgjYrDQqJdALrBJ2ASndRgeNI8ledutOCLrLl1e7T/mRkjIG/IXe/DWBldRTNEoQSpgNURe5puiiaJehrMuJSXSTgbaby0A1WzLrCCQCmyn0FwoN0V06QONWAt1nUxfnjHYA8p65GjhDKxcjedVH6JOejBPwYh21eE0Wzfe0tqIsEkGXcVcpoMH4CRZ+P0lsQp/pWJ4ripf1XFDFe8GHSHlYcSo9Es31t60RdFlN1RUmrma5oTzTVB8ZUaeeYEC9GmL6kNkDw9BANAQYo3xTNdqUkvHq+rYhDKW0Bj3RSEIpmyWyBaZaMTCrCK+tJ5Jsa07fs3E7esE66HzralRLgJKp0/BD6fJRSxvmDsb6joqkcFXGqMVVFFEHDL2gTxwCAaTabnkFUWhDCHTd9iYrGcAL1ZnqIp5Vpiqh7bCfua7FA4qN0INMcN1+cgCzj+UFxtbmvwdZvGIrI41JiqhZBWhhF8WxorkYPpQwJiWYJeA3rXE4hzcwJ+B96F9zCFHC0FcVegghvFul7oeEE8PvHeJqC0w0AUbbFIT8JnEwGbPKcS2OxU3HMTqD0r4wgEIuiKJ7i4MS16+og8/+bPZRPLa+6Ld2DSzcAAAAASUVORK5CYII=",
    "options": {
        "ocr.angle": false,
        "ocr.language": "简体中文",
        "ocr.maxSideLen": 1024,
        "tbpu.parser": "MergeLine",
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
