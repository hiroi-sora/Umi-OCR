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

指定地址：`Umi-OCR.exe --path "D:/xxx.png"`

OCR指令均可在控制台回传识别结果。请耐心等待，在一次指令结束前不要输入下一条指令。

OCR指令的参数（如识别语言，是否复制到剪贴板）等同于`截图OCR`标签页。请在该标签页中修改参数。

#### 指令简写

所有指令支持用前几个字母替代，如`--screenshot`、`--clipboard`可以分别简写为`--sc`、`--cl`。具体可自己尝试。

---

### 结果输出

#### 将结果输出到文件：

- **覆盖原文件** ` --> 文件路径`
- **追加到文件末尾** ` -->> 文件路径`

例：
```
./Umi-OCR.exe --screenshot --> test.txt
或加上双引号：
./Umi-OCR.exe --screenshot "-->" test.txt
```

> 注1：由于运行环境的一些限制，无法使用系统管道重定向符`>`。请使用`-->`代替。  
> 注2：如果该指令失效，请使用双引号括起指令：`"-->"`

#### 将结果复制到剪贴板
- ` | clip`

例：
```
./Umi-OCR.exe --screenshot | clip
```

---

### 高级指令

（仅供有经验的开发者使用）

高级指令代表了一种无限的可能性(笑)，允许通过命令行调用每一个标签页（模块）上的每一个函数。但是用法比较复杂，你需要在一定程度上阅读本项目源码才能知道该调用哪个函数。

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

[name] 为模块名，[function] 为函数名， [..paras] 为任意个参数（只支持字符串类型）。  
调用py模块上的函数：  
```
Umi-OCR.exe --call_py [name] --func [function] [..paras]
```

调用qml模块上的函数：
```
Umi-OCR.exe --call_qml [name] --func [function] [..paras]
```

#### 同步调用函数

> 命令行解析器运行在子线程。为了确保线程安全，会发送到主线程执行命令。所以对于你来说就是异步执行的了，即无法取得函数的返回值。  
> 如果要获取函数返回值，可传入 --thread 指令，同步执行命令。  
> 这种操作较不安全，可能导致功能不正常甚至程序崩溃。

```
Umi-OCR.exe --call_qml [name] --func [function] --thread [..paras]
```
