# 1. 命令行调用

直接打开PaddleOcr_json.exe，输入图片路径，回车。任务成功时，输出图片识别信息的json。任务失败时，输出json为：{"error":"异常原因"} 。输出一条信息后，可继续接收路径输入；程序是死循环。

支持输入带空格的路径。

命令行程序仅接受gbk编码输入，而输出是utf-8。命令行模式下，不支持手动输入中文路径，无法识别输入的非英文字符。用python等调用时，将含中文字符串编码为gbk输入管道即可正确识别。

# 2. python调用

引入 PaddleOcr.py，调用 OCR() 函数。或参考该文件自行编写。

# 3. 输出值JSON说明

PaddleOcr_json.exe 将把识别信息以json格式字符串的形式打印到控制台。
正常情况下，输出值为数组，数组中每一项含三个元素：
text：文本内容，字符串。
box：文本包围盒，长度为8的数组，分别为左上角、右上角、右下角、左下角的x、y坐标整数。
score：识别置信度，浮点数。

# 4. 更新模型与配置

#### 项目附带的模型可能较旧，可以重新下载PaddleOCR的最新官方模型。

### 4.1. 下载模型

前往[https://gitee.com/paddlepaddle/PaddleOCR]下载一组推理模型（非训练模型）。【中英文超轻量PP-OCRv2模型】体积小，【中英文通用PP-OCR server模型】体积大、精度高。

注意只能使用v2.x版模型，不能使用github上PaddlePaddle/PaddleOCR的v1.1版。v1版模型每个压缩包内有model和params两个文件，v2版则是三个文件（见下），不能混用。

如果要使用非简中语言，则前往[https://gitee.com/paddlepaddle/PaddleOCR/blob/release/2.4/doc/doc_ch/models_list.md]下载对应的模型和ppocr_keys.txt字典文件。

### 4.2. 放置模型

在项目根目录下创建三个文件夹：cls，det，rec。将下载下来的方向分类器（如ch_ppocr_mobile_v2.0_cls_infer.tar）、检测模型（如ch_PP-OCRv2_det_infer.tar）、识别模型（如ch_PP-OCRv2_rec_infer.tar）压缩包中的inference.xxxxx三个文件分别放到对应文件夹。

打开PaddleOcr_json.exe。若无报错，则模型文件已正确加载。“Active code page: 65001”是正常现象。

### 4.3. （可选）调整配置

[exe名称]_config.txt是全局配置文件，可设置模型位置、识别参数、开启GPU等。[https://gitee.com/paddlepaddle/PaddleOCR/blob/release/2.4/doc/doc_ch/config.md]
如果修改了exe名称，也需要同步修改配置文件名的前缀。

### 4.4. （可选）多语言

配置不同的语言，需要不同的配置文件和识别模型（rec）；而其余两组模型（cls、det）和一堆dll可共用。可通过不同的exe文件名实现读取不同配置文件。
假如已经配置好了简体中文，需要再配置日文识别；可通过以下步骤：
1. 在官网下载日文模型库和字典。
   [https://gitee.com/paddlepaddle/PaddleOCR/blob/release/2.4/doc/doc_ch/models_list.md]
2. 项目根目录下创建文件夹 rec_jp ，将模型放进去。
3. 将字典 japan_dict.txt 放到项目根目录。
4. 复制一份 PaddleOCR_json.exe ，新文件为 PaddleOCR_json_jp.exe
5. 复制一份 PaddleOCR_json_config.txt ，新文件为 PaddleOCR_json_jp_config.txt
6. 在 PaddleOCR_json_jp_config.txt 中的 # rec config 块，修改其下的模型库地址和字典地址：
rec_model_dir  rec_jp
char_list_file japan_dict.txt
