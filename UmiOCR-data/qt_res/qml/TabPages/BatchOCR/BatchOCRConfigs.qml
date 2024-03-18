// ==============================================
// =============== 批量OCR的配置项 ===============
// ==============================================

import QtQuick 2.15
import "../../Configs"

Configs {
    category_: "BatchOCR"
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
                "title": qsTr("忽略区域"),
                "btnsList": [
                    {"text":qsTr("进入设置"), "onClicked": clickIgnoreArea},
                ],
            },
            "ignoreArea": {
                "type": "var",
                "save": false,
            },
        },

        // 任务参数
        "mission": {
            "title": qsTr("批量任务"),
            "type": "group",

            "recurrence": {
                "title": qsTr("递归读取子文件夹"),
                "toolTip": qsTr("导入文件夹时，导入子文件夹中全部图片"),
                "default": false,
            },
            "dirType": {
                "title": qsTr("保存到"),
                "optionsList": [
                    ["source", qsTr("图片原目录")],
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
                "toolTip": qsTr("无需填写拓展名。支持插入以下占位符：\n%date 日期时间\n%name 原文件夹名/文件名\n举例：[OCR]_%name_%date\n生成：[OCR]_我的图片_2023-09-01_12-13.txt\n添加占位符可以避免旧文件被新文件覆盖。"),
                "default": "[OCR]_%name_%date",
                "advanced": true, // 高级选项
            },
            "datetimeFormat": {
                "title": qsTr("日期时间格式"),
                "toolTip": qsTr("文件名中 %date 的日期格式。支持插入以下占位符：\n%Y 年、 %m 月、 %d 日、 %H 小时、 \n%M 分钟、 %S 秒 、 %unix 时间戳 \n举例：%Y年%m月%d日_%H-%M\n生成：2023年09月01日_12-13.txt"),
                "default": "%Y%m%d_%H%M",
                "advanced": true, // 高级选项
            },

            "filesType": {
                "title": qsTr("保存文件类型"),
                "type": "group",
                "enabledFold": true,
                "fold": false,

                "txt": {
                    "title": qsTr("txt 标准格式"),
                    "toolTip": qsTr("含原图片文件名和识别文字"),
                    "default": true,
                },
                "txtPlain": {
                    "title": qsTr("p.txt 纯文字格式"),
                    "toolTip": qsTr("仅输出识别文字，不含图片标题"),
                    "default": false,
                },
                "txtIndividual": {
                    "title": qsTr("txt 单独文件"),
                    "toolTip": qsTr("对每张图片，生成同名txt文件，仅输出识别文字"),
                    "default": false,
                },
                "md": {
                    "title": qsTr("md 图文混排"),
                    "toolTip": qsTr("Markdown图文混排格式，可用Markdown阅读器浏览文件"),
                    "default": false,
                },
                "csv": {
                    "title": qsTr("csv 表格文件(Excel)"),
                    "toolTip": qsTr("将图片信息和识别内容写入csv表格文件。可用Excel打开，另存为xlsx格式。"),
                    "default": false,
                },
                "jsonl": {
                    "title": qsTr("jsonl 原始信息"),
                    "toolTip": qsTr("每行为一条json数据，便于第三方程序读取操作"),
                    "default": false,
                },
            },

            "ingoreBlank": {
                "title": qsTr("输出忽略空白图片"),
                "toolTip": qsTr("若图片没有文字或识别失败，也不会输出错误提示信息"),
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


/*
输出文件类型
    .txt 标准格式
    .txt 纯文本格式
    .txt 多个独立文件
    .jsonl 原始信息
*/