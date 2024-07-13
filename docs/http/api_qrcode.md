## 目录

### 图片识别

1. [图片OCR：参数查询](api_ocr.md#/api/ocr/get_options)
2. [图片OCR：Base64 识别](api_ocr.md#/api/ocr)

### 文档识别（PDF识别）

- [文档识别流程](api_doc.md#/api/doc)

### 二维码识别

1. [二维码：Base64 识别](#/api/qrcode)
2. [二维码：从文本生成图片](#/api/qrcode/text)

### 命令行

- [命令行接口](argv.md#/argv)

---

<a id="/api/qrcode"></a>

## 1. 二维码：Base64 识别接口

URL：`/api/qrcode`

例：`http://127.0.0.1:1224/api/qrcode`

### 1.1. 请求格式

方法：`POST`

参数：`json` 字典，值为：

- **base64** ： 必填。待识别图像的 Base64 编码字符串，无需 `data:image/png;base64,` 等前缀。
- **options** ：可选。参数字典，可选项为：
    - **preprocessing.median_filter_size** ：中值滤波器的大小。取值范围：1~9的奇数。默认不进行滤波。
    - **preprocessing.sharpness_factor** ：锐度增强因子。取值范围：0.1~10.0。默认不调整锐度。
    - **preprocessing.contrast_factor** ：对比度增强因子。取值范围：0.1~10.0。大于1增强对比度，小于1但大于0减少对比度，1保持原样。默认不调整对比度。
    - **preprocessing.grayscale** ：是否将图像转换为灰度图像。true为转换，false为不转换。默认为false。
    - **preprocessing.threshold** ：二值化阈值，用于灰度图像的二值化处理。取值范围：0~255 整数。只有当 `"preprocessing.grayscale"=true` 时，此参数才生效。默认为false。


参数示例：

```json
{
    "base64": "iVBORw0KGgoAAAAN……",
    "options": {
        "preprocessing.sharpness_factor": 1.0,
        "preprocessing.contrast_factor": 1.0,
        "preprocessing.grayscale": false,
        "preprocessing.threshold": false,
    }
}
```

### 1.2. 响应格式

返回 `json` ，与 OCR 结果的格式非常相似。

| 字段      | 类型   | 描述                                               |
| --------- | ------ | -------------------------------------------------- |
| code      | int    | 任务状态码。`100`为成功，`101`为无文本，其余为失败 |
| data      | list   | 识别结果，格式见下                                 |
| time      | double | 识别耗时（秒）                                     |
| timestamp | double | 任务开始时间戳（秒）                               |

#### `data` 格式

图片中无文本（`code==101`），或识别失败（`code!=100 and code!=101`）时：

- `["data"]` 为string，内容为错误原因。例： `{"code": 204, "data": "【Error】zxingcpp 二维码解析失败。\n[Error] zxingcpp read_bar……"}`

识别成功（`code==100`）时：

- `["data"]` 为list，记录图片中每个二维码的结果（一张图片可能含多个码）。每项结果的子元素为：

| 参数名      | 类型   | 描述                                                |
| ----------- | ------ | --------------------------------------------------- |
| text        | string | 二维码文本。                                        |
| format      | string | 二维码格式，如 `"QRCode"` 等，具体见下。            |
| box         | list   | 文本框顺时针四个角的xy坐标：`[左上,右上,右下,左下]` |
| orientation | int    | 二维码方向。0为正上。                               |
| score       | int    | 为了与OCR格式兼容而设，永远为1，无意义。            |

<a id="qrcode_format"></a>

##### 二维码格式 format：

`"Aztec","Codabar","Code128","Code39","Code93","DataBar","DataBarExpanded","DataMatrix","EAN13","EAN8","ITF","LinearCodes","MatrixCodes","MaxiCode","MicroQRCode","PDF417","QRCode","UPCA","UPCE"`

结果示例：
```json
{
    "code": 100,
    "data": [ {
        "orientation": 0,
        "box": [[4,4],[25,4],[25,25],[4,25]],
        "score": 1,
        "format": "QRCode",
        "text": "abc"
    } ],
    "time": 0,
    "timestamp": 1711521012.625574
}
```

### 1.3. 调用接口 示例代码

<details>
<summary>JavaScript 示例：（点击展开）</summary>

```javascript
const url = "http://127.0.0.1:1224/api/qrcode";
const base64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAAdAB0BAREA/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/9oACAEBAAA/APU/GfjM+EjAzW9o0DW8txNPdXEkSxKkkMYAEcUjMS069hjBrn3+K0yi3B0/RozO52y3OtG3gaPy7WRWV5IVJO27DFSoIEbYycCrF18Sb2z1a20u70rTbO8uLiKzigutRl3NcNDBIyAxW7rhTcIu4sAcE8Cu00LU/wC2/D2mat5Pk/brSK58rdu2b0Dbc4GcZxnAri/iSdPGs6AuqySW+nzpcW11dg27xwIzQspkimikDIZUiG/5QhK5PzCuPI1qz8ISalajUtNu1czLGsxnt7tHhhhiijNmkSF22W8aFeFWZ2RjIjeVXvrq0t/EWmaTpq3d9rTXFpCqpa2iRW92sCJOUP2WZYjEsNszrG7Bd/GNhr2zQtP/ALI8PaZpuMfY7SK3x5nmY2IF+9tXd067Vz6DpXH/ABK1LVrN7SLTIr6622k159isYYnknkjuLVUI8yGXGzzWfhc5UHPFeeSyav4dtI9R8O+Ho5dYS4WNrSK1EV2sb29ncFJY7aOPzIkkYhjhSGaME7WdHy72y8NWthbfDxrrfDDdpdXH2eVvtIu/IcStcOUaCGFMqGKNKUELZDEsU+g/DUcMXhXSI7cRrAllCsYjIKhQgxgh3BGP9t/95upk1PQtH1vyv7W0qxv/ACc+X9rt0l2ZxnG4HGcDp6Co7Xw1oNiipaaJptuiPvVYbVEAbcjZGB13RxnPqin+EYksdC0fTIo4rDSrG0jjlM6JBbpGFkKlC4AHDFSVz1wcdKuQQQ2tvFb28UcMESBI441CqigYAAHAAHGK/9k="
const data = { "base64": base64 };

fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if(data.code === 100) {
            console.log("QRCode count:", data.data.length);
            for (let d of data.data) {
                console.log("    text: ", d.text);
                console.log("    format: ", d.format);
                console.log("    orientation: ", d.orientation);
                console.log("    ====");
            }
        }
        else {
            console.log("Error! Code", data.code, " Msg: ", data.data);
        }
    })
    .catch(error => { console.error(error); });
```

</details>

<a id="/api/qrcode/text"></a>

---

## 2. 二维码：从文本生成图片

传入文本，根据文本生成二维码图片，返回图片base64。

URL：`/api/qrcode` （与二维码识别接口一致，只是参数不同）

例：`http://127.0.0.1:1224/api/qrcode`

### 2.1. 请求格式

方法：`POST`

参数：`json` 字典，值为：

- **text** ： 必填。要写入二维码的文本。
- **options** ：可选。参数字典，可选项为：
    - **format** ：二维码码格式，可选值 [见上文](#qrcode_format)。默认为 `"QRCode"` 。
    - **w** ：生成图像宽度，整数。默认 `0` 为自动设为最小宽度。
    - **h** ：生成图像高度，整数。默认 `0` 为自动设为最小高度。
    - **quiet_zone** ：二维码四周的空白边缘宽度，整数。默认 `-1` 为自动调节。
    - **ec_level** ：纠错等级，整数。默认 `-1` 。可选值： `-1`:自动, `1`:7%,`0`:15%,`3`:25%, `2`:30%。仅在这些格式下生效：`Aztec`、`PDF417`、`QRCode` 。

参数示例：

```json
{
    "text": "要写入二维码的文本",
    "options": {
        "format": "QRCode",
        "w": 0,
        "h": 0,
        "quiet_zone": -1,
        "ec_level": -1,
    }
}
```


### 2.2. 响应格式

`json`

| 字段名 | 类型   | 描述                            |
| ------ | ------ | ------------------------------- |
| code   | int    | 任务状态。`100`成功，其余为失败 |
| data   | string | 生成结果，格式见下              |

- 生成图片成功（`code==100`）时：`"data"` 为图片的base64字符串，图片编码为`jpeg`。
- 生成图片失败（`code!=100`）时：`"data"` 为错误信息字符串。

### 2.3. 调用接口 示例代码

<details>
<summary>JavaScript 示例：（点击展开）</summary>

```javascript
const url = "http://127.0.0.1:1224/api/qrcode";
const data = {
    "text": "test abc 123 !!!",
    // "options": {
    //     "format": "QRCode",
    //     "w": 0,
    //     "h": 0,
    //     "quiet_zone": -1,
    //     "ec_level": -1,
    // }
};
fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if(data.code === 100) {
            console.log("Image base64: \n", data.data);
        }
        else {
            console.log("Error! Code", data.code, " Msg: ", data.data);
        }
    })
    .catch(error => { console.error(error); });
```

</details>