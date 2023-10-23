// ==============================================
// =============== 截图OCR的配置项 ===============
// ==============================================

import QtQuick 2.15
import "../../Configs"

Configs {
    category_: "ScreenshotOCR"

    configDict: {

        "hotkey": {
            "title": qsTr("快捷键"),
            "type": "group",

            "screenshot": {
                "title": qsTr("屏幕截图"),
                "type": "hotkey",
                "default": "", // 默认热键
                "eventTitle": "<<qrcode_screenshot>>", // 触发事件标题
            },
            "paste": {
                "title": qsTr("粘贴图片"),
                "type": "hotkey",
                "default": "",
                "eventTitle": "<<qrcode_paste>>",
            },
        },

        "action": {
            "title": qsTr("扫码后的操作"),
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