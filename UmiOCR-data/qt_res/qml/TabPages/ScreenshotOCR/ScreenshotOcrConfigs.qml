// ==============================================
// =============== 截图OCR的配置项 ===============
// ==============================================

import QtQuick 2.15
import "../../Configs"

Configs {
    category_: "ScreenshotOCR"

    configDict: {
        // OCR参数
        "ocr": qmlapp.globalConfigs.ocrManager.deploy(this, "ocr"), 

        // 后处理
        "tbpu": {
            "title": qsTr("OCR文本后处理"),
            "type": "group",

            "parser": qmlapp.globalConfigs.utilsDicts.getTbpuParser(),
        },

        "hotkey": {
            "title": qsTr("快捷键"),
            "type": "group",

            "screenshot": {
                "title": qsTr("屏幕截图"),
                "type": "hotkey",
                "default": "win+alt+c", // 默认热键
                "eventTitle": "<<screenshot>>", // 触发事件标题
            },
            "paste": {
                "title": qsTr("粘贴图片"),
                "type": "hotkey",
                "default": "win+alt+v",
                "eventTitle": "<<paste>>",
            },
        },

        "action": {
            "title": qsTr("识图后的操作"),
            "type": "group",

            "copy": {
                "title": qsTr("复制结果"),
                "default": false,
            },
            "popMainWindow": {
                "title": qsTr("弹出主窗口"),
                "toolTip": qsTr("识图后，如果主窗口最小化或处于后台，则弹到前台"),
                "default": true,
            },
        },

        "other": {
            "title": qsTr("其它"),
            "type": "group",

            "simpleNotificationType": qmlapp.globalConfigs.utilsDicts.getSimpleNotificationType()
        },
    }
}