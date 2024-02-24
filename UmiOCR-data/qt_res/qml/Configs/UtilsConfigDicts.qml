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

    // OCR文本后处理-排版解析
    function getTbpuParser(d=undefined) {
        return {
            "title": qsTr("排版解析方案"),
            "toolTip": qsTr("按什么方式，解析和排序图片中的文字块"),
            "default": d,
            "optionsList": [
                ["multi_para", qsTr("多栏-自然段换行")],
                ["multi_line", qsTr("多栏-总是换行")],
                ["multi_none", qsTr("多栏-无换行")],
                ["single_para", qsTr("单栏-自然段换行")],
                ["single_line", qsTr("单栏-总是换行")],
                ["single_none", qsTr("单栏-无换行")],
                // ["single_code", qsTr("单栏-代码段")], // TODO
                ["none", qsTr("不做处理")],
            ],
        }
    }

    // 通知类型
    function getSimpleNotificationType(flag=false) {
        let optionsList = [
            ["inside", qsTr("优先内部")],
            ["onlyInside", qsTr("只允许内部")],
            ["onlyOutside", qsTr("只允许外部")],
            ["none", qsTr("禁用所有通知")],
        ]
        if(!flag) optionsList.unshift(["default", qsTr("跟随全局设定")])
        return {
            "title": qsTr("通知弹窗类型"),
            "optionsList": optionsList,
            "onChanged": (newVal, oldValal)=>{
                let msg = ""
                if(oldValal!==undefined) {
                    for(let i in optionsList)
                        if(optionsList[i][0]===newVal)
                            msg = optionsList[i][1]
                    qmlapp.popup.simple(qsTr("通知类型已更改"), msg, newVal)
                }
            },
        }
    }
}