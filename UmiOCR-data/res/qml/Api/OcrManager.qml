// ==========================================
// =============== OCR接口管理 ===============
// ==========================================

import QtQuick 2.15

QtObject {

    // ========================= 【配置】 =========================
    
    // 全局配置，如引擎路径、账号密钥等
    property var globalOptions: {
        "title": qsTr("文字识别"),
        "type": "group",

        "api": {
            "title": qsTr("当前接口"),
            "optionsList": [
                ["PaddleOCR", qsTr("PaddleOCR（本地）")],
                ["RapidOCR", qsTr("RapidOCR（本地）")],
            ],
            "onChanged": (key)=>{
                switchApi(key)
            }
        },

        "PaddleOCR": {
            "title": qsTr("PaddleOCR（本地）"),
            "type": "group",

            "dir": {
                "title": qsTr("引擎exe路径"),
                "type": "file",
                "default": "lib/PaddleOCR-json/PaddleOCR-json.exe",
                "selectExisting": true, // 选择现有
                "selectFolder": false, // 选择文件
                "dialogTitle": qsTr("PaddleOCR 引擎exe路径"),
            },
        },
        "RapidOCR": {
            "title": qsTr("RapidOCR（本地）"),
            "type": "group",

            "dir": {
                "title": qsTr("引擎exe路径"),
                "type": "file",
                "default": "lib/RapidOCR-json/RapidOCR-json.exe",
                "selectExisting": true, // 选择现有
                "selectFolder": false, // 选择文件
                "dialogTitle": qsTr("RapidOCR 引擎exe路径"),
            },
        },
    }

    // 单独配置，每个页面的选项可以不同。都必须有 language 语言列表。
    property var pageOptions: {
        "PaddleOCR": {
            "title": qsTr("PaddleOCR 设置"),
            "type": "group",

            "language": {
                "title": qsTr("语言/模型库"),
                "optionsList": [
                    ["default", "简体中文"],
                    ["specify", "English"],
                ],
            },
        },
        "RapidOCR": {
            "title": qsTr("RapidOCR 设置"),
            "type": "group",

            "language": {
                "title": qsTr("语言/模型库"),
                "optionsList": [
                    ["default", "默认"],
                ],
            },
        },
    }

    // ========================= 【外部接口】 =========================

    // 改变API
    function switchApi(apiKey) {
        if(staticDict.apiKey == apiKey || !pageOptions.hasOwnProperty(apiKey))
            return
        staticDict.apiKey = apiKey
        for(let i = deployList.length - 1; i >= 0; i--) { // 倒序遍历
            const p = deployList[i].page
            if(!p.configDict) { // 页面已经不存在了，则从记录列表中删除
                deployList.splice(i, 1);
                continue
            }
            const k = deployList[i].configKey
            p.configDict[k] = pageOptions[staticDict.apiKey] // 刷新页面设置
            p.reload() // 刷新页面UI
        }
    }

    // 部署进一个Configs的配置项里，可动态改变配置页。
    // 传入configs页引用和所在字典键（只能在最外层）
    function deploy(page, configKey) {
        deployList.push({ // 记录已部署页面
            "page": page,
            "configKey": configKey,
        })
        if(staticDict.apiKey === ""){
            return { // apiKey未初始化，先返回空的占位
                "title": " ",
                "type": "group",
            }
        }
        else{ // apiKey已初始化，返回对应配置
            return pageOptions[staticDict.apiKey]
        }
    }

    // ========================= 【内部】 =========================
    property var staticDict: { // 静态变量，不参与动态绑定
        "apiKey": "" // 当前选定的api
    }
    property var deployList: [] // 存放 部署了配置的页面
}