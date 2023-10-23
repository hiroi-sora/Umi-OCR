// ==============================================
// =============== 截图OCR的配置项 ===============
// ==============================================

import QtQuick 2.15
import "../../Configs"

Configs {
    category_: "QRcode"

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

        "preprocessing": {
            "title": qsTr("二维码图像预处理"),
            "type": "group",
            "advanced": true,

            "median_filter_size": {
                "title": qsTr("中值滤波"),
                "toolTip": qsTr("对图像进行平滑处理\n>0 时生效。可填1~9的奇数（不允许偶数）"),
                "isInt": true,
                "default": 0,
                "max": 10,
                "min": 0,
            },
            "sharpness_factor": {
                "title": qsTr("锐度增强"),
                "toolTip": qsTr("增加图像的锐度\n>0.1 时生效。可填0.1~10的小数"),
                "isInt": false,
                "default": 0,
                "max": 10,
                "min": 0,
            },
            "contrast_factor": {
                "title": qsTr("对比度增强"),
                "toolTip": qsTr("增加图像的对比度\n>0.1 时生效。可填0.1~10的小数"),
                "isInt": false,
                "default": 0,
                "max": 10,
                "min": 0,
            },
            "grayscale": {
                "title": qsTr("转为灰度"),
                "toolTip": qsTr("将图像像素转为灰度"),
                "default": false,
            },
            "threshold": {
                "title": qsTr("二值化"),
                "toolTip": qsTr("将图像像素转为纯黑和纯白\n启用了灰度，且二值化 >-1 时生效。可填0~255的整数"),
                "isInt": true,
                "default": -1,
                "max": 255,
                "min": -1,
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