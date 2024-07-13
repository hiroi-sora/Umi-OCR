[Translate to English](https://github-com.translate.goog/hiroi-sora/Umi-OCR/blob/main/docs/http/README.md?_x_tr_sl=zh-CN&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp)

- [命令行手册](../README_CLI.md)
- HTTP接口手册

# HTTP接口手册

（本文档仅适用于 Umi-OCR 最新版本。旧版本请查看 [Github备份分支](https://github.com/hiroi-sora/Umi-OCR/branches) 中对应版本的文档。）

#### 基础说明

![Umi-OCR-全局页-服务.png](https://tupian.li/images/2023/10/25/653907e9bac06.png)

如上图，必须允许HTTP服务才能使用HTTP接口（默认开启）。如果需要允许被局域网访问，请将主机切换到**任何可用地址**。

在全局设置页中勾选**高级**才会显示。

##### 注意事项：

1. 关闭 Umi-OCR 软件时，如果仍有用户未断开HTTP接口连接，可能导致Umi-OCR关闭不完全（UI线程结束了，但负责网络的子线程未被关闭）。这时只能等待所有用户关闭连接，或者进任务管理器强制结束进程。  
2. 由于后端组件的性能限制，对并发支持较差，尽量不要并发调用。
3. 由于后端组件的性能限制，在长时间、大批量、连续调用时，有小几率出现 `Error: connect ECONNREFUSED` 之类的HTTP报错。此时重新发起请求即可。只要后台工作线程没有崩，这些小问题不会持续影响调用。

---

## 目录

### 图片识别

1. [图片OCR：参数查询](api_ocr.md#/api/ocr/get_options)
2. [图片OCR：Base64 识别](api_ocr.md#/api/ocr)

### 文档识别（PDF识别）

- [文档识别流程](api_doc.md#/api/doc)

### 二维码识别

1. [二维码：Base64 识别](api_qrcode.md#/api/qrcode)
2. [二维码：从文本生成图片](api_qrcode.md#/api/qrcode/text)

### 命令行

- [命令行接口](argv.md#/argv)
