// ==============================================
// =============== 批量OCR的配置项 ===============
// ==============================================

import QtQuick 2.15
import "../../Configs"

Configs {
    key: "BatchOCR"

    ConfigGroup { key: "output"
        title: qsTr("OCR结果保存")

        ConfigItemOptionsList { key: "directoryType"
            title: qsTr("保存到")
            defaultValue: 0
            optionsList: [qsTr("图片原目录"), qsTr("指定目录")]
        }
        ConfigItem { key: "directory"
            title: qsTr("指定目录")
            defaultValue: ""
        }
        
        ConfigGroup { key: "filesType"
            title: qsTr("保存文件类型")

            ConfigItem { key: "txt"
                title: qsTr(".txt 标准格式")
                defaultValue: true
            }
            ConfigItem { key: "txtPlain"
                title: qsTr(".txt 纯文字")
                defaultValue: false
            }
            ConfigItem { key: "txtSingle"
                title: qsTr(".txt 单独文件")
                defaultValue: false
            }
        }

        ConfigItem { key: "ingoreBlank"
            title: qsTr("忽略空白图片")
            defaultValue: false
        }
    }
}


/*
输出文件类型
    .txt 标准格式
    .txt 纯文本格式
    .txt 多个独立文件
    .jsonl 原始信息


以下是两种通过键值对存放嵌套数据的方案

方案一：
{
    "a": {
        "b": "111",
        "c": "222",
        "d": {
            "e": "333"
        }
    }
}

方案二：
{
    "a/b": "111",
    "a/c": "222"
    "a/d/e": "333"
}

这两种方案有什么区别，各有什么优劣？
*/