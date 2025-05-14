# 手动下载/更新依赖库

总体步骤：

1. 使用pip下载whl包（但不安装）。

    当前系统中安装任意版本Python和PIP后，使用指令 `pip download --only-binary=:all: --platform win_amd64 --python-version 38 --dest . XXXX` 将库 `XXXX` 下载到 **当前目录** 。

2. 解压whl包，得到一堆目录，放置到 `Umi-OCR/UmiOCR-data/site-packages` 中。
3. 尝试删减无用的文件以缩减体积。

### PyMuPDF （旧称fitz）

用于PDF解析与生成。

当前版本： `1.24.11`，更新时间： `2024-10-04`
（注：最后一个支持cp38的版本）

下载whl包：
```
pip download --only-binary=:all: --platform win_amd64 --python-version 38 --dest . pymupdf
```

删减文件：
- `pymupdf/mupdf-devel`

### fontTools

当前版本： `4.56.0`，更新时间： `2025-02-07`

用于支持 PyMuPDF 的 `subset_fonts()` 接口，为PDF构建字体子集。

下载whl包：
```
pip download --only-binary=:all: --platform win_amd64 --python-version 38 --dest . fonttools
```

删减文件：
- `fonttools-*.data`

### Pillow

当前版本： `10.4.0`，更新时间： `2024-07-01`
（注：最后一个支持cp38的版本）

用于图像处理。

下载whl包：
```
pip download --only-binary=:all: --platform win_amd64 --python-version 38 --dest . pillow
```

### psutil

当前版本： `10.4.0`，更新时间： `2025-02-14`
（注：支持cp37+）

用于获取硬件信息（如CPU内核数）及系统运行信息（如进程编号）。

下载whl包：
```
pip download --only-binary=:all: --platform win_amd64 --python-version 38 --dest . psutil
```

删减文件：
- `psutil/tests`

### pynput

当前版本： `1.8.0`，更新时间： `2025-03-04`
（注：纯代码库）

用于接收键鼠事件，实现快捷键触发。

下载whl包：
```
pip download --only-binary=:all: --platform win_amd64 --python-version 38 --dest . pynput
```

### zxing-cpp

当前版本： `2.3.0`，更新时间： `2025-01-02`

用于二维码解析。

下载whl包：
```
pip download --only-binary=:all: --platform win_amd64 --python-version 38 --dest . zxing-cpp
```

### PySide2

当前版本： `5.15.2.1`，更新时间： `2022-01-04`
（注：对应QT5，可能是最后的稳定版本）

用于搭建UI界面。`shiboken2`也是此库的一部分。

不建议更新。本项目当前提供的是经过手动裁切的最优（仅保留所需功能，体积最小）的 PySide2 。
