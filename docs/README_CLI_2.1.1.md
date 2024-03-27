- 命令行手册： [README_CLI.md](README_CLI.md)
- HTTP接口手册： [README_HTTP.md](README_HTTP.md)

# 命令行手册

#### 基础说明

命令行调用入口就是主程序 `Umi-OCR.exe` 。如果你使用的是备用启动器（如`UmiOCR-data/RUN_GUI.bat`），可能无法使用命令行。

![Umi-OCR-全局页-服务.png](https://tupian.li/images/2023/10/25/653907e9bac06.png)

如上图，必须允许HTTP服务才能使用命令行（默认开启）。主机选择`仅本地`就行了。

> Umi-OCR 依赖HTTP接口进行跨进程通信，将你输入的命令行指令传递给后台的Umi-OCR处理进程。通信过程仅在系统内部的本地环回进行，不会泄露到外部（不经过物理网卡），请放心使用。  

获取说明：`Umi-OCR.exe --help`

#### 软件操控指令

弹出主窗口：`Umi-OCR.exe --show`

隐藏主窗口：`Umi-OCR.exe --hide`

关闭软件：`Umi-OCR.exe --quit`

#### OCR指令

截屏：`Umi-OCR.exe --screenshot`

粘贴图片：`Umi-OCR.exe --clipboard`

指定路径：`Umi-OCR.exe --path "D:/xxx.png"`

- 可传入文件夹的路径。将搜索文件夹中所有图片（包括嵌套子文件夹），并输出所有识别结果。
- 可传入多个路径。请用双引号`""`包裹单个路径，不同路径间用空格 ` ` 隔开。

指定多个路径示例：`Umi-OCR.exe --path "D:/img1.png" "D:/img2.png" "D:/image/test"`

注意：

- 注意：多图识别时，耗时较长；一次命令结束前不要输入下一个命令。
- 对于截屏、粘贴、路径指令，OCR参数（如识别语言，是否复制到剪贴板、是否弹出主窗口）采用`截图OCR`标签页的设定。如果不希望命令行任务弹出主窗口，请在`截图OCR`标签页中关闭该选项。

#### 二维码指令

识别二维码：`Umi-OCR.exe --qrcode_read "D:/xxx.png"`

- 与OCR指令一致，二维码识别的指令也支持传入多个图片&文件夹路径。

生成二维码：`Umi-OCR.exe --qrcode_create "文本内容" "D:/输出图片.jpeg"`

- 默认的图片宽高为最小适配长度。也可以在指令后方加上数字，手动指定图片宽高：

例，同时指定宽高为128像素：`Umi-OCR.exe --qrcode_create "文本内容" "D:/输出图片.jpeg" 128`

例，宽128，高256像素：`Umi-OCR.exe --qrcode_create "文本内容" "D:/输出图片.jpeg" 128 256`

#### 关于指令简写

- 所有指令支持用前几个字母替代，如`--screenshot`、`--clipboard`可以分别简写为`--sc`、`--cl`。具体可自己尝试。
- 对于大部分系统，支持使用小写文件名+省略`.exe`，例： `umi-ocr --sc`

---

### 结果输出

#### 将结果输出到文件：

- **覆盖原文件** ` --output "文件路径.txt"`
- **追加到文件末尾** ` --output_append "文件路径.txt"`

也可以使用箭头符号：

- `"-->"` 等价于 `--output`
- `"-->>"` 等价于 `--output_append`

例：
```
./Umi-OCR.exe --screenshot --output test.txt
./Umi-OCR.exe --screenshot "-->" test.txt
```

> 注：由于运行环境的一些限制，无法使用系统管道重定向符`>`。请使用 `-->` 或 `--output` 代替。  

#### 将结果复制到剪贴板
- ` | clip`

例：
```
./Umi-OCR.exe --screenshot | clip
```

---

### 高级指令

（仅供有经验的开发者使用）

高级指令代表了一种无限的可能性(笑)，允许通过命令行调用任意标签页（模块）上的任意函数。但是用法比较复杂，你需要在一定程度上阅读本项目源码才能知道该调用哪个函数、传入什么参数。

#### 页面指令

> “页面模板”相当于收藏夹，可以从收藏夹中打开一个新页面。  
> “已打开的页面”可以关闭。  

查询当前已打开的页面，及所有页面模板：可以获取 [index]
```
Umi-OCR.exe --all_pages
```

创建新标签页：[index] 为页面模板序号
```
Umi-OCR.exe --add_page [index]
```

删除已创建的标签页：[index] 为现有页面序号
```
Umi-OCR.exe --del_page [index]
```

#### 模块指令

> 每个标签页，通常会具有两个模块，一个是py，一个是qml。还可能会有一些不依附于标签页的独立py或qml模块。  
> 每个模块上都有一些函数可以被调用。 
> 模块名 [name] 允许简写，如一个模块全称是 "ScreenshotOCR_1" ，那么可用 "ScreenshotOCR" 来代替。  
> 每次程序运行，模块名（的后缀）不一定相同。请使用简写来忽略后缀。

查询当前存在的py和qml模块：可获取 [name]
```
Umi-OCR.exe --all_modules
```

#### 函数指令

查询某个py模块上有什么可调用的函数： [name] 为模块名
```
Umi-OCR.exe --call_py [name]
```

查询某个qml模块上有什么可调用的函数： [name] 为模块名
```
Umi-OCR.exe --call_qml [name]
```

调用py模块上的函数：  

- [name] 为模块名，[function] 为函数名。 [..paras] 为任意个参数。
- paras 输入字符串。会根据文本结构，自动转为4种变量类型： `int`、`float`、`list`、`dict` 。  
```
Umi-OCR.exe --call_py [name] --func [function] [..paras]
```

调用qml模块上的函数：
```
Umi-OCR.exe --call_qml [name] --func [function] [..paras]
```

示例，调用二维码页qml模块的路径扫码函数，传入路径列表：

```
umi-ocr --call_qml QRCode --func scanPaths '[\"D:/Pictures/Screenshots/test/二维码/1111.png\",\"D:/Pictures/Screenshots/test/二维码/2222.png\"]'
```

#### 同步调用函数

> 命令行解析器运行在子线程。为了确保线程安全，默认转到主线程执行命令。所以对于你来说就是异步执行的了，即无法取得函数的返回值。  
> 如果要获取函数返回值，可传入 --thread 指令，同步执行命令。  
> 这种操作较不安全，可能导致功能不正常甚至程序崩溃。

```
Umi-OCR.exe --call_qml [name] --func [function] --thread [..paras]
```
