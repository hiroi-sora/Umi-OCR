- 命令行手册： [README_CLI.md](README_CLI.md)
- HTTP接口手册： [README_HTTP.md](README_HTTP.md)

# HTTP接口手册

#### 基础说明

![Umi-OCR-全局页-服务.png](https://tupian.li/images/2023/10/25/653907e9bac06.png)

如上图，必须允许HTTP服务才能使用HTTP接口（默认开启）。如果需要允许被局域网访问，请将主机切换到`任何可用地址`。

在全局设置页中勾选`高级`才会显示。

> 由于目前的一些缺陷，如果Umi-OCR关闭时仍有用户未断开HTTP接口连接，可能导致Umi-OCR关闭不完全（UI面板和主线程结束了，但负责网络的子线程未被关闭）。这时只能等待所有用户关闭连接，或者进任务管理器删掉Umi-OCR的进程。

> 由于目前的一些缺陷，对并发支持较差。


### Base64 接口

传入一个base64编码的图片，进行识别。

URL：`/api/ocr`

例：（实际端口请在全局设置中查看）
```
http://127.0.0.1:1224/api/ocr
```

#### 请求

方法：`POST`

参数：`json`

> 注：所有参数均为必填！暂时不支持默认参数。

| 参数名  | 类型   | 描述                                     |
| ------- | ------ | ---------------------------------------- |
| base64  | string | 待识别图像的 Base64 编码字符串，无需前缀 |
| options | object | 配置选项对象                             |

`base64`无需`data:image/png;base64,`等前缀，直接放正文。

`options` 的参数：

Paddle引擎插件：

| 参数名         | 类型    | 描述                                      |
| -------------- | ------- | ----------------------------------------- |
| language       | string  | 识别语言，具体见下                        |
| cls            | boolean | 是否进行图像旋转校正。`true/false`        |
| limit_side_len | int     | 图像压缩边长。允许 `960/2880/4320/999999` |

Paddle可选语言：(填写下列字符串)
```
models/config_chinese.txt
models/config_en.txt
models/config_chinese_cht(v2).txt
models/config_japan.txt
models/config_korean.txt
models/config_cyrillic.txt
```

Rapid引擎插件：

| 参数名     | 类型    | 描述                                       |
| ---------- | ------- | ------------------------------------------ |
| language   | string  | 识别语言，具体见下                         |
| angle      | boolean | 是否进行图像旋转校正。`true/false`         |
| maxSideLen | int     | 图像压缩边长。允许 `1024/2048/4096/999999` |

Rapid可选语言：(填写下列字符串)
```
简体中文(V4)
简体中文(V3)
English
繁體中文
日本語
한국어
Русский
```

#### 响应

`json`

| 字段名    | 类型        | 描述                                              |
| --------- | ----------- | ------------------------------------------------- |
| code      | int         | 任务状态。`100`为成功，`101`为无文本，其余为失败  |
| data      | list/string | 识别结果。`code==100`时为object，其余情况为string |
| time      | double      | 识别耗时（秒）                                    |
| timestamp | double      | 任务开始时间戳（秒）                              |

#### `data` 参数

识别成功（`code==100`）时为列表list，列表中每项元素的组成如下。
图片中无文本（`code==101`），或识别失败（`code>101`）时为string，内容为错误原因。

| 参数名 | 类型   | 描述               |
| ------ | ------ | ------------------ |
| text   | string | 文本               |
| score  | double | 置信度 (0~1)       |
| box    | list   | 文本框四个角的坐标 |

`box`的格式：从左上角开始，顺时针。

`[左上角,右上角,右下角,左下角]`

每个角为 `[x, y]`

例：
```json
"data": {
    "text": "识别文本",
    "score": 0.99800001,
    "box": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
}
```

### Base64 接口示例

JavaScript 示例：

```javascript
const url = 'http://127.0.0.1:1224/api/ocr';
const data = {
    base64: 'iVBORw0KGgoAAAANSUhEUgAAAC4AAAAXCAIAAAD7ruoFAAAACXBIWXMAABnWAAAZ1gEY0crtAAAAEXRFWHRTb2Z0d2FyZQBTbmlwYXN0ZV0Xzt0AAAHjSURBVEiJ7ZYrcsMwEEBXnR7FLuj0BPIJHJOi0DAZ2qSsMCxEgjYrDQqJdALrBJ2ASndRgeNI8ledutOCLrLl1e7T/mRkjIG/IXe/DWBldRTNEoQSpgNURe5puiiaJehrMuJSXSTgbaby0A1WzLrCCQCmyn0FwoN0V06QONWAt1nUxfnjHYA8p65GjhDKxcjedVH6JOejBPwYh21eE0Wzfe0tqIsEkGXcVcpoMH4CRZ+P0lsQp/pWJ4ripf1XFDFe8GHSHlYcSo9Es31t60RdFlN1RUmrma5oTzTVB8ZUaeeYEC9GmL6kNkDw9BANAQYo3xTNdqUkvHq+rYhDKW0Bj3RSEIpmyWyBaZaMTCrCK+tJ5Jsa07fs3E7esE66HzralRLgJKp0/BD6fJRSxvmDsb6joqkcFXGqMVVFFEHDL2gTxwCAaTabnkFUWhDCHTd9iYrGcAL1ZnqIp5Vpiqh7bCfua7FA4qN0INMcN1+cgCzj+UFxtbmvwdZvGIrI41JiqhZBWhhF8WxorkYPpQwJiWYJeA3rXE4hzcwJ+B96F9zCFHC0FcVegghvFul7oeEE8PvHeJqC0w0AUbbFIT8JnEwGbPKcS2OxU3HMTqD0r4wgEIuiKJ7i4MS16+og8/+bPZRPLa+6Ld2DSzcAAAAASUVORK5CYII=',
    // Paddle引擎插件格式
    options: {
        cls: false,
        language: "models/config_chinese.txt",
        limit_side_len: 960
    }
    // Rapid引擎插件格式
    // options: {
    //     angle: false,
    //     language: "简体中文(V4)",
    //     maxSideLen: 1024
    // }
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
```

Python 示例：

```python
import requests
import json

url = "http://127.0.0.1:1224/api/ocr"
data = {
    "base64": "iVBORw0KGgoAAAANSUhEUgAAAC4AAAAXCAIAAAD7ruoFAAAACXBIWXMAABnWAAAZ1gEY0crtAAAAEXRFWHRTb2Z0d2FyZQBTbmlwYXN0ZV0Xzt0AAAHjSURBVEiJ7ZYrcsMwEEBXnR7FLuj0BPIJHJOi0DAZ2qSsMCxEgjYrDQqJdALrBJ2ASndRgeNI8ledutOCLrLl1e7T/mRkjIG/IXe/DWBldRTNEoQSpgNURe5puiiaJehrMuJSXSTgbaby0A1WzLrCCQCmyn0FwoN0V06QONWAt1nUxfnjHYA8p65GjhDKxcjedVH6JOejBPwYh21eE0Wzfe0tqIsEkGXcVcpoMH4CRZ+P0lsQp/pWJ4ripf1XFDFe8GHSHlYcSo9Es31t60RdFlN1RUmrma5oTzTVB8ZUaeeYEC9GmL6kNkDw9BANAQYo3xTNdqUkvHq+rYhDKW0Bj3RSEIpmyWyBaZaMTCrCK+tJ5Jsa07fs3E7esE66HzralRLgJKp0/BD6fJRSxvmDsb6joqkcFXGqMVVFFEHDL2gTxwCAaTabnkFUWhDCHTd9iYrGcAL1ZnqIp5Vpiqh7bCfua7FA4qN0INMcN1+cgCzj+UFxtbmvwdZvGIrI41JiqhZBWhhF8WxorkYPpQwJiWYJeA3rXE4hzcwJ+B96F9zCFHC0FcVegghvFul7oeEE8PvHeJqC0w0AUbbFIT8JnEwGbPKcS2OxU3HMTqD0r4wgEIuiKJ7i4MS16+og8/+bPZRPLa+6Ld2DSzcAAAAASUVORK5CYII=",
    # Paddle引擎插件格式
    "options": {
        "cls": False,
        "language": "models/config_chinese.txt",
        "limit_side_len": 960,
    },
    # Rapid引擎插件格式
    # "options": {
    #     "angle": False,
    #     "language": "简体中文(V4)",
    #     "maxSideLen": 1024,
    # },
}
headers = {"Content-Type": "application/json"}
data_str = json.dumps(data)
response = requests.post(url, data=data_str, headers=headers)
if response.status_code == 200:
    res_dict = json.loads(response.text)
    print("返回值字典\n", res_dict)
```


### 获取可用配置 接口

获取当前是什么引擎，及需要提供哪些options参数。

URL：`/api/ocr/get_options`

例：（实际端口请在全局设置中查看）
```
http://127.0.0.1:1224/api/ocr/get_options
```

#### 请求

方法：`GET`

#### 响应

`json`

| 参数名 | 类型   | 描述                |
| ------ | ------ | ------------------- |
| title  | string | 引擎名称            |
| type   | string | 总是`group`，无意义 |
| 其余   | object | 描述一个配置项。    |

以Paddle为例：

```
{
    "title": "文字识别（PaddleOCR）",
    "type": "group",
    "language": {
        "title": "语言/模型库",
        "optionsList": [
            ["models/config_chinese.txt","简体中文"],
            ["models/config_en.txt","English"],
            ["models/config_chinese_cht(v2).txt","繁體中文(V2)"],
            ["models/config_chinese_cht.txt","繁體中文(V3)"],
            ["models/config_japan.txt","日本語"],
            ["models/config_korean.txt","한국어"],
            ["models/config_cyrillic.txt","Русский"]
        ]
    },
    "cls": {
        "title": "纠正文本方向",
        "default": false,
        "toolTip": "启用方向分类，识别倾斜或倒置的文本。可能降低识别速度。"
    },
    "limit_side_len": {
        "title": "限制图像边长",
        "optionsList": [
            [960,"960 （默认）"],
            [2880,"2880"],
            [4320,"4320"],
            [999999,"无限制"]
        ],
        "toolTip": "将边长大于该值的图片进行压缩，可以提高识别速度。可能降低识别精度。",
        "advanced": true
    }
}
```

可以看到，当前引擎插件的名称为`文字识别（PaddleOCR）`，拥有3个配置参数：`language`、`cls`、`limit_side_len`。  
其中`cls`是布尔值，`language`和`limit_side_len`是枚举。它们对应到UI面板中的开关和下拉栏。  
对于枚举的`optionsList`，元素的第1位是key，第2位是显示文本。当使用HTTP接口时，应该传入key值。


### 命令行 接口

此接口用于命令行参数的跨进程传输，一般由程序内部自动调用。开发者也可手动调用。

由于此接口较敏感（如允许访问本机图片、关闭软件），故只允许本地环回 `127.0.0.1` 调用。局域网无法访问此接口。

URL：`/argv`

例：
```
http://127.0.0.1:1224/argv
```

#### 请求

方法：`POST`

参数：`json` `list`

传入一个列表，列表中记录命令行参数。

- 如：命令行调用 `Umi-OCR.exe --path "D:/xxx.png"`
- 等价于向argv接口发送： `["--path", "D:/xxx.png"]`

具体命令行规则请见 [README_CLI.md](README_CLI.md) 。