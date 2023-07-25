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
}