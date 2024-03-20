// ==============================================
// =============== 截图OCR的配置项 ===============
// ==============================================

import QtQuick 2.15
import "../../Configs"

Configs {
    category_: "QRCode"

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
            "title": qsTr("预处理（一般无需改动）"),
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

        "writeBarcode": {
            "title": qsTr("生成二维码/条形码"),
            "type": "group",

            "format": {
                "title": qsTr("类型"),
                "toolTip": qsTr("默认二维码：")+"QRCode",
                "default": "QRCode",
                "optionsList": [
                    ["Aztec", "Aztec"],
                    ["Codabar", "Codabar"],
                    ["Code128", "Code128"],
                    ["Code39", "Code39"],
                    ["Code93", "Code93"],
                    ["DataBar", "DataBar"],
                    ["DataBarExpanded", "DataBarExpanded"],
                    ["DataMatrix", "DataMatrix"],
                    ["EAN13", "EAN13"],
                    ["EAN8", "EAN8"],
                    ["ITF", "ITF"],
                    ["LinearCodes", "LinearCodes"],
                    ["MatrixCodes", "MatrixCodes"],
                    ["MaxiCode", "MaxiCode"],
                    ["MicroQRCode", "MicroQRCode"],
                    ["PDF417", "PDF417"],
                    ["QRCode", "QRCode"],
                    ["UPCA", "UPCA"],
                    ["UPCE", "UPCE"],
                ],
            },
            "width": {
                "title": qsTr("宽度"),
                "toolTip": qsTr("填0：自动选择"),
                "isInt": true,
                "default": 256,
                "min": 0,
                "unit": qsTr("像素"),
            },
            "height": {
                "title": qsTr("高度"),
                "toolTip": qsTr("填0：自动选择"),
                "isInt": true,
                "default": 256,
                "min": 0,
                "unit": qsTr("像素"),
            },
            "quiet_zone": {
                "title": qsTr("边缘空白"),
                "toolTip": qsTr("填-1：自动选择"),
                "isInt": true,
                "default": -1,
                "min": -1,
                "unit": qsTr("像素"),
            },
            "ec_level": {
                "title": qsTr("纠错等级"),
                "toolTip": qsTr("仅适用于：")+"Aztec, PDF417, QRCode",
                "optionsList": [
                    [-1, qsTr("自动")],
                    [1, "7%"],
                    [0, "15%"],
                    [3, "25%"],
                    [2, "30%"],
                ],
            },
        },

        "other": {
            "title": qsTr("其它"),
            "type": "group",

            "simpleNotificationType": qmlapp.globalConfigs.utilsDicts.getSimpleNotificationType()
        },
    }
}