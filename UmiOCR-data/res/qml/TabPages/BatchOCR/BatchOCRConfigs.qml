// ==============================================
// =============== 批量OCR的配置项 ===============
// ==============================================

import QtQuick 2.15
import "../../Configs"

Configs {
    category_: "BatchOCR"

    UtilsConfigDicts { // 通用配置项
        id: utilsDicts
    }

    configDict: {
        "output": {
            "title": " ",
            "type": "group",

            "directoryType": {
                "title": qsTr("保存到"),
                "optionsList": [
                    ["default", qsTr("图片原目录")],
                    ["specify", qsTr("指定目录")],
                ],
            },
            "directory": {
                "title": qsTr("指定目录"),
                "type": "file",
                "selectExisting": true, // 选择现有
                "selectFolder": true, // 选择文件夹
                "dialogTitle": qsTr("OCR结果保存目录"),
            },

            "filesType": {
                "title": qsTr("保存文件类型："),
                "type": "group",

                "txt": {
                    "title": qsTr(".txt 标准格式"),
                    "default": true,
                },
                "txtPlain": {
                    "title": qsTr(".txt 纯文字"),
                    "default": false,
                },
                "txtSingle": {
                    "title": qsTr(".txt 单独文件"),
                    "default": false,
                },
            },

            "ingoreBlank": {
                "title": qsTr("输出忽略空白图片"),
                "default": false,
            },
            "recurrence": {
                "title": qsTr("递归读取子文件夹"),
                "default": false,
            },

            "scheduledTasks": utilsDicts.getScheduledTasks(), // 计划任务
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