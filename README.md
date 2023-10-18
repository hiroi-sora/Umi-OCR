<p align="center">
  <a href="https://github.com/hiroi-sora/Umi-OCR">
    <img width="200" height="128" src="https://tupian.li/images/2022/10/27/icon---256.png" alt="Umi-OCR">
  </a>
</p>

<h1 align="center">Umi-OCR V2 文字识别工具</h1>

<p align="center">
  <a href="https://github.com/hiroi-sora/Umi-OCR_v2/releases/latest">
    <img src="https://img.shields.io/github/v/release/hiroi-sora/Umi-OCR_v2?style=flat-square" alt="Umi-OCR_v2">
  </a>
  <a href="License">
    <img src="https://img.shields.io/github/license/hiroi-sora/Umi-OCR_v2?style=flat-square" alt="LICENSE">
  </a>
</p>

<div align="center">
  <h3>
    <span> • </span>
    <a href="#下载">
      下载地址
    </a>
    <span> • </span>
    <a href="#开发计划">
      开发计划
    </a>
    <span> • </span>
    <a href="#构建项目">
      构建项目
    </a>
    <span> • </span>
    <a href="https://github.com/hiroi-sora/Umi-OCR_v2/issues">
      提交Bug
    </a>
  </h3>
</div>
<br>

<div align="center">
  <strong>免费，开源，可批量的离线OCR软件</strong><br>
  <sub>适用于 Windows7 x64 及以上</sub>
</div><br>

