// =========================================
// =============== 全局配置项 ===============
// =========================================

import QtQuick 2.15
import "../../Configs"
import "../../ApiManager"

Configs {
    category_: "Global"

    // ========================= 【全局配置项】 =========================

    configDict: {
        "ui": {
            "title": qsTr("界面"),
            "type": "group",

            "theme": {
                "title": qsTr("主题"),
                "optionsList": qmlapp.themeManager.themeList, // 从全局主题管理器中取列表
                "onChanged": (val)=>{
                    qmlapp.themeManager.switchTheme(val)
                },
            },
            "disableEffect": {
                "title": qsTr("禁用美化效果"),
                "default": false,
                "toolTip": qsTr("在低配置机器上，禁用动画、阴影等效果可减少部分资源占用"),
                "onChanged": (flag)=>{
                    qmlapp.themeManager.switchEnabledEffect(!flag)
                },
            },
            "disableExternalNotification": {
                "title": qsTr("禁用外部通知"),
                "default": false,
                "toolTip": qsTr("不再发送窗口外部通知。当应用处于后台时，你可能错过信息。"),
            },
        },
        // OCR接口全局设定
        "ocr": ocrManager.globalOptions
    }

    // ========================= 【全局单例，通过 qmlapp.globalConfigs.xxx 访问】 =========================

    OcrManager { id: ocrManager } // OCR管理器 qmlapp.globalConfigs.ocrManager
    UtilsConfigDicts { id: utilsDicts } // 通用配置项 qmlapp.globalConfigs.utilsDicts

    property alias ocrManager: ocrManager
    property alias utilsDicts: utilsDicts

    Component.onCompleted: {
        console.log("% GlobalConfig 初始化全局配置完毕！")
    }
}