# 单层纯文本 PDF

from .output_pdf_layered import OutputPdfLayered
import fitz  # PyMuPDF


class OutputPdfOneLayer(OutputPdfLayered):
    def __init__(self, argd):
        super().__init__(argd)
        self.opacity = 1  # 文本不透明
        self.outputPath = f"{self.dir}/{self.fileName}.text.pdf"  # 输出路径

    # 创建空白 PDF
    def _getPDF(self, path):
        source_doc = fitz.open(path)  # 打开原文档
        # 如果已加密，则尝试解密
        if source_doc.is_encrypted and not source_doc.authenticate(self.password):
            raise Exception(
                f'The document is encrypted, and the password "{self.password}" is incorrect.\n文档已加密，输入密码不正确。'
            )
        pdf = fitz.open()  # 创建空白PDF文档对象
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
        # 尝试复制原始文档的目录数据
        try:
            pdf.set_toc(source_doc.get_toc())
        except Exception as e:
            print(f"[Warning] set_toc: {e}")
        source_doc.close()  # 释放原文档
        return pdf
