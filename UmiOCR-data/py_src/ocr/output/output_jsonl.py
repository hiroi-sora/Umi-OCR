# 输出到jsonl文件

from .output import Output

import json


class OutputJsonl(Output):
    def __init__(self, argd):
        self.dir = argd["outputDir"]  # 输出路径（文件夹）
        self.fileName = argd["outputFileName"]  # 文件名
        self.outputPath = f"{self.dir}/{self.fileName}.jsonl"  # 输出路径
        self.ingoreBlank = argd["ingoreBlank"]  # 忽略空白文件
        # 创建输出文件
        try:
            with open(self.outputPath, "w", encoding="utf-8") as f:  # 覆盖创建文件
                pass
        except Exception as e:
            raise Exception(f"Failed to create jsonl file. {e}\n创建jsonl文件失败。")

    def print(self, res):  # 输出图片结果
        # 不忽略空白条目
        with open(self.outputPath, "a", encoding="utf-8") as f:  # 追加写入本地文件
            f.write(json.dumps(res, ensure_ascii=False) + "\n")
