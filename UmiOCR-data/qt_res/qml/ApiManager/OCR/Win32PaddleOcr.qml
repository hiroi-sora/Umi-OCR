import QtQuick 2.15

QtObject {
    property string optKey: "PaddleOCR"

    // 全局配置
    property var globalOptions: {
        "title": qsTr("PaddleOCR（本地）"),
        "type": "group",

        "path": {
            "title": qsTr("引擎exe路径"),
            "type": "file",
            "default": "lib/PaddleOCR-json/PaddleOCR-json.exe",
            "selectExisting": true, // 选择现有
            "selectFolder": false, // 选择文件
            "dialogTitle": qsTr("PaddleOCR 引擎exe路径"),
        },
        "enable_mkldnn": {
            "title": qsTr("启用MKL-DNN加速"),
            "default": true,
            "toolTip": qsTr("使用MKL-DNN数学库提高神经网络的计算速度。能大幅加快OCR识别速度，但也会增加内存占用。"),
        },
        "ram_max": {
            "title": qsTr("内存占用限制"),
            "default": -1,
            "min": -1,
            "unit": "MB",
            "isInt": true,
            "advanced": true,
            "toolTip": qsTr("值>0时启用。引擎内存占用超过该值时，执行内存清理。"),
        },
        "ram_time": {
            "title": qsTr("内存闲时清理"),
            "default": 30,
            "min": -1,
            "unit": qsTr("秒"),
            "isInt": true,
            "advanced": true,
            "toolTip": qsTr("值>0时启用。引擎空闲时间超过该值时，执行内存清理。"),
        },
    }

    // 局部配置
    property var localOptions: {
        "title": qsTr("文字识别（PaddleOCR）"),
        "type": "group",

        "language": {
            "title": qsTr("语言/模型库"),
            "optionsList": [],
        },
        "cls": {
            "title": qsTr("纠正文本方向"),
            "default": false,
            "toolTip": qsTr("启用方向分类，识别倾斜或倒置的文本。可能降低识别速度。")
        },
        "limit_side_len": {
            "title": qsTr("限制图像边长"),
            "optionsList": [
                [960, "960 "+qsTr("（默认）")],
                [2880, "2880"],
                [4320, "4320"],
                [999999, qsTr("无限制")],
            ],
            "toolTip": qsTr("将边长大于该值的图片进行压缩，可以提高识别速度。可能降低识别精度。"),
            "advanced": true, // 高级选项
        },
    }
}