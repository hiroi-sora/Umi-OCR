![](https://tupian.li/images/2023/04/29/644c8c105339b.png)

<h1 align="center">Umi-OCR.Rapid 文字识别工具</h1>


<div align="center">
<strong>
采用全新RapidOCR引擎，</br>
适用于 Windows7 x64 及以上平台
</strong>
  <br><br>
  <sub>（当前为测试阶段）</sub>
</div>

<br>

![](https://tupian.li/images/2023/04/29/644c8e1bb01d0.png)

## 版本说明

从诞生之初，**Umi-OCR** 就采用基于 [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) 的离线识别引擎`PaddleOCR-json`。它在同类项目中具有较好的速度和准确性，但也存在一些祖传的缺陷，如`低版本Windows兼容性欠佳`、`内存占用过大`、`打包体积偏大`等。

现在， **Umi-OCR.Rapid** 正努力适配一个基于 [RapidOCR](https://github.com/RapidAI/RapidOCR) 的全新识别引擎`RapidOCR-json`。Rapid能有效的解决上述陈年旧疾。

> RapidOCR是一个开源项目，它**实际上是PaddleOCR的一个第三方改进版本**。本项目采用其中的 C++ [RapidOcrOnnx](https://github.com/RapidAI/RapidOcrOnnx) 库，封装成 [RapidOCR-json](https://github.com/hiroi-sora/RapidOCR-json) 。

##### Rapid的优势：

- 支持Win7。
- 不依赖AVX指令集，支持凌动、安腾、赛扬、奔腾等缺乏AVX指令集的处理器。
- 打包体积非常小。一个exe内嵌所有静态库，引擎本体仅16MB。（原Paddle引擎附带opencv_world、mklml等运行库，展开后需要300+MB空间）。
- 内存占用非常低。长时间运行后，内存占用峰值稳定在500MB左右。（Paddle引擎启用mkldnn后会逐渐增长到2GB，不启用mkl也需500MB以上）。
- 启动和初始化速度快。

##### Rapid的弱项：

- 识别速度相对较慢。Rapid不支持使用mkldnn数学库加速CPU推理，所以会比启用mkl的Paddle慢。未来可能会适配GPU版以弥补这个弱项。
- 使用人数较少，稳定性和效果还需时间的检验。

##### Umi-OCR.Rapid版暂未适配的功能：

- 暂不支持切换多国语言，仅支持默认的`简体中文&英文`识别库。以后将慢慢适配。  
  （请不要导入多国语言扩展包，或者载入主版本的`Umi-OCR_config.json`配置文件，否则可能引发异常。）

##### 其他绝大部分功能与 Umi-OCR 主版本保持一致：
- 使用方法请参考 [主版本Readme的说明](https://github.com/hiroi-sora/Umi-OCR/tree/release/1.3.4) 。

## 下载

Github下载：[Rapid v1.3.4.alpha](https://github.com/hiroi-sora/Umi-OCR/releases/tag/v1.3.4-rapid-alpha)

蓝奏云下载：[https://hiroi-sora.lanzoul.com/s/umi-ocr-test](https://hiroi-sora.lanzoul.com/s/umi-ocr-test)

## Windows 兼容性

经测试，此版本可在 `Windows 7 x64 旗舰版 SP1` 及 `Win10/11` 正常运行。
理论上，也兼容其他64位Win7及Win8版本。

若启动主程序时报下述错误：
```
无法启动此程序，因为计算机中丢失api-ms-win-crt-runtime-l1-1-0.dll。尝试重新安装程序以解决此问题。
```
请下载并安装VC++（2015或以上版本）64位运行库 `vc_redist.x64.exe` 。[微软官网链接](https://www.microsoft.com/zh-CN/download/details.aspx?id=48145) 

## 更新日志

##### v1.3.4-alpha.1 `2023.4.26`
- 适配 [RapidOCR-json](https://github.com/hiroi-sora/RapidOCR-json) 引擎。


## 感谢

本项目核心引擎组件基于 [RapidAI/RapidOcrOnnx](https://github.com/RapidAI/RapidOcrOnnx)：
> A cross platform OCR Library based on PaddleOCR & OnnxRuntime & OpenVINO.
