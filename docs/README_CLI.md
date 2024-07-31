[Translate to English](https://github-com.translate.goog/hiroi-sora/Umi-OCR/blob/main/docs/README_CLI.md?_x_tr_sl=zh-CN&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp)

- 命令行手册
- [HTTP接口手册](http/README.md)

# 命令行手册

### 基础说明

命令行调用入口就是主程序 `Umi-OCR.exe` 。如果你使用的是备用启动器（如`UmiOCR-data/RUN_GUI.bat`），可能无法使用命令行。

![Umi-OCR-全局页-服务.png](https://tupian.li/images/2023/10/25/653907e9bac06.png)

如上图，必须允许HTTP服务才能使用命令行（默认开启）。主机选择 **仅本地** 就行了。

> Umi-OCR 依赖HTTP接口进行跨进程通信，将你输入的命令行指令传递给后台的Umi-OCR处理进程。通信过程仅在系统内部的本地环回进行，不会泄露到外部（不经过物理网卡），请放心使用。  

**获取说明**：`umi-ocr --help`

### 软件操控指令

**弹出主窗口**：`umi-ocr --show`

**隐藏主窗口**：`umi-ocr --hide`

**关闭软件**：`umi-ocr --quit`

### OCR指令

**鼠标截屏**：`umi-ocr --screenshot`

<details>
<summary><b>范围截屏</b>（无需鼠标划选）</summary>
</br>
自动对指定屏幕、指定区域进行截屏。

**范围截屏** 指令：
```bash
umi-ocr --screenshot screen=0 rect=x,y,w,h
```

范围截屏控制参数：
- `screen`: 要截图的显示器编号（多个显示器时有效），从0开始。缺省为0。
- `rect`: 截图范围矩形框，`x坐标,y坐标,w宽度,h高度`。缺省为全屏。

注意：
- 这两个参数的前面无需加`--`。
- 这两个参数至少要填一个，才能触发范围截图。没有任一参数时，执行鼠标截屏。

示例1：截取第1个显示器的全屏
```bash
umi-ocr --screenshot screen=0
```

示例2：截取第2个显示器，从左上角 (50,100) 开始，大小为 300x200 的矩形区域
```bash
umi-ocr --screenshot screen=1 rect=50,100,300,200
```

示例3：与 [HotkeysCMD](https://github.com/hiroi-sora/HotkeysCMD) 工具配合，实现点击 **快捷键** 进行范围截图。

向 HotkeysCMD 的配置文件中添加这一行，表示点击 `F10` 时进行范围截图：

```bash
F10 umi-ocr --screenshot screen=0 rect=50,100,300,200
```

更多快捷键定义方式，详见 [HotkeysCMD](https://github.com/hiroi-sora/HotkeysCMD) 文档。

</details></br>

**粘贴图片**：`umi-ocr --clipboard`

**指定路径**：`umi-ocr --path "D:/xxx.png"`

- 可传入文件夹的路径。将搜索文件夹中所有图片（包括嵌套子文件夹），并输出所有识别结果。
- 可传入多个路径。请用双引号`""`包裹单个路径，不同路径间用空格 ` ` 隔开。

**指定多个路径** 示例：`umi-ocr --path "D:/img1.png" "D:/img2.png" "D:/image/test"`

提示：

- 多图识别时，耗时较长；一次命令结束前不要输入下一个命令。
- 对于截屏、粘贴、路径指令，OCR参数（如识别语言，是否复制到剪贴板、是否弹出主窗口）采用`截图OCR`标签页的设定。如果不希望命令行任务弹出主窗口，请在`截图OCR`标签页中关闭该选项。

### 二维码指令

**识别二维码**：`umi-ocr --qrcode_read "D:/xxx.png"`

- 与OCR指令一致，二维码识别的指令也支持传入多个图片&文件夹路径。

**生成二维码**：`umi-ocr --qrcode_create "文本内容" "D:/输出图片.jpeg"`

- 默认的图片宽高为最小适配长度。也可以在指令后方加上数字，手动指定图片宽高：

例，同时指定宽高为128像素：`umi-ocr --qrcode_create "文本内容" "D:/输出图片.jpeg" 128`

例，宽128，高256像素：`umi-ocr --qrcode_create "文本内容" "D:/输出图片.jpeg" 128 256`

### 关于指令简写

- 所有指令支持用前几个字母替代，如`--screenshot`、`--clipboard`可以分别简写为`--sc`、`--clipbo`。具体可自己尝试。
- 对于大部分系统，支持使用小写文件名+省略`.exe`来调用程序。即 `umi-ocr --sc` 等价于  `Umi-OCR.exe --sc` 。

---

### 命令行结果输出

- **复制到剪贴板** ` --clip`
- **输出到文件（覆盖）** ` --output "file.txt"`
- **输出到文件（追加）** ` --output_append "file.txt"`

也可以使用箭头符号：

- `"-->"` 等价于 `--output`
- `"-->>"` 等价于 `--output_append`

例：
```bash
umi-ocr --screenshot --clip
umi-ocr --screenshot --output test.txt
umi-ocr --screenshot "-->" test.txt
```

> 注：由于运行环境的一些限制，Umi-OCR 暂时无法重定向输出流，系统管道重定向符`>`、管道操作符`|`可能失效。  
> 如果需要用程序 调用命令行指令，但是发现无法收到回传，可使用 [HTTP转发命令行](http/argv.md#/argv) 代替。

---

## 高级指令

（仅供有经验的开发者使用）

高级指令代表了一种无限的可能性(笑)，允许通过命令行调用任意标签页（模块）上的任意函数。但是用法比较复杂，你需要在一定程度上阅读本项目源码才能知道该调用哪个函数、传入什么参数。

### 页面指令

> “页面模板”相当于收藏夹，可以从收藏夹中打开一个新页面。  
> “已打开的页面”可以关闭。  

查询当前已打开的页面，及所有页面模板：可以获取 [index]
```
umi-ocr --all_pages
```

创建新标签页：[index] 为页面模板序号
```
umi-ocr --add_page [index]
```

删除已创建的标签页：[index] 为现有页面序号
```
umi-ocr --del_page [index]
```

### 模块指令

> 每个标签页，通常会具有两个模块，一个是py，一个是qml。还可能会有一些不依附于标签页的独立py或qml模块。  
> 每个模块上都有一些函数可以被调用。 
> 模块名 [name] 允许简写，如一个模块全称是 "ScreenshotOCR_1" ，那么可用 "ScreenshotOCR" 来代替。  
> 每次程序运行，模块名（的后缀）不一定相同。请使用简写来忽略后缀。

查询当前存在的py和qml模块：可获取 [name]
```
umi-ocr --all_modules
```

### 函数指令

查询某个py模块上有什么可调用的函数： [name] 为模块名
```
umi-ocr --call_py [name]
```

查询某个qml模块上有什么可调用的函数： [name] 为模块名
```
umi-ocr --call_qml [name]
```

调用py模块上的函数：  

- [name] 为模块名，[function] 为函数名。 [..paras] 为任意个参数。
- paras 输入字符串。会根据文本结构，自动转为4种变量类型： `int`、`float`、`list`、`dict` 。  
```
umi-ocr --call_py [name] --func [function] [..paras]
```

调用qml模块上的函数：
```
umi-ocr --call_qml [name] --func [function] [..paras]
```

示例，调用二维码页qml模块的路径扫码函数，传入路径列表：

```
umi-ocr --call_qml QRCode --func scanPaths '[\"D:/Pictures/Screenshots/test/二维码/1111.png\",\"D:/Pictures/Screenshots/test/二维码/2222.png\"]'
```

### 同步调用函数

> 命令行解析器运行在子线程。为了确保线程安全，默认转到主线程执行命令。所以对于你来说就是异步执行的了，即无法取得函数的返回值。  
> 如果要获取函数返回值，可传入 --thread 指令，同步执行命令。  
> 这种操作较不安全，可能导致功能不正常甚至程序崩溃。

```
umi-ocr --call_qml [name] --func [function] --thread [..paras]
```

---

### 高级指令示例：

示例目标：将一些PDF文档添加到软件，生成双层可搜索PDF。

（提示：这个例子只是用来演示高级指令能做到什么事情。PDF文档识别可以直接调用 [HTTP接口](http/api_doc.md) 。）

做法：

##### 1. （可选）如果当前没有打开`批量文档`标签页，那么打开它：
- 1.1. 查询当前所有页面模板：
```bash
umi-ocr --all_pages
```
- 1.2. 已知`BatchDOC`标签页的 `template_index` 为`3`。创建该标签页：
```bash
umi-ocr --add_page 3
```
- 1.3. 检查 `BatchDOC` 模块是否已存在：
```bash
umi-ocr --all_modules
```
- 发现在`Qml modules`中，已存在 `BatchDOC_1` ，那么就是正确的。

##### 2. 将多个文档的路径，输入软件：
- 假设想要添加以下的文件：
```bash
C:\Users\My\Desktop\111.epub
C:\Users\My\Desktop\222.pdf
```
- 使用以下指令，输入文档路径：（路径中`\`需要改为`/`）
```bash
umi-ocr --call_qml BatchDOC --func addDocs '[ \"C:/Users/My/Desktop/111.epub\", \"C:/Users/My/Desktop/222.pdf\"]'
```
关于`addDocs`后面路径参数的格式：
- 在 Powershell 中，最外层为单引号`'`，且左双引号前面必须有空格。即：`'[■\"path_1\",■\"path_2\",■\"path_3\"]'` （将`■`替换为空格` `）。单个路径为`'[■\"路径1\"]'`。
- 在 Terminal （终端）中，最外层为双引号`"`。即：`"[\"path_1\",\"path_2\",\"path_3\"]"`。
- 这是 Windows 解析命令行参数的规则限制，与 Umi 自身的设计无关。

##### 3. 启动任务：
```bash
umi-ocr --call_qml BatchDOC --func docStart
```
- 暂时无法通过CLI更改保存文件的类型（默认为 双层可搜索PDF ）。想要添加其他保存类型，必须在软件界面中勾选。
