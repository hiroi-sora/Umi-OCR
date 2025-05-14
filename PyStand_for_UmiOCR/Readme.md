# PyStand for UmiOCR

这是为 Umi-OCR 而适配的 PyStand 启动器，功能为启动 Python Embedded 解释器并运行指定PY脚本。源项目为 [skywind3000/PyStand](https://github.com/skywind3000/PyStand) 。

可选32位和64位两种启动器。对应使用的python解释器和包也要换成32/64位。

### 生成解决方案

```cmd
# 创建 build 子目录，用于存储构建过程中生成的临时文件
mkdir build

# 32位：
# 指定构建目录为build，生成器为VS2019，生成32位exe，当前目录为根目录
cmake -B build -G "Visual Studio 16 2019" -A Win32 .

# 64位：
cmake -B build -G "Visual Studio 16 2019" -A x64 .
```

### 编译

```
# 构建生成到 build/Release 目录下
cmake --build build --config Release
```
