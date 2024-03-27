<p align="left">
    <a href="README.md">
        中文
    </a>
    <span> • </span>
    <a href="README_ja.md">
        日本語
    </a>
    <span> • </span>
    <span>
        English
    </span>
</p>

<p align="center">
  <a href="https://github.com/hiroi-sora/Umi-OCR">
    <img width="200" height="128" src="https://tupian.li/images/2022/10/27/icon---256.png" alt="Umi-OCR">
  </a>
</p>

<h1 align="center">Umi-OCR</h1>

<p align="center">
  <a href="https://github.com/hiroi-sora/Umi-OCR/releases/latest">
    <img src="https://img.shields.io/github/v/release/hiroi-sora/Umi-OCR?style=flat-square" alt="Umi-OCR">
  </a>
  <a href="License">
    <img src="https://img.shields.io/github/license/hiroi-sora/Umi-OCR?style=flat-square" alt="LICENSE">
  </a>
  <a href="#下载">
    <img src="https://img.shields.io/github/downloads/hiroi-sora/Umi-OCR/total?style=flat-square" alt="forks">
  </a>
  <a href="https://star-history.com/#hiroi-sora/Umi-OCR">
    <img src="https://img.shields.io/github/stars/hiroi-sora/Umi-OCR?style=flat-square" alt="stars">
  </a>
  <a href="https://github.com/hiroi-sora/Umi-OCR/forks">
    <img src="https://img.shields.io/github/forks/hiroi-sora/Umi-OCR?style=flat-square" alt="forks">
  </a>
  <a href="https://hosted.weblate.org/engage/umi-ocr/">
    <img src="https://hosted.weblate.org/widget/umi-ocr/svg-badge.svg" alt="翻译状态">
  </a>
</p>

<div align="center">
  <h3>
    <a href="#Usage:">
      Usage
    </a>
    <span> • </span>
    <a href="#Download Releases:">
      Download Releases
    </a>
    <span> • </span>
    <a href="CHANGE_LOG.md">
      Changelog
    </a>
    <span> • </span>
    <a href="https://github.com/hiroi-sora/Umi-OCR/issues">
      Issue a problem
    </a>
  </h3>
</div>
<br>

<div align="center">
  <strong>Free, Open-source, Batch Offline OCR Software</strong><br>
  <sub>Compatible with Windows7 x64 and above</sub>
</div><br>

- **Free**: All the code of this project is open-source and completely free.
- **Convenient**: Unzip and use, run offline, no need for network.
- **Efficient**: Comes with a highly efficient offline OCR engine. As long as the computer performance is sufficient, it can be faster than online OCR services.
- **Flexible**: Supports customizable interface, and supports multiple calling methods such as command-line and HTTP API.

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ec301b55.png" alt="1-标题-1.png" style="width: 80%;"></p>

