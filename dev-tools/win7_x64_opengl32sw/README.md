# Win7 Supplemental Driver Files

On some Windows 7 systems, such as:

• Early versions of Win7, or older Windows systems
• Incomplete graphics drivers, or older graphics card models (including integrated graphics)
• Certain virtual machine environments

This project may display an error pop-up when launching:

> Failed to create OpenGL context for format QSurfaceFormat(version 2.0, options QFlags\<QSurfaceFormat:FormatOption\>0,depthBufferSize24 redBufferSize -1,greenBufferSize -1,blueBufferSize -1, alphaBufferSize 8, stencilBufferSize 8, samples -1, swapBehavior QSurfaceFormat:DoubleBuffer, swaplnterval 1, colorSpace QSurfaceFormat:DefaultColorSpace, profile QSurfaceFormat:NoProfile).  
> This is most likely caused by not having the necessary graphics drivers installed.  
>  
> Install a driver providing OpenGL 2.0 or higher, or, if this is not possible, make sure the ANGLE Open GL ES 2.0 emulation libraries (libEGL.dll, libGLESv2.dll and d3dcompiler_*.dll) are available in the application executable's directory or in a location listedinPATH.

<p align="center"><img src="https://github.com/hiroi-sora/Umi-OCR_v2/assets/56373419/06705d3b-84fa-4797-a2e4-8d37a6dceda0" alt="" style="width: 80%;"></p>

In such cases, copy the following two files from this directory:

• `opengl32sw.dll`
• `d3dcompiler_47.dll`

into the directory:

• `UmiOCR-data/site-packages/PySide2/`

---

# Win7 补充驱动文件

在一些 Windows7 系统上，如：

- win7 早期版本，或更老的windows系统
- 显卡驱动不全，或显卡（包括核显）型号太老
- 部分虚拟机环境

本项目在启动时会弹出错误弹窗：

> Failed to create OpenGL context for format QSurfaceFormat(version 2.0, options QFlags\<QSurfaceFormat:FormatOption\>0,depthBufferSize24 redBufferSize -1,greenBufferSize -1,blueBufferSize -1, alphaBufferSize 8, stencilBufferSize 8, samples -1, swapBehavior QSurfaceFormat:DoubleBuffer, swaplnterval 1, colorSpace QSurfaceFormat:DefaultColorSpace, profile QSurfaceFormat:NoProfile).  
> This is most likely caused by not having the necessary graphics drivers installed.  
>  
> Install a driver providing OpenGL 2.0 or higher, or, if this is not possible, make sure the ANGLE Open GL ES 2.0 emulation libraries (libEGL.dll, libGLESv2.dll and d3dcompiler_*.dll) are available in the application executable's directory or in a location listedinPATH.

<p align="center"><img src="https://github.com/hiroi-sora/Umi-OCR_v2/assets/56373419/06705d3b-84fa-4797-a2e4-8d37a6dceda0" alt="" style="width: 80%;"></p>

在这种情况下，将本目录下的两个文件：

- `opengl32sw.dll`
- `d3dcompiler_47.dll`

复制到如下目录：

- `UmiOCR-data/site-packages/PySide2/`
