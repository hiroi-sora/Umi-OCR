// =============================================
// =============== 通用的配置字典 ===============
// =============================================

import QtQuick 2.15

QtObject {
    // 任务完成后续操作
    function getPostTaskActions() {
        return {
            "title": qsTr("任务完成后的操作"),
            "type": "group",

            "openFile": {
                "title": qsTr("自动打开文件"),
                "default": false,
            },
            "openFolder": {
                "title": qsTr("自动打开目录"),
                "default": false,
            },
            "system": {
                "title": qsTr("系统"),
                "save": false, // 不保存
                "optionsList": [
                    ["", qsTr("无")],
                    ["shutdown", qsTr("关机")],
                    ["hibernate", qsTr("休眠")],
                ],
            },
        }
    }

    // OCR文本后处理
    function getTbpu() {
        return {
            "title": qsTr("OCR文本后处理"),
            "type": "group",

            "merge": {
                "title": qsTr("段落合并"),
                "optionsList": [
                    ["MergeLineH", qsTr("优化单行")],
                    ["None", qsTr("不做处理")],
                ],
            },
        }
    }
}