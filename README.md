<p align="center">
  <a href="https://github.com/hiroi-sora/Umi-OCR">
    <img width="200" height="128" src="https://tupian.li/images/2022/10/27/icon---256.png" alt="Umi-OCR">
  </a>
</p>

<h1 align="center">Umi-OCR V2 文字识别工具</h1>

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

- **全新升级**：V2版本重构了绝大部分代码，提供焕然一新的界面和更强大的功能。
- **免费**：本项目所有代码开源，完全免费。
- **方便**：解压即用，离线运行，无需网络。
- **高效**：自带高效率离线OCR引擎。只要电脑性能足够，可以比在线OCR服务更快。
- **灵活**：支持定制界面，支持命令行、HTTP接口等多种调用方式。

<p align="center"><img src="https://tupian.li/images/2023/11/19/65599097ab5f4.png" alt="1-标题-1.png" style="width: 80%;"></p>

![1-标题-2.png](https://tupian.li/images/2023/11/19/6559909fdeeba.png)

## 目录

- [截图识别](#截图OCR)
  - [段落合并](#段落合并) - 优化不同文字排版
- [批量识别](#批量OCR)
  - [忽略区域](#忽略区域) - 排除截图水印处的文字
- [二维码](#二维码) 支持扫码或生成二维码图片
- [全局设置](#全局设置) 添加更多PP-OCR支持的语言模型库！
- [命令行调用](docs/README_CLI.md)
- [HTTP接口](docs/README_HTTP.md)
- [构建项目](#构建项目)

## 使用源码：

开发者请务必阅读 [构建项目](#构建项目) 。

## 下载发行版：

#### v2.0.0 预览版本

[Releases](https://github.com/hiroi-sora/Umi-OCR_v2/releases)

#### v1.3 稳定版本

[Umi-OCR 主仓库](https://github.com/hiroi-sora/Umi-OCR)

## 开始使用

软件发布包下载为 `.7z` 压缩包或 `.7z.exe` 自解压包。自解压包可在没有安装压缩软件的电脑上，解压文件。

本软件无需安装。解压后，点击 `Umi-OCR.exe` 即可启动程序。

遇到任何问题，请提 [Issue](https://github.com/hiroi-sora/Umi-OCR/issues) ，我会尽可能帮助你。

## 标签页

Umi-OCR v2 由一系列灵活好用的**标签页**组成。您可按照自己的喜好，打开需要的标签页。

标签栏左上角可以切换**窗口置顶**。右上角能够**锁定标签页**，以防止日常使用中误触关闭标签页。

### 截图OCR

<p align="center"><img src="https://tupian.li/images/2023/11/19/65599097aba8e.png" alt="2-截图-1.png" style="width: 80%;"></p>

**截图OCR**：打开这一页后，就可以用快捷键唤起截图，识别图中的文字。
- 左侧的图片预览栏，可直接用鼠标划选复制。
- 右侧的识别记录栏，可以编辑文字，允许划选多个记录复制。
- 也支持在别处复制图片，粘贴到Umi-OCR进行识别。

#### 段落合并

<p align="center"><img src="https://tupian.li/images/2023/11/19/6559909f3e378.png" alt="2-截图-2.png" style="width: 80%;"></p>

关于 **OCR文本后处理 - 段落合并**： 可以整理OCR结果的排版和顺序，使文本更适合阅读和使用。预设方案：
  - **单行**：合并同一行的文字，适合绝大部分情景。
  - **多行-自然段**：智能识别、合并属于同一段落的文字，适合绝大部分情景，如上图所示。
  - **多行-代码段**：尽可能还原原始排版的缩进与空格。适合识别代码片段，或需要保留空格的场景。
  - **竖排**：适合竖排排版。需要与同样支持竖排识别的模型库配合使用。

---

### 批量OCR

<p align="center"><img src="https://tupian.li/images/2023/11/19/655990a2511e0.png" alt="3-批量-1.png" style="width: 80%;"></p>

**批量OCR**：这一页支持批量导入本地图片并识别。
- 识别内容可以保存为 txt / jsonl / md / csv(Excel) 等多种格式。
- 支持`文本后处理`技术，能识别属于同一自然段的文字，并将其合并。还支持代码段、竖排文本等多种处理方案。
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

### 二维码

<p align="center"><img src="https://tupian.li/images/2023/11/19/655991268d6b1.png" alt="4-二维码-1.png" style="width: 80%;"></p>

**扫码**：
- 可截图/粘贴/拖入本地图片，读取其中的二维码、条形码。
- 支持一图多码。
- 支持19种协议，如下：

`Aztec`,`Codabar`,`Code128`,`Code39`,`Code93`,`DataBar`,`DataBarExpanded`,`DataMatrix`,`EAN13`,`EAN8`,`ITF`,`LinearCodes`,`MatrixCodes`,`MaxiCode`,`MicroQRCode`,`PDF417`,`QRCode`,`UPCA`,`UPCE`,

<p align="center"><img src="https://tupian.li/images/2023/11/19/6559911cda737.png" alt="4-二维码-2.png" style="width: 80%;"></p>

**生成码**：
- 输入文本，生成二维码图片。
- 支持19种协议和**纠错等级**等参数。

---

### 全局设置

<p align="center"><img src="https://tupian.li/images/2023/11/19/655991252e780.png" alt="5-全局设置-1.png" style="width: 80%;"></p>

**全局设置**：在这里可以调整软件的全局参数。常用功能如下：
- 一键添加快捷方式或设置开机自启。
- 更改界面**语言**。Umi支持繁中、英 语、日语等语言。
- 切换界面**主题**。Umi拥有多个亮/暗主题。
- 调整界面**文字的大小**和**字体**。
- 切换OCR插件。
- **渲染器**：软件界面默认支持显卡加速渲染。如果在你的机器上出现截屏闪烁、UI错位的情况，请调整`界面和外观` → `渲染器` ，尝试切换到不同渲染方案，或关闭硬件加速。

---

## 调用接口：

- 命令行手册： [README_CLI.md](docs/README_CLI.md)
- HTTP接口手册： [README_HTTP.md](docs/README_HTTP.md)

## 协助软件界面翻译

参见 [dev-tools/i18n](dev-tools/i18n)

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

</details>


##### 近期开发计划

近期准备进行的工作，将会在 v2 头几个版本内逐步上线。

- [ ] PDF识别
- [ ] 图片翻译

##### 远期计划

<details>
<summary>展开</summary>

这些是预想中的功能，在开发初期已预留好接口，将在远期慢慢实现。

但开发途中受限于实际情况，可能更改功能设计、新增及取消功能。

- 基于GPU的离线OCR。
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

- [主仓库](https://github.com/hiroi-sora/Umi-OCR_v2) 👈
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

如果要拉取本仓库代码，强烈建议只 clone 主分支。因为某些备份分支含有体积很大的二进制库，会让你花费长时间下载。

```
 git clone --branch main --single-branch https://github.com/hiroi-sora/Umi-OCR_v2.git
```

或，将你fork的仓库拉到本地。

### 后续步骤：

请跳转下列仓库，完成对应平台的开发/运行环境部署。

- [Windows](https://github.com/hiroi-sora/Umi-OCR_runtime_windows)
- 跨平台的支持筹备中

## 更新日志

##### v2.0.0 dev `2023.11.14`

- 新增：生成二维码功能。
- 新增：所有图片预览窗口（如截图、二维码页），允许保存图片到指定路径。
- 优化：二维码解析库改用性能更好、功能更丰富的zxingcpp。 (#47) (感谢：@Byxs20)
- 优化：截图预览面板中，文本框的位置更准确。
- 修复：图片预览窗口，无法复制本地图片的Bug。
- 修复：tbpu合并自然段时，垂直距离不准确的Bug。
- 修复：HTTP API 的跨域问题。 (#52)
- 修复：HTTP API 传base64的大小限制问题。 (#49)
- 修复：其它少量报错。
- 翻译：人工校对`繁体中文`和`英语`。 (贡献：@QZGao)

##### v2.0.0 dev `2023.11.5`

- 新增：记忆窗口位置。 (#44)
- 新增：批量识图页增加图片预览窗口，单击图片条目打开。 (#2)
- 新增：检查软件是否有权限读写配置文件。 (#30)
- 新增：报错弹窗提供一键复制及打开issues的功能。
- 新增：全局设置页添加左侧目录栏。
- 新增：插件的多国语言UI机制。
- 优化：截图预览面板中，文本框的位置更准确。
- 优化：调整部分UI布置。
- 修复：扫码模块添加导入异常检查。 (#33)
- 修复：补充扫码页的拖入图片功能。 (#43)
- 修复：输出到单独文件txt时，文件名去除原后缀。 (#36)
- 修复：一些小Bug。

##### v2.0.0 dev `2023.10.25`
- 新增：命令行支持传入图片路径。 (#28)
- 新增：HTTP接口支持Base64传输图片。 (#28)
- 新增：忽略区域功能。
- 新增：二维码识别页。支持识别多种格式的二维码、条形码。 ([Umi-OCR #95](https://github.com/hiroi-sora/Umi-OCR/issues/95))
- 新增：提供备选启动器`UmiOCR-data/RUN_GUI.bat`，供`Umi-OCR.exe`不兼容时使用。 (#21)
- 优化：图片预览窗口，支持用`Tab`切换显示/隐藏文本。
- 优化：记录面板，每条记录顶部添加复制按钮。 (#32)
- 优化：记录面板，拖拽过程中允许指针移出文本框区域。 (#32)
- 优化：重新设计截图缓存机制，避免Image组件销毁时的内存泄露。
- 优化：标签页应用动态解析机制，小幅提高加载速度。
- 优化：运行环境转为64位包。（计划不再提供对32位的兼容）
- 修正：配置项中布尔值解析不正确的问题。 (#30)
- 修正：拖入非图片文件可能导致卡顿几秒的问题。
- 修正：PaddleOCR插件的兼容性问题。 ([Umi-OCR #209](https://github.com/hiroi-sora/Umi-OCR/issues/209))

##### v2.0.0 dev `2023.10.18`
- 新增：截图前自动隐藏窗口。 (#26)
- 新增：更改字体功能。 (#25)
- 新增：可爱的加载动画。
- 新增：截图预览面板 支持显示结果文本、划选文本。
- 新增：截图预览面板 支持将图片复制到剪贴板。
- 新增：结果记录面板 支持跨文本框划选文本。 (#18)
- 新增：结果记录面板 支持删除一条或多条记录。 (#10)
- 新增：支持用Esc或右键中断截图。
- 优化：更改插件目录结构和导入机制。
- 修正：文件重复导致无法添加开机自启。 (#27)


##### v2.0.0 dev `2023.10.10`
- 新功能：第一次启动软件时，根据系统情况，选择最恰当的渲染器。解决截图闪烁问题。 (#7)
- 新功能：初步实现插件机制，切换引擎等组件更加便捷。
- 新功能：支持调整界面比例（文字大小）。
- 优化：调整截图页UI，提高屏占比。优化标签栏阴影。 (#8)
- 优化：双击通知弹窗可打开主窗口。 (#10)
- 优化：截图完成后，如果主窗口在前台，则不弹出成功提示。 (#10)
- 优化：禁用美化效果时，外部弹窗将不会渲染阴影区域。 (#14)
- 优化：Paddle引擎也支持win7系统了。