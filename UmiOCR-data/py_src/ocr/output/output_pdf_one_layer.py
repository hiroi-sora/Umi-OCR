# 单层纯文本 PDF

from .output_pdf_layered import OutputPdfLayered
import fitz  # PyMuPDF


class OutputPdfOneLayer(OutputPdfLayered):
    def __init__(self, argd):
        super().__init__(argd)
        self.opacity = 1  # 文本不透明

    # 创建空白 PDF
    def _getPDF(self, path):
        source_doc = fitz.open(path)  # 打开原文档
        pdf = fitz.open()  # 创建空白PDF文档对象
        try:
            pdf.set_toc(source_doc.get_toc())  # 复制原始文档的目录
        except Exception as e:
            print(f"[Warning] get_toc: {e}")
        # 复制原始文档的元数据（如作者、标题等）
        meta = source_doc.metadata
        if not meta["producer"]:
            meta["producer"] = "Umi-OCR & PyMuPDF v" + fitz.VersionBind
        if not meta["creator"]:
            meta["creator"] = "Umi-OCR & PyMuPDF PDF converter"
        pdf.set_metadata(meta)
        # 生成空白的每一页
        for page in source_doc:
            rect = page.rect  # 原文档渲染尺寸
            pdf.new_page(width=rect.width, height=rect.height)
        source_doc.close()  # 释放原文档
        return pdf
