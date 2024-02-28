<p align="left">
    <span>
        中文
    </span>
    <span> • </span>
    <a href="README_ja.md">
        日本語
    </a>
    <span> • </span>
    <a href="README_en.md">
        English
    </a>
</p>




<p align="center">
  <a href="https://github.com/hiroi-sora/Umi-OCR">
    <img width="200" height="128" src="https://tupian.li/images/2022/10/27/icon---256.png" alt="Umi-OCR">
  </a>
</p>

<h1 align="center">Umi-OCR 文字识别工具</h1>

<p align="center">
  <a href="https://github.com/hiroi-sora/Umi-OCR/releases/latest">
    <img src="https://img.shields.io/github/v/release/hiroi-sora/Umi-OCR?style=flat-square" alt="Umi-OCR">
  </a>
  <a href="License">
    <img src="https://img.shields.io/github/license/hiroi-sora/Umi-OCR?style=flat-square" alt="LICENSE">
  </a>
  <a href="#下载">
    <img src="https://img.shields.io/github/downloads/hiroi-sora/Umi-OCR/total?style=flat-square" alt="forks">
  </a>
  <a href="https://star-history.com/#hiroi-sora/Umi-OCR">
    <img src="https://img.shields.io/github/stars/hiroi-sora/Umi-OCR?style=flat-square" alt="stars">
  </a>
  <a href="https://github.com/hiroi-sora/Umi-OCR/forks">
    <img src="https://img.shields.io/github/forks/hiroi-sora/Umi-OCR?style=flat-square" alt="forks">
  </a>
  <a href="https://hosted.weblate.org/engage/umi-ocr/">
    <img src="https://hosted.weblate.org/widget/umi-ocr/svg-badge.svg" alt="翻译状态">
  </a>
</p>

<div align="center">
  <h3>
    <a href="#说明目录">
      使用说明
    </a>
    <span> • </span>
    <a href="#下载">
      下载地址
    </a>
    <span> • </span>
    <a href="#更新日志">
      更新日志
    </a>
    <span> • </span>
    <a href="https://github.com/hiroi-sora/Umi-OCR/issues">
      提交Bug
    </a>
  </h3>
</div>
<br>

<div align="center">
  <strong>免费，开源，可批量的离线OCR软件</strong><br>
  <sub>适用于 Windows7 x64 及以上</sub>
</div><br>

