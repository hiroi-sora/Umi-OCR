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

    // OCR文本后处理-段落合并
    function getTbpuMerge(d=undefined) {
        return {
            "title": qsTr("段落合并"),
            "default": d,
            "optionsList": [
                ["MergeLine", qsTr("单行")],
                ["MergePara", qsTr("多行-自然段")],
                ["MergeParaCode", qsTr("多行-代码段")],
                ["MergeLineVrl", qsTr("竖排-从右到左")],
                ["MergeLineVlr", qsTr("竖排-从左到右")],
                ["None", qsTr("不做处理")],
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