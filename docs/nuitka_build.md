# nuitka 打包方式说明

这是一种测试中的打包方式，旨在提供更好的前端性能。

## nuitka_build.py 一键打包脚本

脚本的主要功能有：

nuitka 生成可执行文件、zipfile制作portable文件、 InnoSetup制作安装文件。如不需要生成zip压缩包，或制作安装包。可以自行注释掉create_portable()、create_portable()对应语句
```
if __name__ == '__main__':
    build()
    create_portable()
    if SYSTEM == 'Windows':
       create_portable()
```

### 说明
nuitka是一个可以将Python代码转换为C++代码并编译为可执行文件或扩展模块的工具。可以明显提高python项目的加载运行速度。Inno Setup 是一个免费的 Windows 安装程序制作软件，十分简单实用的打包小工具。

### 使用步骤
1、安装项目依赖
```
pip install -r requirements.txt
```
2、安装nuitka
```
pip install -U nuitka
```
3、安装Inno Setup
官网下载地址：[https://jrsoftware.org/download.php/is.exe](https://jrsoftware.org/download.php/is.exe)
中文语言包：[https://raw.githubusercontent.com/jrsoftware/issrc/main/Files/Languages/Unofficial/ChineseSimplified.isl](https://raw.githubusercontent.com/jrsoftware/issrc/main/Files/Languages/Unofficial/ChineseSimplified.isl)
请保存语言包到Inno Setup安装目录

![image](https://github.com/hiroi-sora/Umi-OCR/assets/10486408/00c7f0d5-a0b3-4185-904a-c4238b3305f2)

4、执行脚本
```
python nuitka_build.py
```

5、安装

- 生成build目录，包括nuitka编译过程文件目录（main.build）、可执行文件目录（main.release）、Inno Setup安装脚本（.iss）

![image](https://github.com/hiroi-sora/Umi-OCR/assets/10486408/0fc8dd7e-1926-4e14-b35c-5cc4c29b5562)

- 用Inno Setup打开生成的.iss文件，或双击.iss打开。点击Run，生成安装文件

![image](https://github.com/hiroi-sora/Umi-OCR/assets/10486408/6bf46fff-d699-4a20-9397-4762be837aa3)

- release目录包含portable压缩文件以及安装文件

![image](https://github.com/hiroi-sora/Umi-OCR/assets/10486408/be27876e-2f1e-4208-a899-947702a5e7b0)

- 双击安装文件，可以采用安装Umi-OCR到指定位置

![image](https://github.com/hiroi-sora/Umi-OCR/assets/10486408/b67b6fd2-d0d0-4295-b1cb-b1f586d9c38d)

6、卸载
控制面板找到Umi-OCR，卸载即可

![image](https://github.com/hiroi-sora/Umi-OCR/assets/10486408/ac4129be-32ab-42fc-886b-41a0534a5b3e)