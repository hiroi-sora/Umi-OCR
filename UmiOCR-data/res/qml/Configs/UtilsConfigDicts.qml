// =============================================
// =============== 通用的配置字典 ===============
// =============================================

import QtQuick 2.15


QtObject {
    // 计划任务
    function getScheduledTasks() {
        return {
            "title": qsTr("计划任务："),
            "type": "group",

            "openFile": {
                "title": qsTr("完成后打开文件"),
                "default": false,
            },
            "openFolder": {
                "title": qsTr("完成后打开目录"),
                "default": false,
            },
            "extra": {
                "title": qsTr("本次完成后执行："),
                "optionsList": [
                    ["", qsTr("无")],
                    ["default", qsTr("关机")],
                    ["specify", qsTr("休眠")],
                ],
            },
        }
    }
}