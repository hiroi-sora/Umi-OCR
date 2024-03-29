// ==============================================
// =============== 批量PDF的配置项 ===============
// ==============================================

import QtQuick 2.15
import "../../Configs"

Configs {
    category_: "BatchPDF"
    signal clickIgnoreArea() // 打开忽略区域

    configDict: {
        // OCR参数
        "ocr": qmlapp.globalConfigs.ocrManager.deploy(this, "ocr"), 

        // 后处理
        "tbpu": {
            "title": qsTr("OCR文本后处理"),
            "type": "group",

            "parser": qmlapp.globalConfigs.utilsDicts.getTbpuParser(),
            "btns": {
                "title": qsTr("忽略区域（点击文档名进入设置）"),
                "btnsList": [],
            },
            "ignoreArea": {
                "type": "var",
                "save": false,
            },
            "ignoreRangeStart": { // 忽略区域范围
                "default": 1,
                "save": false,
            },
            "ignoreRangeEnd": {
                "default": -1,
                "save": false,
            },
        },

        // 文档参数
        "doc": {
            "title": qsTr("文档处理"),
            "type": "group",

            "extractionMode": {
                "title": qsTr("内容提取模式"),
                "toolTip": qsTr("若一页文档既存在图片又存在文本，如何进行处理"),
                "optionsList": [
                    ["mixed", qsTr("混合OCR/原文本")],
                    ["fullPage", qsTr("整页强制OCR")],
                    ["imageOnly", qsTr("仅OCR图片")],
                    ["textOnly", qsTr("仅拷贝原有文本")],
                ],
            },
        },

        // 任务参数
        "mission": {
            "title": qsTr("批量任务"),
            "type": "group",

            "recurrence": {
                "title": qsTr("递归读取子文件夹"),
                "toolTip": qsTr("导入文件夹时，导入子文件夹中全部文档"),
                "default": false,
            },
            "dirType": {
                "title": qsTr("保存到"),
                "optionsList": [
                    ["source", qsTr("文档原目录")],
                    ["specify", qsTr("指定目录")],
                ],
            },
            "dir": {
                "title": qsTr("指定目录"),
                "toolTip": qsTr("必须先指定“保存到指定目录”才生效"),
                "type": "file",
                "selectExisting": true, // 选择现有
                "selectFolder": true, // 选择文件夹
                "dialogTitle": qsTr("OCR结果保存目录"),
            },
            "fileNameFormat": {
                "title": qsTr("文件名格式"),
                "toolTip": qsTr("无需填写拓展名。支持插入以下占位符：\n%date 日期时间\n%name 原文档名\n举例：[OCR]_%name_%date\n生成：[OCR]_文档A_20230901_1213.txt\n添加占位符可以避免旧文件被新文件覆盖。"),
                "default": "[OCR]_%name_%date",
                "advanced": true,
            },
            "datetimeFormat": {
                "title": qsTr("日期时间格式"),
                "toolTip": qsTr("文件名中 %date 的日期格式。支持插入以下占位符：\n%Y 年、 %m 月、 %d 日、 %H 小时、 \n%M 分钟、 %S 秒 、 %unix 时间戳 \n举例：%Y年%m月%d日_%H-%M\n生成：2023年09月01日_12-13.txt"),
                "default": "%Y%m%d_%H%M",
                "advanced": true,
            },

            "filesType": {
                "title": qsTr("保存文件类型"),
                "type": "group",
                "enabledFold": true,
                "fold": false,

                "pdfLayered": {
                    "title": qsTr("layered.pdf 双层可搜索文档"),
                    "toolTip": qsTr("拷贝原文档内容，并叠加一层透明文字，可以搜索和复制"),
                    "default": true,
                },
                "txt": {
                    "title": qsTr("txt 标准格式"),
                    "toolTip": qsTr("含识别文字和页数信息"),
                    "default": false,
                },
                "txtPlain": {
                    "title": qsTr("p.txt 纯文字格式"),
                    "toolTip": qsTr("输出所有识别文字"),
                    "default": false,
                },
                "csv": {
                    "title": qsTr("csv 表格文件(Excel)"),
                    "toolTip": qsTr("将页数信息和识别内容写入csv表格文件。可用Excel打开，另存为xlsx格式。"),
                    "default": false,
                },
                "jsonl": {
                    "title": qsTr("jsonl 原始信息"),
                    "toolTip": qsTr("每行为一条json数据，便于第三方程序读取操作"),
                    "default": false,
                },
            },

            "ingoreBlank": {
                "title": qsTr("忽略空白页"),
                "toolTip": qsTr("若某一页没有文字或识别失败，也不会输出错误提示信息"),
                "default": true,
            },
        },

        // 任务完成后续操作
        "postTaskActions": qmlapp.globalConfigs.utilsDicts.getPostTaskActions(),

        "other": {
            "title": qsTr("其它"),
            "type": "group",
            "simpleNotificationType": qmlapp.globalConfigs.utilsDicts.getSimpleNotificationType()
        },
    }
}