- **免费**：本项目所有代码开源，完全免费。
- **方便**：解压即用，离线运行，无需网络。
- **高效**：自带高效率的离线OCR引擎，内置多种语言识别库。
- **灵活**：支持命令行、HTTP接口等多种调用方式。
- **功能**：截图OCR / 批量OCR / PDF识别 / 二维码 / 公式识别（[测试中](https://github.com/hiroi-sora/Umi-OCR/issues/254)）

<p align="center"><img src="https://tupian.li/images/2023/11/19/65599097ab5f4.png" alt="1-标题-1.png" style="width: 80%;"></p>

![1-标题-2.png](https://tupian.li/images/2023/11/19/6559909fdeeba.png)

## 目录

- [截图识别](#截图OCR)
  - [段落合并](#段落合并) - 优化不同文字排版
- [批量识别](#批量OCR)
  - [忽略区域](#忽略区域) - 排除截图水印处的文字
- [二维码](#二维码) 支持扫码或生成二维码图片
- [文档识别](#文档识别) 从PDF扫描件中提取文本，或转为双层可搜索PDF
- [全局设置](#全局设置) 添加更多PP-OCR支持的语言模型库！
- [命令行调用](docs/README_CLI.md)
- [HTTP接口](docs/README_HTTP.md)
- [构建项目](#构建项目)

## 使用源码

开发者请务必阅读 [构建项目](#构建项目) 。

## 下载发行版

可选择以下方式下载：

- **GitHub** https://github.com/hiroi-sora/Umi-OCR/releases/latest
- **蓝奏云** https://hiroi-sora.lanzoul.com/s/umi-ocr
- **Source Forge** https://sourceforge.net/projects/umi-ocr

## 开始使用

软件发布包下载为 `.7z` 压缩包或 `.7z.exe` 自解压包。自解压包可在没有安装压缩软件的电脑上，解压文件。

本软件无需安装。解压后，点击 `Umi-OCR.exe` 即可启动程序。

遇到任何问题，请提 [Issue](https://github.com/hiroi-sora/Umi-OCR/issues) ，我会尽可能帮助你。

## 界面语言

Umi-OCR 支持的界面多国语言。在第一次打开软件时，将会按照你的电脑的系统设置，自动切换语言。

如果需要手动切换语言，请参考下图，`全局设置`→`语言/Language` 。

<p align="center"><img src="https://tupian.li/images/2023/11/19/65599c3f9e600.png" alt="1-标题-1.png" style="width: 80%;"></p>

## 标签页

Umi-OCR v2 由一系列灵活好用的**标签页**组成。您可按照自己的喜好，打开需要的标签页。

标签栏左上角可以切换**窗口置顶**。右上角能够**锁定标签页**，以防止日常使用中误触关闭标签页。

### 截图OCR

<p align="center"><img src="https://tupian.li/images/2023/11/19/65599097aba8e.png" alt="2-截图-1.png" style="width: 80%;"></p>

**截图OCR**：打开这一页后，就可以用快捷键唤起截图，识别图中的文字。
- 左侧的图片预览栏，可直接用鼠标划选复制。
- 右侧的识别记录栏，可以编辑文字，允许划选多个记录复制。
- 也支持在别处复制图片，粘贴到Umi-OCR进行识别。

#### 文本后处理

<p align="center"><img src="https://tupian.li/images/2023/11/19/6559909f3e378.png" alt="2-截图-2.png" style="width: 80%;"></p>

关于 **OCR文本后处理 - 排版解析方案**： 可以整理OCR结果的排版和顺序，使文本更适合阅读和使用。预设方案：
- `多栏-按自然段换行`：适合大部分情景，自动识别多栏布局，按自然段规则进行换行。
- `多栏-总是换行`：每段语句都进行换行。
- `多栏-无换行`：强制将所有语句合并到同一行。
- `单栏-按自然段换行`/`总是换行`/`无换行`：与上述类似，不过 不区分多栏布局。
- `单栏-保留缩进`：适用于解析代码截图，保留行首缩进和行中空格。
- `不做处理`：OCR引擎的原始输出，默认每段语句都进行换行。

上述方案，均能自动处理横排和竖排（从右到左）的排版。（竖排文字还需要OCR引擎本身支持）

---

### 批量OCR

<p align="center"><img src="https://tupian.li/images/2023/11/19/655990a2511e0.png" alt="3-批量-1.png" style="width: 80%;"></p>

**批量OCR**：这一页支持批量导入本地图片并识别。
- 识别内容可以保存为 txt / jsonl / md / csv(Excel) 等多种格式。
- 与截图OCR一样，支持`文本后处理`功能，整理OCR文本的排版和顺序。
- 支持 `忽略区域` 。
- 没有数量上限，可一次性导入几百张图片进行任务。
- 支持任务完成后自动关机/待机。

#### 忽略区域

<p align="center"><img src="https://tupian.li/images/2023/11/19/6559911d28be7.png" alt="3-批量-2.png" style="width: 80%;"></p>

关于 **OCR文本后处理 - 忽略区域**： 批量OCR中的一种特殊功能，适用于排除图片中的不想要的文字。
- 在批量识别页的右栏设置中可进入忽略区域编辑器。
- 如上方样例，图片顶部和右下角存在多个水印 / LOGO。如果批量识别这类图片，水印会对识别结果造成干扰。
- 按住右键，绘制多个矩形框。这些区域内的文字将在任务中被忽略。
- 请尽量将矩形框画得大一些，完全包裹住水印所有可能出现的位置。

---

### 文档识别

<p align="center"><img src="https://github.com/hiroi-sora/Umi-OCR/assets/56373419/fc2266ee-b9b7-4079-8b10-6610e6da6cf5" alt="" style="width: 80%;"></p>

仅在 [v2.1.0+](https://github.com/hiroi-sora/Umi-OCR/releases) 支持。

**文档识别**：
- 支持导入 `pdf, xps, epub, mobi, fb2, cbz` 格式的文件。
- 对扫描件进行OCR，或提取原有文本。可输出为 **双层可搜索PDF** 。
- 支持设定 **忽略区域** ，可用于排除页眉页脚的文字。
- 可设置任务完成后 **自动关机/休眠** 。

---

### 二维码

<p align="center"><img src="https://tupian.li/images/2023/11/19/655991268d6b1.png" alt="4-二维码-1.png" style="width: 80%;"></p>

**扫码**：
- 截图/粘贴/拖入本地图片，读取其中的二维码、条形码。
- 支持一图多码。
- 支持19种协议，如下：

`Aztec`,`Codabar`,`Code128`,`Code39`,`Code93`,`DataBar`,`DataBarExpanded`,`DataMatrix`,`EAN13`,`EAN8`,`ITF`,`LinearCodes`,`MatrixCodes`,`MaxiCode`,`MicroQRCode`,`PDF417`,`QRCode`,`UPCA`,`UPCE`

<p align="center"><img src="https://tupian.li/images/2023/11/19/6559911cda737.png" alt="4-二维码-2.png" style="width: 80%;"></p>

**生成码**：
- 输入文本，生成二维码图片。
- 支持19种协议和**纠错等级**等参数。

---

### 全局设置

<p align="center"><img src="https://tupian.li/images/2023/11/19/655991252e780.png" alt="5-全局设置-1.png" style="width: 80%;"></p>

**全局设置**：在这里可以调整软件的全局参数。常用功能如下：
- 一键添加快捷方式或设置开机自启。
- 更改界面**语言**。Umi支持繁中、英语、日语等语言。
- 切换界面**主题**。Umi拥有多个亮/暗主题。
- 调整界面**文字的大小**和**字体**。
- 切换OCR插件。
- **渲染器**：软件界面默认支持显卡加速渲染。如果在你的机器上出现截屏闪烁、UI错位的情况，请调整`界面和外观` → `渲染器` ，尝试切换到不同渲染方案，或关闭硬件加速。

---

## 调用接口：

- 命令行手册： [README_CLI.md](docs/README_CLI.md)
- HTTP接口手册： [README_HTTP.md](docs/README_HTTP.md)

## 协助软件界面翻译

您可以在 Weblate 在线参与翻译工作：

https://hosted.weblate.org/engage/umi-ocr/

## 开发计划

<details>
<summary>已完成的工作</summary>

- 标签页框架。
- OCR API控制器。
- OCR 任务控制器。
- 主题管理器，支持切换浅色/深色主题主题。
- 实现 **批量OCR**。
- 实现 **截图OCR**。
- 快捷键机制。
- 系统托盘菜单。
- 文本块后处理（排版优化）。
- 引擎内存清理。
- 软件界面多国语言。
- 命令行模式。
- Win7兼容。
- Excel（csv）输出格式。
- `Esc`中断截图操作
- 外置主题文件
- 字体切换
- 加载动画
- 忽略区域。
- 二维码识别。
- 批量识别页面的图片预览窗口。
- PDF识别。
- 调用本地图片浏览器打开图片。 [#335](https://github.com/hiroi-sora/Umi-OCR/issues/335)
- 重复上一次截图。 [#357](https://github.com/hiroi-sora/Umi-OCR/issues/357)

</details>

##### 远期计划

<details>
<summary>展开</summary>

这些是预想中的功能，在开发初期已预留好接口，将在远期慢慢实现。

但开发途中受限于实际情况，可能更改功能设计、新增及取消功能。

- 基于GPU的离线OCR。
- 图片翻译
- 离线翻译。
- 插件系统。
- 固定区域识别。
- 识别表格图片，输出为Excel。
- 根据系统的深/浅模式，自动切换主题。
- 历史记录系统。
- 兼容 MacOS / Ubuntu 等平台。

</details>


## 关于项目结构

### 各仓库：

- [主仓库](https://github.com/hiroi-sora/Umi-OCR) 👈
- [插件库](https://github.com/hiroi-sora/Umi-OCR_plugins)
- [Win 运行库](https://github.com/hiroi-sora/Umi-OCR_runtime_windows)

### 工程结构：

`**` 后缀表示本仓库(`主仓库`)包含的内容。

```
Umi-OCR
├─ Umi-OCR.exe
└─ UmiOCR-data
   ├─ main.py **
   ├─ version.py **
   ├─ site-packages
   │  └─ python包
   ├─ runtime
   │  └─ python解释器
   ├─ qt_res **
   │  └─ 项目qt资源，包括图标和qml源码
   ├─ py_src **
   │  └─ 项目python源码
   ├─ plugins
   │  └─ 插件
   └─ i18n **
      └─ 翻译文件
```

支持的离线OCR引擎：

- [PaddleOCR-json](https://github.com/hiroi-sora/PaddleOCR-json)
- [RapidOCR-json](https://github.com/hiroi-sora/RapidOCR-json)

运行环境框架：

- [PyStand](https://github.com/skywind3000/PyStand) 定制版

## 构建项目

### 第零步：（可选）fork本项目

### 第一步：下载代码

请参考 [更新日志](CHANGE_LOG.md) 开头的说明。

### 后续步骤：

对于不同平台（虽然现在只有Windows），需要不同的运行环境。

- [Windows](https://github.com/hiroi-sora/Umi-OCR_runtime_windows)
- 跨平台的支持筹备中

请跳转上述仓库，完成对应平台的开发/运行环境部署。

本项目也拥有非常简易的一键打包脚本，在以上仓库中查看。

## [更新日志](CHANGE_LOG.md)
