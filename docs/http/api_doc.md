## 目录

### 图片识别

1. [图片OCR：参数查询](api_ocr.md#/api/ocr/get_options)
2. [图片OCR：Base64 识别](api_ocr.md#/api/ocr)

### 文档识别（PDF识别）

- [文档识别流程](#/api/doc)

### 二维码识别

1. [二维码：Base64 识别](api_qrcode.md#/api/qrcode)
2. [二维码：从文本生成图片](api_qrcode.md#/api/qrcode/text)

### 命令行

- [命令行接口](argv.md#/argv)

---

> [!TIP]
> 必须使用最新的 Umi-OCR [v2.1.3（测试版）](https://github.com/hiroi-sora/Umi-OCR/releases) ，才具有文档识别功能。

<a id="/api/doc"></a>

---

## 文档识别流程

调用文档识别的流程为：

0. 开发之前，先查询确认一下参数。👉 [说明](#/api/doc/get_options)
1. 上传要识别的文件，获取任务ID。👉 [说明](#/api/doc/upload)
2. 通过ID，轮询任务状态，直到OCR任务结束。👉 [说明](#/api/doc/result)
3. 生成目标文件（如双层可搜索PDF），获取下载链接。👉 [说明](#/api/doc/download)
4. 下载目标文件。👉 [说明](#/api/doc/download/id)
5. 清理任务。👉 [说明](#/api/doc/clear)

建议参考下述示例代码：

Python - [api_doc_demo.py](api_doc_demo.py)
Web - [api_doc_demo.html](api_doc_demo.html)

<a id="/api/doc/get_options"></a>

---

## 0. 文档上传：参数查询

> 在不同的情况下（比如使用不同的OCR引擎插件），**文档上传接口**可以传入不同的参数。   
> 通过【参数查询接口】，可以获取所有参数的定义、默认值、可选值等信息。   
> 你可以调用查询接口来确认信息，也可以通过查询接口返回的字典来自动化生成前端UI。   


URL：`/api/doc/get_options`

例：`http://127.0.0.1:1224/api/doc/get_options`

### 0.1. 请求格式

方法：`GET`

### 0.2. 响应格式

返回 `json` 字典，记录**文档上传接口**的参数定义。

以PaddleOCR引擎插件为例，返回值为：

<details>
<summary>展开</summary>

```json
{
    "ocr.language": {
        "title": "语言/模型库",
        "optionsList": [
            ["models/config_chinese.txt","简体中文"],
            ["models/config_en.txt","English"],
            ["models/config_chinese_cht(v2).txt","繁體中文"],
            ["models/config_japan.txt","日本語"],
            ["models/config_korean.txt","한국어"],
            ["models/config_cyrillic.txt","Русский"]
        ],
        "type": "enum",
        "default": "models/config_chinese.txt"
    },
    "ocr.cls": {
        "title": "纠正文本方向",
        "default": false,
        "toolTip": "启用方向分类，识别倾斜或倒置的文本。可能降低识别速度。",
        "type": "boolean"
    },
    "ocr.limit_side_len": {
        "title": "限制图像边长",
        "optionsList": [
            [960,"960 （默认）"],
            [2880,"2880"],
            [4320,"4320"],
            [999999,"无限制"]
        ],
        "toolTip": "将边长大于该值的图片进行压缩，可以提高识别速度。可能降低识别精度。",
        "type": "enum",
        "default": 960
    },
    "tbpu.parser": {
        "title": "排版解析方案",
        "toolTip": "按什么方式，解析和排序图片中的文字块",
        "default": "multi_para",
        "optionsList": [
            ["multi_para","多栏-按自然段换行"],
            ["multi_line","多栏-总是换行"],
            ["multi_none","多栏-无换行"],
            ["single_para","单栏-按自然段换行"],
            ["single_line","单栏-总是换行"],
            ["single_none","单栏-无换行"],
            ["single_code","单栏-保留缩进"],
            ["none","不做处理"]
        ],
        "type": "enum"
    },
    "tbpu.ignoreArea": {
        "title": "忽略区域",
        "toolTip": "数组，每一项为[[左上角x,y],[右下角x,y]]。",
        "default": [],
        "type": "var"
    },
    "tbpu.ignoreRangeStart": {
        "title": "忽略区域起始",
        "toolTip": "忽略区域生效的页数范围起始。从1开始。",
        "default": 1,
        "type": "number",
        "isInt": true
    },
    "tbpu.ignoreRangeEnd": {
        "title": "忽略区域结束",
        "toolTip": "忽略区域生效的页数范围结束。可以用负数表示倒数第X页。",
        "default": -1,
        "type": "number",
        "isInt": true
    },
    "pageRangeStart": {
        "title": "OCR页数起始",
        "toolTip": "OCR的页数范围起始。从1开始。",
        "default": 1,
        "type": "number",
        "isInt": true
    },
    "pageRangeEnd": {
        "title": "OCR页数结束",
        "toolTip": "OCR的页数范围结束。可以用负数表示倒数第X页。",
        "default": -1,
        "type": "number",
        "isInt": true
    },
    "pageList": {
        "title": "OCR页数列表",
        "toolTip": "数组，可指定单个或多个页数。例：[1,2,5]表示对第1、2、5页进行OCR。如果与页数范围同时填写，则 pageList 优先。",
        "default": [],
        "type": "var"
    },
    "password": {
        "title": "密码",
        "toolTip": "如果文档已加密，则填写文档密码。",
        "default": "",
        "type": "text"
    },
    "doc.extractionMode": {
        "title": "内容提取模式",
        "toolTip": "若一页文档既存在图片又存在文本，如何进行处理。",
        "default": "mixed",
        "optionsList": [
            ["mixed","混合OCR/原文本"],
            ["fullPage","整页强制OCR"],
            ["imageOnly","仅OCR图片"],
            ["textOnly","仅拷贝原有文本"]
        ],
        "type": "enum"
    }
}
```

上述返回值示例中，拥有12个根元素，表示12个参数。

</details></br>

返回值中，每个参数有这些属性：

- `title`：参数名称。
- `toolTip`：参数说明。
- `default`：默认值。
- `type`：参数值的类型，具体如下：
  - `enum`：枚举。参数值必须为 `optionsList` 中某一项的 `[0]` 。
  - `boolean`：布尔。参数值必须为 `true/false` 。
  - `text`：字符串。
  - `number`：数字。如何属性`isInt==true`，那么必须为整数。
  - `var`：特殊类型，具体见 `toolTip` 的说明。

部分参数的具体说明，可参考： [图片OCR参数查询](api_ocr.md#/api/ocr/options_info) 。


对于上述返回值示例，可以组装出这样的参数字典：

<details>
<summary>展开</summary>

```json
{
    "ocr.language": "models/config_chinese.txt",
    "ocr.cls": true,
    "ocr.limit_side_len": 4320,
    "tbpu.parser": "multi_none",
    "pageRangeStart": 1,
    "pageRangeEnd": 10,
    "doc.extractionMode": "fullPage",
}
```

</details></br>

### 0.3. 参数查询 示例代码

<details>
<summary>JavaScript 示例：（点击展开）</summary>

```javascript
const url = "http://127.0.0.1:1224/api/doc/get_options";
fetch(url, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
    })
    .then(response => response.json())
    .then(data => { console.log(data); })
    .catch(error => { console.error(error); });
```

</details>

<details>
<summary>Python 示例：（点击展开）</summary>

```python
import json, requests

response = requests.get("http://127.0.0.1:1224/api/doc/get_options")
res_dict = json.loads(response.text)
print(json.dumps(res_dict, indent=4, ensure_ascii=False))
```

</details></br>

手动调用：
- 确保 Umi-OCR 已在运行。
- 浏览器访问 http://127.0.0.1:1224/api/doc/get_options
- 复制全部内容，粘贴到在线json格式化工具里转换为可读文本。

<a id="/api/doc/upload"></a>

---

## 1. 文档识别：上传

上传一个文档文件，启动识别任务，返回任务ID。

URL：`/api/doc/upload`

例：`http://127.0.0.1:1224/api/doc/upload`

### 1.1. 请求格式

方法：`POST`

参数：表单 `formData` ，值为：

- **file** ：必填。要上传的文件。
- **json** ：可选。参数字典（json字符串），详情见查询接口。



<details>
<summary>JavaScript 示例：（点击展开）</summary>

```JavaScript
    const fileInput = document.getElementById('file_path').files[0];
    const missionOptions = {
        "doc.extractionMode": "mixed",
    };

    const formData = new FormData();
    formData.append('file', fileInput);
    formData.append('json', JSON.stringify(missionOptions));

    let response = await fetch("http://127.0.0.1:1224/api/doc/upload", {
        method: 'POST',
        body: formData
    });
```

</details>

### 1.2. 响应格式

返回 `json` 字典，内容为：

- **code** ：（int）任务状态码。`100`为上传成功，其余为失败。
- **data** ：（string）如果上传成功，则为任务ID。失败，则为失败原因。

<a id="/api/doc/result"></a>

---

## 2. 文档识别：查询任务状态

传入任务ID，返回任务执行状态和识别文本。

URL：`/api/doc/result`

例：`http://127.0.0.1:1224/api/doc/result`

### 2.1. 请求格式

方法：`POST`

参数： `json` 字典，键值为：

- **id** ：必填，字符串。文件上传接口执行成功后，返回的任务ID。
- **is_data** ：布尔值。非必填。
  - `true` ：返回值中包含识别结果。
  - `false` （默认）：返回值中不包含识别结果，只有简略的任务状态信息。
- **is_unread** ：布尔值。非必填。
  - `true` （默认）：返回未读过的识别结果条目。
  - `false` ：返回全部识别结果条目。
- **format** ：字符串。非必填。
  - `"dict"` （默认）：以字典形式返回详细的识别结果。
  - `"text"` ：以字符串形式返回识别结果文本。

### 2.2. 响应格式

返回 `json` 字典，内容为：

- **code** ：（int）任务状态码。`100`为查询成功，其余为失败。
- **data** ：（string）如果查询失败，则为失败原因。如果查询成功且`is_data=true`，则为识别内容。如果查询成功且`is_data=false`，则为空数组。

以下内容只有 `code==100` 时才存在：

- **processed_count** ：（int）已经识别完的页数。
- **pages_count** ：（int）总页数。
- **is_done** ：（boolean）`true`表示任务已结束（state可能为`success`或`failure`），`false`表示任务仍在进行中。
- **state** ：（string）任务状态。值的含义：`waiting` 任务排队中，`running` 任务进行中，`success` 任务成功，`failure` 任务失败。
- **message** ：（string）只有 `state=="failure"` 才存在此项，表示任务失败的原因。注意，就算任务失败，仍可能通过 `data` 获取已完成的部分任务结果。

<a id="/api/doc/download"></a>

---

## 3. 文档识别：获取下载链接

必须在任务成功结束后才能调用，即第2步查询得知 `is_done==true && state=="success"` 。

传入任务ID和目标文件类型，生成目标文件，返回目标文件的下载链接。

URL：`/api/doc/download`

例：`http://127.0.0.1:1224/api/doc/download`

### 3.1. 请求格式

方法：`POST`

参数： `json` 字典，键值为：

- **id** ：必填，字符串。任务ID。
- **file_types** ：数组，每一项为字符串。只填写一个值时，返回单个文件的下载链接。填写多个值时，返回单个zip压缩包下载链接，其中打包了多个文件。
    - `"pdfLayered"` （默认）：双层可搜索PDF。
    - `"pdfOneLayer"` ：单层纯文本PDF。
    - `"txt"` ：带页数等信息的txt文件。
    - `"txtPlain"` ：只含识别文本的txt文件。
    - `"jsonl"` ：与 `result` 接口， `format="dict"` 的格式类似。每行为一个json对象。
    - `"csv"` ：表格，每行为一页的识别文本。
- **ingore_blank** ：布尔值。是否忽略空页（没有文字的页数）。
  - `true` （默认）：如 txt、csv 等文件中，会跳过空页。
  - `false` ：不跳过空页，文件中空页的内容记为空字符串。

### 3.2. 响应格式

返回 `json` 字典，内容为：

- **code** ：（int）任务状态码。`100`为成功生成目标文件，其余为无法生成目标文件。
- **data** ：（string）如果成功，则为下载链接。如果失败，则为失败原因。
- **name** ：（string）只有成功时才存在此项。下载链接对应的文件名。

<a id="/api/doc/download/id"></a>

---

## 4. 文档识别：下载链接

第3步获取的下载链接，可通过get请求下载，或者直接用浏览器打开下载。

链接中类似id的部分， **不是** 任务ID。 **不能** 通过任务ID拼接出下载链接。

<a id="/api/doc/clear"></a>

---

## 5. 文档识别：任务清理

在URL中拼接任务ID，清理对应的任务。

URL：`/api/doc/clear/<id>`

例：`http://127.0.0.1:1224/api/doc/clear/cbe2f874-84a9-48b4-a6c0-9157245f7bae`

### 5.1. 请求格式

方法：`GET`

### 5.2. 响应格式

返回 `json` 字典，内容为：

- **code** ：（int）状态码。`100`为清理成功，其余为清理失败（或者不存在对应任务）。
- **data** ：（string）原因。

### 5.3. 关于清理的说明

清理：指强制终止任务（如果任务进行中），并删除此任务对应的临时文件。

一个任务被清理后，无法再获取任务状态、访问下载链接。

建议调用者在每次完成任务后手动清理任务，以便及时释放服务器资源。如果不手动清理，任务会在24小时后自动清理。

- 如果任务上传后一直在进行，那么最长持续运行24小时。
- 如果任务已完成，那么从完成的时候开始算，最长保留24小时。

如果 Umi-OCR 被意外关闭，那么重新启动时自动清理上次遗留的所有任务。