![1-标题-2.png](https://tupian.li/images/2023/11/19/6559909fdeeba.png)

## Usage:

- [Screenshot OCR](#Screenshot-OCR)
  - [Paragraph Merge](#Paragraph-Merge) - Recognize different paragraphs and merge correctly
- [Batch OCR](#Batch-OCR)
  - [Ignore Regions](#Ignore-Regions) - exclude the watermarks, headers or footers
- [QR Code](#QR-Code) Support for scanning QR Code or generating QR Code.
- [Batch Documents OCR](#Batch-Documents-OCR) OCR from scanned PDF document and output layered PDF
- [Global settings](#Global-Settings) Add more PP-OCR supported language models!
- [Command line usage](docs/README_CLI.md)
- [HTTP API](docs/README_HTTP.md)
- [Building the Project](#Build-the-Project)

## Using the Source Code:

Developers should read [Building the Project](#Build-the-Project) before proceeding.

## Download Releases:

- **GitHub** https://github.com/hiroi-sora/Umi-OCR/releases/latest
- **Source Forge** https://sourceforge.net/projects/umi-ocr
- **Lanzou (蓝奏云)** https://hiroi-sora.lanzoul.com/s/umi-ocr

## Getting Started

The software release package is available in `.7z` compressed format or as a self-extracting `.7z.exe` package. The self-extracting package can be used to extract files on a computer without compression software installed.

This software does not require installation. After extraction, simply click on `Umi-OCR.exe` to start the program.

If you encounter any problems, please submit an [Issue](https://github.com/hiroi-sora/Umi-OCR/issues) and I will do my best to assist you.

## Interface Language

Umi-OCR supports multiple languages for its interface. When you open the software for the first time, it will automatically switch to the language based on your computer's system settings.

If you need to manually switch languages, please refer to the following figure, `全局设置`→`语言/Language` .

<p align="center"><img src="https://tupian.li/images/2023/11/19/65599c3f9e600.png" alt="1-标题-1.png" style="width: 80%;"></p>

### Help us translate / 帮助我们翻译！

You can participate in translation work online on Weblate:

https://hosted.weblate.org/engage/umi-ocr/

## Tabbed Interface

Umi-OCR v2 is composed of a series of flexible and easy-to-use **tabbed interfaces**. You can open the required tabbed interface according to your preferences.

The top left corner of the tab bar can be used to switch **window always on top**. The top right corner can be used to **lock the tabbed interface** to prevent accidental closure during daily use.

### Screenshot OCR

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ecb4dfb4.png" alt="2-截图-1.png" style="width: 80%;"></p>

**Screenshot OCR**: After opening this page, you can use a keyboard shortcut to capture a screenshot and recognize the text in the image.

- The left-side image preview panel allows you to select and copy text with your mouse.
- The right-side recognition record panel allows you to edit text and select and copy multiple records.
- It also supports copying images from elsewhere and pasting them into Umi-OCR for recognition.

#### Paragraph Merge

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ecc62ac9.png" alt="2-截图-2.png" style="width: 80%;"></p>

About **OCR Text Post-Processing - Paragraph Merge**: This feature can organize the layout and order of OCR results to make the text more suitable for reading and use. The preset schemes are:

- **Single line**: Merge text on the same line, suitable for most scenarios.
- **Multiple lines - natural paragraphs**: Intelligently recognize and merge text belonging to the same paragraph, suitable for most scenarios, as shown in the figure above.
- **Multiple lines - code block**: Try to restore the original indentation and spacing of the text. Suitable for recognizing code snippets or scenes that require retaining spaces.
- **Vertical layout**: Suitable for vertical layout. Needs to be used in conjunction with a model library that also supports vertical layout recognition.

---

### Batch OCR

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ecdc5197.png" alt="3-批量-1.png" style="width: 80%;"></p>

**Batch OCR**: This page supports batch importing local images for recognition.

- The recognized content can be saved in various formats such as txt/jsonl/md/csv(Excel).
- Supports `text post-processing` technology, which can recognize text belonging to the same natural paragraph and merge it. It also supports multiple processing schemes such as code blocks and vertical text.
- There is no limit on the number of images that can be imported for processing at one time, and the software can automatically shut down or sleep after completing the task.

#### Ignore Regions

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ecbc0021.png" alt="3-批量-2.png" style="width: 80%;"></p>

About **OCR Text Post-Processing - Ignore Regions**: This is a special function in batch OCR that is used to exclude unwanted text in images.

- The ignore region editor can be accessed in the right column of the batch recognition page settings.
- As shown in the example above, there are multiple watermarks/LOGOs at the top and bottom right corner of the image. If these images are recognized in batches, the watermarks will interfere with the recognition results.
- Hold down the right mouse button to draw multiple rectangular boxes. The text inside these areas will be ignored during the task.
- Please try to draw the rectangular boxes larger, completely wrapping all possible positions of the watermark.

---

### Batch Documents OCR

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ecc8bfd4.png" alt="" style="width: 80%;"></p>

---

### QR Code

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ed01f5b2.png" alt="4-二维码-1.png" style="width: 80%;"></p>

**Scan Code**:

- You can capture screenshots, paste, or drag local images to read QR codes and barcodes.
- Supports multiple codes in one image.
- Supports 19 protocols, as follows:

`Aztec`,`Codabar`,`Code128`,`Code39`,`Code93`,`DataBar`,`DataBarExpanded`,`DataMatrix`,`EAN13`,`EAN8`,`ITF`,`LinearCodes`,`MatrixCodes`,`MaxiCode`,`MicroQRCode`,`PDF417`,`QRCode`,`UPCA`,`UPCE`,

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ed001437.png" alt="4-二维码-2.png" style="width: 80%;"></p>

**Generate Code**:

- Enter text to generate a QR code image.
- Supports 19 protocols and parameters such as **error correction level**.

---

### Global Settings

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ed16f4e0.png" alt="5-全局设置-1.png" style="width: 80%;"></p>

**Global Settings**: Here you can adjust the global parameters of the software. Common features include:

- One-click to add shortcuts or set auto-startup.
- Change the interface **language**. Umi supports traditional Chinese, English, Japanese, and other languages.
- Switch interface **themes**. Umi has multiple light/dark themes.
- Adjust the **font size** and **font** of the interface text.
- Switch OCR plugins.
- **Renderer**: The software interface defaults to support GPU-accelerated rendering. If you encounter screen flickering or UI misalignment on your machine, please adjust `Interface and Appearance` → `Renderer`, try switching to different rendering schemes, or turn off hardware acceleration.

---

## API Usage:

- Command-line manual: [README_CLI.md](docs/README_CLI.md)
- HTTP API manual: [README_HTTP.md](docs/README_HTTP.md)

## About Project Structure

### Repositories:

- [Main Repository](https://github.com/hiroi-sora/Umi-OCR) 👈
- [Plugin Repository](https://github.com/hiroi-sora/Umi-OCR_plugins)
- [Win Runtime Library](https://github.com/hiroi-sora/Umi-OCR_runtime_windows)

## Build the Project

### Step 0: (Optional) Fork this project

### Step 1: Download the code

Choose one of the following:

- Pull your forked repository to your local machine
- Download the zip source code package of this repository
- Clone this repository

### Next Steps:

Please go to the following repositories to complete the development/runtime environment deployment for the corresponding platform.

This project also has a very simple one-click packaging script, which can be found in the following repositories.

- [Windows](https://github.com/hiroi-sora/Umi-OCR_runtime_windows)
- Cross-platform support is under development.

## [CHANGE LOG](CHANGE_LOG.md)
