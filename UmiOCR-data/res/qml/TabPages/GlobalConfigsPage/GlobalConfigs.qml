// =========================================
// =============== 全局配置项 ===============
// =========================================

import QtQuick 2.15
import "../../Configs"
import "../../Api"

Configs {
    category_: "Global"

    configDict: {
        "ui": {
            "title": qsTr("界面"),
            "type": "group",

            "theme": {
                "title": qsTr("主题"),
                "optionsList": app.themeManager.themeList, // 从全局主题管理器中取列表
                "onChanged": (val)=>{
                    app.themeManager.switchTheme(val)
                },
            },
            "disableEffect": {
                "title": qsTr("禁用美化效果"),
                "default": false,
                "toolTip": qsTr("在低配置机器上，禁用动画、阴影等效果可减少部分资源占用"),
                "onChanged": (flag)=>{
                    app.themeManager.switchEnabledEffect(!flag)
                },
            },
            "disableExternalNotification": {
                "title": qsTr("禁用外部通知"),
                "default": false,
                "toolTip": qsTr("不再发送窗口外部通知。当应用处于后台时，你可能错过信息。"),
            },
            "qwerweqreqeqwr": {
                "title": qsTr("测试用"),
                "default": false,
                "save": false,
                "onChanged": ()=>{
                    app.popupManager.showSimple("测试标题！", "测试内容112233445566！！！！")
                },
            },
        },
        // OCR接口全局设定
        "ocr": ocrManager.globalOptions
    }

    OcrManager { id: ocrManager } // OCR管理器
    UtilsConfigDicts { id: utilsDicts } // 通用配置项

    property alias ocrManager: ocrManager
    property alias utilsDicts: utilsDicts

    Component.onCompleted: {
        console.log("% GlobalConfig 初始化全局配置完毕！")
    }
}