# 双层可搜索 searchable pdf
# https://github.com/pymupdf/PyMuPDF/discussions/2299

from .output import Output

import os
import fitz  # PyMuPDF


class OutputPdfLayered(Output):
    def __init__(self, argd):
        self.dir = argd["outputDir"]  # 输出路径（文件夹）
        self.originPath = argd["originPath"]  # 原始文件路径
        self.fileName = argd["outputFileName"]  # 文件名
        self.outputPath = f"{self.dir}/{self.fileName}.layered.pdf"  # 输出路径
        self.pdf = None
        self.existentPages = []  # 已处理的页数
        self.isInsertFont = False  # 是否有字体嵌入
        self.opacity = 0  # 文本透明度为0
        try:
            self.font = fitz.Font("cjk")  # 字体
        except Exception as e:
            raise Exception(f"Failed to load cjk font. {e}\n无法加载cjk字体。")
        try:
            self.pdf = self._getPDF(self.originPath)  # 加载pymupdf对象
        except Exception as e:
            raise Exception(
                f"Failed to load doc file. {e}\n无法加载文档。\n{self.originPath}"
            )

    # 获取pdf文档对象，或将其它类型的文档转为PDF对象
    def _getPDF(self, path):
        # https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/examples/convert-document/convert.py
        doc = fitz.open(path)
        if doc.is_pdf:
            return doc
        b = doc.convert_to_pdf()  # 转换为PDF格式的二进制数据
        pdf = fitz.open("pdf", b)  # 创建PDF文档对象
        try:
            pdf.set_toc(doc.get_toc())  # 复制原始文档的目录
        except Exception as e:
            print(f"[Warning] set_toc: {e}")
        # 复制原始文档的元数据（如作者、标题等）
        meta = doc.metadata
        if not meta["producer"]:
            meta["producer"] = "Umi-OCR & PyMuPDF v" + fitz.VersionBind
        if not meta["creator"]:
            meta["creator"] = "Umi-OCR & PyMuPDF PDF converter"
        pdf.set_metadata(meta)
        # 复制原始文档的链接
        for pinput in doc:
            links = pinput.get_links()
            pout = pdf[pinput.number]
            for l in links:
                if l["kind"] == fitz.LINK_NAMED:  # 不处理 named links
                    continue
                pout.insert_link(l)  # 写入新文档
        doc.close()  # 释放原文档
        return pdf

    # 计算填满宽和高的一行字体大小
    def _calculateFontSize(self, text, w, h):
        if h > w:  # 竖排转为横排计算
            w, h = h, w
        fontsize = round(h)  # 字体大小初值，假设为行高
        minSize = 5  # 大小下限
        getLen = lambda text, s: self.font.text_length(text, fontsize=s)
        while getLen(text, fontsize) > w and fontsize >= minSize:
            fontsize -= 1  # 尝试减小字体，直到行宽刚好小于界限
        while getLen(text, fontsize) < w:
            fontsize += 1  # 尝试增大字体，直到行宽刚好超过界限
        while getLen(text, fontsize) > w and fontsize >= minSize:
            fontsize -= 0.1  # 再次减小字体，将精度提升到 0.1
        return fontsize

    def print(self, res):  # 输出图片结果
        if not self.pdf:
            print("[Error] PDF对象未初始化！")
            return
        pno = res["page"] - 1  # 当前页数
        self.existentPages.append(pno)  # 记录已处理的页面
        if not res["code"] == 100:
            return  # 忽略空白

        page = self.pdf[pno]  # 当前页对象
        page.clean_contents()  # 内容流清理、语法更正，减少错误
        protation = page.rotation  # 获取页面旋转角度
        isInsertFont = False  # 当前是否进行过字体注入
        # 插入文本，用shape.insert_text（可编辑）或page.insert_text（不可编辑）
        for tb in res["data"]:
            if "from" in tb and tb["from"] == "text":
                continue  # 跳过直接提取的文本，只写入OCR文本
            if not isInsertFont:  # 页面插入字体
                self.isInsertFont = isInsertFont = True
                page.insert_font(fontname="cjk", fontbuffer=self.font.buffer)
            text = tb["text"]
            box = tb["box"]
            x0, y0 = box[0]
            x2, y2 = box[2]
            w = x2 - x0
            h = y2 - y0
            fontsize = self._calculateFontSize(text, w, h)
            # 插入点的 旋转后的坐标
            point = fitz.Point(x0, y2) * page.derotation_matrix
            page.insert_text(
                point,
                text,
                fontsize,
                fontname="cjk",
                rotate=protation,  # 文本角度设定
                stroke_opacity=self.opacity,  # 描边透明度
                fill_opacity=self.opacity,  # 填充（字体）透明度
            )

    def onEnd(self):  # 结束时保存。
        if not self.pdf:
            return
        # 删除未处理的页数
        for i in range(len(self.pdf) - 1, -1, -1):
            if i not in self.existentPages:
                self.pdf.delete_page(i)
        print(f"保存{len(self.pdf)}页PDF：{self.outputPath}")
        if self.isInsertFont:  # 有任意页面嵌入字体，则构建字体子集
            try:  # 对于部分PDF，如用txt直接打印的，构建字体子集会失败。
                self.pdf.subset_fonts()  # 构建字体子集，减小文件大小。需要 fontTools 库
            except Exception as e:  # TODO: 失败原因？可能文件中实际并没有字体？
                print("[Warning] 构建字体子集失败：", e)
            # 保存：压缩并进行3级垃圾回收。等同 ez_save
            self.save(self.pdf, self.outputPath, deflate=True, garbage=3)
        else:
            # 无嵌入字体，则直接保存，不压缩
            self.save(self.pdf, self.outputPath)

    def save(self, pdf, path, **options):  # 保存并关闭 pdf 对象
        try:
            # 尝试保存到指定路径
            pdf.save(path, **options)
        except Exception as e:
            # 保存失败，尝试保存到 ".temp" 路径
            tempPath = self.outputPath + ".temp"
            try:
                pdf.save(tempPath, **options)
                pdf.close()
            except Exception as e:
                raise Exception(f"[Error] Unable to save PDF to [{tempPath}]: {e}")
            # 已保存到 .temp 并 close 原对象，尝试替换文件
            try:
                if os.path.exists(path):
                    os.remove(path)
                os.rename(tempPath, path)
            except Exception as e:
                raise Exception(
                    f"[Warning] Unable to save PDF: [{path}]. Exception: {e}. Saved to temporary path: [{tempPath}]."
                )
        else:  # 正常结束
            pdf.close()
