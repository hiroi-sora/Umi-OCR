## 参与本地化翻译（译者）

前往 Weblate 在线翻译平台，注册账户，或用Github账户登录：

https://hosted.weblate.org/engage/umi-ocr/

您可以补充、订正现有语言的翻译，或创建新的语言。

## 维护本地化文件（开发者）

### 从源代码生成或更新翻译文件.ts

1. 运行 `lupdate_all.py`
2. 提交更改，等待 Weblate 平台更新

### 从翻译文件.ts 生成二进制翻译包.qm 并载入软件

1. 运行 `lrelease_all.py`
2. 在 `/release` 目录下，找到所有 .qm 后缀的文件，剪贴到 `Umi-OCR/UmiOCR-data/i18n`

## 翻译插件界面

Umi-OCR 中的插件（如引擎组件）使用另一套轻量翻译机制。

简单而言：
1. 打开 [插件仓库](https://github.com/hiroi-sora/Umi-OCR_plugins) ，找到某个插件对应的目录。
2. 目录下往往有 `i18n.csv` 这个文件。用Excel或WPS打开它。如果打开乱码，网上有很多解决方法。
3. 在Excel中编辑表格。
4. 保存回csv文件。
5. 确保 `i18n.csv` 存储为 `utf-8` 编码。可以用VsCode打开该文件并转换编码。
6. 向插件仓库提交PR。