# 分支使用说明

点击后续列表的版本号链接，可前往对应备份分支页面。

部分备份分支含有体积较大的二进制库，会让你花费长时间下载。因此，建议只下载你需要用的分支。

方法1：将所需的分支，fork到你自己的账号下，然后clone你自己仓库。

方法2：使用以下命令手动clone指定分支：

```
git clone --single-branch --branch [分支名] https://github.com/hiroi-sora/Umi-OCR.git
```

方法3：在本仓库手动下载指定分支的zip源码包。

`[分支名]` 可以是 `main` 、`release/2.0.0` 等，详见下方列表。

`main`、`dev` 等分支，可能含有开发中的不稳定的新功能。如果用于研究学习或二次开发，建议选择 `release` 开头的分支。

# 更新日志 CHANGE LOG

##### v2.1.0 `2024.2.29`

分支名：`release/2.1.0`

- 新增：批量文档识别功能。支持 `pdf, epub, mobi` 等格式。
- 新增：允许隐藏托盘图标。 (#338)
- 新增：重复上一次截图区域的快捷键。 (#357)
- 新增：用本地图片浏览器打开图片的快捷按钮。 (#335)
- 更新：更强大的排版解析器。
- 修复：避免系统环境变量`QMLSCENE_DEVICE`的影响。 (#270)

##### v2.0.2 `2024.1.15`

分支名：`release/2.0.2`

- 更新：全局设置可调节 图片文字叠加层`开启/关闭`默认显示状态。 (#264)
- 优化：输出为`txt 单独文件`时，将应用`指定路径`参数。 (#269)
- 优化：`段落合并-多行-代码段` 去除结尾多余换行符。 (#292)
- 优化：渲染器不兼容时，减少渲染层级错误的影响。 (#259)
- 修复：清理图片缓存前进行检查，避免空图错误。 (#279)
- 修复：记录面板中，光标无法移到第1个字符前面。 (#264)
- 修复：系统语言非简体中文时，软件启动异常。 (#274) (#306)
- 修复：csv输出的字符编码兼容性问题。 (#284)
- 修复：`段落合并参数不存在` 的误报。
- 修复：组件`DefaultTips`不生效。

##### v2.0.1 `2023.12.8`

分支名：`release/2.0.1`

- 更新：重新设计了OCR HTTP接口，允许省略参数，允许指定段落合并。
- 更新：命令行增加指令`-->`和`-->>`，将结果输出到文件。
- 优化：调整图像数据的内部编码，减少英文空格丢失的几率。
- 优化：调整部分UI文本和布局。
- 优化：csv默认保存为ansi编码，以兼容Office Excel。 (#237)
- 修复：开启“禁用美化效果”后，外部通知弹窗无法关闭。 (#234)
- 修复：别的程序通过命令行调用Umi-OCR时，无法获取stdout输出。

##### [v2.0.0](https://github.com/hiroi-sora/Umi-OCR/tree/release/2.0.0) `2023.11.19`

分支名：`release/2.0.0`

- 优化：插件UI翻译机制。
- 优化：下拉框UI。
- 修复：段落合并-自然段合并的bug。

##### v2.0.0 dev `2023.11.14`

- 新增：生成二维码功能。
- 新增：所有图片预览窗口（如截图、二维码页），允许保存图片到指定路径。
- 优化：二维码解析库改用性能更好、功能更丰富的zxingcpp。 ([v2 #47](https://github.com/hiroi-sora/Umi-OCR_v2/issues/47)) (感谢：@Byxs20)
- 优化：截图预览面板中，文本框的位置更准确。
- 修复：图片预览窗口，无法复制本地图片的Bug。
- 修复：tbpu合并自然段时，垂直距离不准确的Bug。
- 修复：HTTP API 的跨域问题。 [v2 #52](https://github.com/hiroi-sora/Umi-OCR_v2/issues/52)
- 修复：HTTP API 传base64的大小限制问题。 [v2 #49](https://github.com/hiroi-sora/Umi-OCR_v2/issues/49)
- 修复：其它少量报错。
- 翻译：人工校对`繁体中文`和`英语`。 (贡献：@QZGao)

##### v2.0.0 dev `2023.11.5`

- 新增：记忆窗口位置。 [v2 #44](https://github.com/hiroi-sora/Umi-OCR_v2/issues/44)
- 新增：批量识图页增加图片预览窗口，单击图片条目打开。 [v2 #2](https://github.com/hiroi-sora/Umi-OCR_v2/issues/2)
- 新增：检查软件是否有权限读写配置文件。 [v2 #30](https://github.com/hiroi-sora/Umi-OCR_v2/issues/30)
- 新增：报错弹窗提供一键复制及打开issues的功能。
- 新增：全局设置页添加左侧目录栏。
- 新增：插件的多国语言UI机制。
- 优化：截图预览面板中，文本框的位置更准确。
- 优化：调整部分UI布置。
- 修复：扫码模块添加导入异常检查。 [v2 #33](https://github.com/hiroi-sora/Umi-OCR_v2/issues/33)
- 修复：补充扫码页的拖入图片功能。 [v2 #43](https://github.com/hiroi-sora/Umi-OCR_v2/issues/43)
- 修复：输出到单独文件txt时，文件名去除原后缀。 [v2 #36](https://github.com/hiroi-sora/Umi-OCR_v2/issues/36)
- 修复：一些小Bug。

##### v2.0.0 dev `2023.10.25`
- 新增：命令行支持传入图片路径。 [v2 #28](https://github.com/hiroi-sora/Umi-OCR_v2/issues/28)
- 新增：HTTP接口支持Base64传输图片。 [v2 #28](https://github.com/hiroi-sora/Umi-OCR_v2/issues/28)
- 新增：忽略区域功能。
- 新增：二维码识别页。支持识别多种格式的二维码、条形码。 ([Umi-OCR #95](https://github.com/hiroi-sora/Umi-OCR/issues/95))
- 新增：提供备选启动器`UmiOCR-data/RUN_GUI.bat`，供`Umi-OCR.exe`不兼容时使用。 [v2 #21](https://github.com/hiroi-sora/Umi-OCR_v2/issues/21)
- 优化：图片预览窗口，支持用`Tab`切换显示/隐藏文本。
- 优化：记录面板，每条记录顶部添加复制按钮。 [v2 #32](https://github.com/hiroi-sora/Umi-OCR_v2/issues/32)
- 优化：记录面板，拖拽过程中允许指针移出文本框区域。 [v2 #32](https://github.com/hiroi-sora/Umi-OCR_v2/issues/32)
- 优化：重新设计截图缓存机制，避免Image组件销毁时的内存泄露。
- 优化：标签页应用动态解析机制，小幅提高加载速度。
- 优化：运行环境转为64位包。（计划不再提供对32位的兼容）
- 修正：配置项中布尔值解析不正确的问题。 [v2 #30](https://github.com/hiroi-sora/Umi-OCR_v2/issues/30)
- 修正：拖入非图片文件可能导致卡顿几秒的问题。
- 修正：PaddleOCR插件的兼容性问题。 ([Umi-OCR #209](https://github.com/hiroi-sora/Umi-OCR/issues/209))

##### v2.0.0 dev `2023.10.18`
- 新增：截图前自动隐藏窗口。 [v2 #26](https://github.com/hiroi-sora/Umi-OCR_v2/issues/26)
- 新增：更改字体功能。 [v2 #25](https://github.com/hiroi-sora/Umi-OCR_v2/issues/25)
- 新增：可爱的加载动画。
- 新增：截图预览面板 支持显示结果文本、划选文本。
- 新增：截图预览面板 支持将图片复制到剪贴板。
- 新增：结果记录面板 支持跨文本框划选文本。 [v2 #18](https://github.com/hiroi-sora/Umi-OCR_v2/issues/18)
- 新增：结果记录面板 支持删除一条或多条记录。 [v2 #10](https://github.com/hiroi-sora/Umi-OCR_v2/issues/10)
- 新增：支持用Esc或右键中断截图。
- 优化：更改插件目录结构和导入机制。
- 修正：文件重复导致无法添加开机自启。 [v2 #27](https://github.com/hiroi-sora/Umi-OCR_v2/issues/27)


##### v2.0.0 dev `2023.10.10`
- 新功能：第一次启动软件时，根据系统情况，选择最恰当的渲染器。解决截图闪烁问题。 [v2 #7](https://github.com/hiroi-sora/Umi-OCR_v2/issues/7)
- 新功能：初步实现插件机制，切换引擎等组件更加便捷。
- 新功能：支持调整界面比例（文字大小）。
- 优化：调整截图页UI，提高屏占比。优化标签栏阴影。 [v2 #8](https://github.com/hiroi-sora/Umi-OCR_v2/issues/8)
- 优化：双击通知弹窗可打开主窗口。 [v2 #10](https://github.com/hiroi-sora/Umi-OCR_v2/issues/10)
- 优化：截图完成后，如果主窗口在前台，则不弹出成功提示。 [v2 #10](https://github.com/hiroi-sora/Umi-OCR_v2/issues/10)
- 优化：禁用美化效果时，外部弹窗将不会渲染阴影区域。 [v2 #14](https://github.com/hiroi-sora/Umi-OCR_v2/issues/14)
- 优化：Paddle引擎也支持win7系统了。

##### v2.0.0 dev `2023.9.25`

##### v2.0.0 dev `2023.9.8`
- 支持多种界面语言（实验性）

##### v2.0.0 dev `2023.9.7`

##### v2.0.0 dev `2023.8.9`
- 截图OCR
- 兼容高分辨率屏幕和多屏幕系统
- 更准确、智能的段落合并

##### v2.0.0 dev `2023.7.26`
- 批量OCR
- 现代化UI风格
- 自定义标签页系统
- 主题切换：明亮/深色

---

##### [v1.3.7](https://github.com/hiroi-sora/Umi-OCR/tree/release/1.3.7) `2023.10.10`
- Paddle引擎兼容Win7 x64 。

##### v1.3.6 `2023.9.26`
- 新功能：更强大的段落合并方案-`单行/多行自然段/多行代码段`。支持自动判断中/英文段落，采取对应的合并规则。
- 移除一些过时的段落合并方案。
- 功能调整：`截图联动` 划分为独立的功能，不受常规截图OCR影响。

##### [v1.3.5](https://github.com/hiroi-sora/Umi-OCR/tree/release/1.3.5) `2023.6.20`
<!-- 6.5k★ 撒花~ -->
- 新功能：复制识别结果后，可发送指定按键，以便联动唤起翻译器等工具。
- 新功能：命令行增加切换识别语言的指令。
- 修Bug：低配置机器上有概率误报`OCR init timeout: 5s` 。[#154](https://github.com/hiroi-sora/Umi-OCR/issues/154) , [#156](https://github.com/hiroi-sora/Umi-OCR/issues/156)。
- 调整：默认停止任务30秒后释放一次内存。

##### [v1.3.4](https://github.com/hiroi-sora/Umi-OCR/tree/release/1.3.4) `2023.4.26`
<!-- 一周年纪念！ -->
- 新功能：截图预览窗口。
- 新功能：可用方向键微调截图框位置。
- 修Bug：拖入图片时有几率卡退主窗口 [issue #126](https://github.com/hiroi-sora/Umi-OCR/issues/126) 。
- 优化了一些处理流程。

##### [v1.3.3](https://github.com/hiroi-sora/Umi-OCR/tree/release/1.3.3) `2023.3.19`
<!-- 4.5k★ 撒花~ -->
- 新功能：命令行模式。
- 新功能：识图完成的通知悬浮窗。
- 新功能：自动清理引擎内存。
- 修复了一些BUG，优化了一些UI表现。

##### [v1.3.2](https://github.com/hiroi-sora/Umi-OCR/tree/release/1.3.2) `2022.12.1`
<!-- 3k★ 撒花~ -->
- 新功能：创建开机启动项时，可选`不显示主窗口`。
- 新功能：OCR结果输出到每个图片同名的单独txt文件。
- 新功能：增加独立的设置语言窗口，可在多处点开，便于切换语言。
- 新功能：合并段落添加`合并自然段-西文模式`，可在英文段落换行时补充空格。
- 新功能：快捷识图可选`自动清空面板`，只显示本次识别结果，且隐藏时间信息。
- 修复了一些BUG。

##### [v1.3.1](https://github.com/hiroi-sora/Umi-OCR/tree/release/1.3.1) `2022.11.4`
<!-- 2k★ 撒花~ -->
- 修Bug：快捷键模块重写，引入pynput库，舍弃keyboard库，解决几率失效、录制不正确等Bug。
- 新功能：添加开机自启，桌面快捷方式，开始菜单快捷方式。
- 新功能：多开软件时提示。
- 新功能：截图时隐藏窗口。
- 调整UI：使用频率极低的设置项设为隐藏的高级选项。
- 优化：检查引擎组件是否存在。
- 优化：`横排-合并多行-自然段` 优化逻辑，支持0~2全角空格首行缩进。

##### [v1.3.0](https://github.com/hiroi-sora/Umi-OCR/tree/release/1.3.0) `2022.9.29`
- 新功能：框选截屏。
- 新功能：系统托盘图标。
- 新功能：引擎进程常驻。
- 新功能：文本块后处理模块。
- 新功能：自定义主输出栏字体。
- 新功能：设置窗口弹出模式（保持置顶）。
- 调整UI：自适应Win风格组件。
- 修正了Bug：系统语言兼容性问题 [issue #16](https://github.com/hiroi-sora/Umi-OCR/issues/16) 。
- 修正了Bug：微信图片粘贴问题 [issue #22](https://github.com/hiroi-sora/Umi-OCR/issues/22) 。
- 更新PaddleOCR-json模块至`v1.2.1`，提供剪贴板支持。快捷识图通过剪贴板中转，无需再保存临时文件到硬盘。

##### [v1.2.6](https://github.com/hiroi-sora/Umi-OCR/tree/release/1.2.6) `2022.9.1`
<!-- Takahara Umi酱生日快乐~ -->
- 更新PaddleOCR-json模块至`v1.2.0`，提高识别速度、准确度。
- 调整UI：更方便地用下拉框切换识别语言。
- 调整UI：可以从主窗口任意位置/任意选项卡拖入图片。
- 修正了Bug：提高程序健壮性，增加启动子进程时的更多异常处理情况。
- 修正了Bug：彻底解决了对边缘过窄的图片，识别结果不准确的问题 [issue #7](https://github.com/hiroi-sora/Umi-OCR/issues/7) 。
- 优化适配PP-OCRv3模型，彻底解决了v3版模型比v2慢、不准的问题 [issue #4](https://github.com/hiroi-sora/Umi-OCR/issues/4#issuecomment-1141735773) 。

##### v1.2.5 `2022.7.22`
- 新功能：计划任务。识图完成后执行自动关机等任务。
- 新功能：可选拖入文件夹时递归导入子文件夹中所有图片。
- 调整UI：添加一些配置文件的快捷入口。

##### v1.2.4 `2022.6.4`
- 新功能：可选识别剪贴板图片后自动复制识别的文本。
- 补充功能：快捷键调用剪贴板识图时，若程序窗口被最小化，则恢复前台状态并挪到最前位置。
  
##### v1.2.3 `2022.5.31`
- 新功能：读取剪贴板图片。配置全局快捷键调用该功能。

##### v1.2.2 `2022.4.30`
- 新功能：可选任务完成后自动打开输出文件或目录。

##### v1.2.1 `2022.4.16`
- 更新PaddleOCR-json模块至`v1.1.1`，修正了可能得到错误包围盒的漏洞。

##### v1.2.0 `2022.4.8`
- 可选生成图文链接.md文件，作为索引使用有更佳的观感。
- 修改设置面板的样式，改为滚动面板以容纳更多设置选项。
- 用户修改配置项后可自动保存。

##### v1.1.1 `2022.3.30`
- 修正了Bug：退出忽略区域窗口时，OCR子进程未关闭。

##### v1.1.0 `2022.3.30`
- 新功能：忽略区域窗口以虚线框 展示识别出的文字块。

##### v1.0.0 `2022.3.28`
- “梦开始的地方”