这里是记录 [Umi-OCR](https://github.com/hiroi-sora/Umi-OCR) 全新重构版本v2.0的仓库。

- **全新升级**：V2版本重构了绝大部分代码，提供焕然一新的界面和更强大的功能。
- **免费**：本项目所有代码开源，完全免费。
- **方便**：解压即用，离线运行，无需网络。
- **批量**：支持批量导入处理图片。也可以即时截屏识别。
- **高效**：自带高效的离线OCR引擎。只要电脑性能足够，可以比在线OCR服务更快。
- **灵活**：支持定制界面，支持命令行、HTTP接口等多种调用方式。


![Umi-OCR-截图页2.png](https://tupian.li/images/2023/10/18/652fed59f21c8.png)
![i18n.png](https://tupian.li/images/2023/09/25/65119e87e8041.png)

## 源码：

开发者请务必阅读 [构建项目](#构建项目) 。

## 下载：

#### v2.0.0 预览版本

[Releases](https://github.com/hiroi-sora/Umi-OCR_v2/releases)

<!-- #### v2 插件库

[Umi-OCR_plugins](https://github.com/hiroi-sora/Umi-OCR_plugins) -->

#### v1.3 稳定版本

[Umi-OCR 主仓库](https://github.com/hiroi-sora/Umi-OCR)

## 标签页

Umi-OCR v2 由一系列灵活好用的标签页组成。您可按照自己的喜好，打开需要的标签页，并锁定标签栏。

### 截图OCR

![Umi-OCR-截图页1.png](https://tupian.li/images/2023/10/18/652fea30b095b.png)

**截图OCR**：打开这一页后，就可以用快捷键唤起截图，识别图中的文字。
- 左侧的图片预览栏，可直接用鼠标划选复制。
- 右侧的识别记录栏，可以编辑文字，允许划选多个记录复制。
- 也支持在别处复制图片，粘贴到Umi-OCR进行识别。

---

### 批量OCR

![Umi-OCR-批量页1.png](https://tupian.li/images/2023/10/18/652fefa69c9b8.png)

**批量OCR**：这一页支持批量导入本地图片并识别。
- 识别内容可以保存为 txt / jsonl / md / csv(Excel) 等多种格式。
- 支持`文本后处理`技术，能识别属于同一自然段的文字，并将其合并。还支持代码段、竖排文本等多种处理方案。
- 没有数量上限，可一次性导入几百张图片进行任务。
- 支持任务完成后自动关机/待机。

---

### 全局设置

![Umi-OCR-全局页1.png](https://tupian.li/images/2023/10/18/652ff116f0f15.png)

**全局设置**：在这里可以调整软件的全局参数。
- 支持更改界面语言。（翻译校对工作将在第一个正式版发布后进行）
- 支持切换界面主题。Umi-OCR拥有多个亮/暗主题。
- 可以调整界面文字大小、文字字体。
- 切换OCR插件。

---



## 辅助功能说明：

- **多国语言界面**：软件界面支持多国语言。目前预览阶段为AI翻译生成，可能词义和排版不好，或者有错漏的情况。正式发布时会进行人工校对。
- **渲染器**：软件界面默认支持显卡加速渲染。但是如果在你的机器上出现截屏闪烁、UI错位的情况，请调整 `全局设置` → `界面和外观` → `渲染器` 。
- **文本块后处理（段落合并）** 可以整理OCR结果的排版和顺序，使文本更适合阅读和使用。预设方案如下：
  - **单行**：合并同一行的文字，适合绝大部分情景。
  - **多行-自然段**：智能识别、合并属于同一段落的文字，适合绝大部分情景。
  - **多行-代码段**：尽可能还原原始排版的缩进与空格。适合识别代码片段，或需要保留空格的场景。
  - **竖排**：适合竖排排版。需要与同样支持竖排识别的模型库配合使用。

## 调用接口：

Umi-OCR v2 具有一套强大的命令行控制模式，及开发中的HTTP接口 / Web服务器模式。

#### 命令行指令

命令行调用入口就是主程序 `Umi-OCR.exe` 。

获取说明：`Umi-OCR.exe --help`

输入任意指令时，若系统中没有Umi-OCR服务进程在运行，则会自动启动Umi-OCR主进程。

#### 快捷指令

弹出主窗口：`Umi-OCR.exe --show`

隐藏主窗口：`Umi-OCR.exe --hide`

关闭软件：`Umi-OCR.exe --quit`

截屏并获取OCR结果：`Umi-OCR.exe --screenshot`

粘贴图片，并获取OCR结果：`Umi-OCR.exe --clipboard`

#### 高级指令

Umi-OCR 允许通过命令行调用每一个标签页（模块）上的任意函数，但是使用门槛较高。

如果有需要使用高级指令，请阅读下列说明，仔细编写指令。

<details>
<summary>展开</summary>

查询当前已打开的页面，及可以创建的页面模板：`Umi-OCR.exe --all_pages`

根据页面模板序号，创建新标签页：`Umi-OCR.exe --add_page [index]`

根据标签页序号，删除已有标签页：`Umi-OCR.exe --del_page [index]`

> 每个标签页，通常会具有两个模块，一个是py，一个是qml。每个模块上有不同的函数。

查询当前已打开的模块：`Umi-OCR.exe --all_modules`

查询某个py模块上有什么可调用的函数：`Umi-OCR.exe --call_py [name]`

查询某个qml模块上有什么可调用的函数：`Umi-OCR.exe --call_qml [name]`

> --call指令允许只写模块名的首字母。假设一个qml模块叫 `ScreenshotOCR_1` ，那么 `--call_qml Scre` 也可以正确调用。

调用py模块上的函数：`Umi-OCR.exe --call_py [name] --func [function] [..paras]`

调用qml模块上的函数：`Umi-OCR.exe --call_qml [name] --func [function] [..paras]`

> 允许在指令最后传入任意个参数，但目前只支持识别为字符串类型。

通过上述的指令调用函数，不会得到函数返回值。因为上述会自动跳转到UI线程运行，避免跨线程调用导致程序崩溃的风险。

如果要取得函数返回值，可以加上 `--thread` 。如：

`Umi-OCR.exe --call_qml [name] --func [function] --thread [..paras]`

这样会在子线程同步执行函数，并将返回值输出给命令行。但是子线程执行部分函数可能报错或崩溃。

> 建议阅读本项目源代码（或发行包中的代码文件）来辅助编写指令。

</details>

#### HTTP接口

端口号可以在`全局设置`中查看及修改。请开启`全局设置`顶部的`高级`开关。

目前仅开放一个接口，用于传输命令行指令。

- `POST /argv`
- 参数：一个列表，元素均为字符串，格式与命令行指令一致。
- 如：命令行 `Umi-OCR.exe --call_qml ScreenshotOCR`
- 等价于： `POST /argv ["--call_qml", "ScreenshotOCR"]`

## 关于项目依赖：

支持的离线OCR引擎：

- [PaddleOCR-json](https://github.com/hiroi-sora/PaddleOCR-json) 仅支持Win10 x64以上，性能更好，速度快。
- [RapidOCR-json](https://github.com/hiroi-sora/RapidOCR-json) 兼容Win7 x64 ，内存占用低，适合低配机器。

运行环境框架：

- [PyStand](https://github.com/skywind3000/PyStand) 的定制版。

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

</details>


##### 近期开发计划

近期准备进行的工作，将会在 v2 头几个版本内逐步上线。

- [ ] 制订软件界面翻译的开源协作机制。
- [ ] 快捷键权限优化。
- [ ] 允许隐藏托盘图标。
- [ ] 截图联动/截图翻译。
- [ ] 忽略区域。
- [ ] PDF识别。
- [ ] 批量识别页面的图片预览窗口。
- [ ] 高级截图（仿Snipaste，支持贴图）。
- [ ] 完善Web服务器功能。

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
- 兼容32位系统。

</details>

## 构建项目

### 第一步：下载代码

强烈建议只 clone 主分支，因为某些分支含有体积很大的二进制库，会让你花费很长时间下载。

```
 git clone --branch main --single-branch git@github.com:hiroi-sora/Umi-OCR_v2.git
```

### 第二步：运行环境

根据下列文档，完成对应平台的开发/运行环境部署。

- [Windows](https://github.com/hiroi-sora/Umi-OCR_runtime_windows)
- 跨平台的支持筹备中

## 更新日志

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