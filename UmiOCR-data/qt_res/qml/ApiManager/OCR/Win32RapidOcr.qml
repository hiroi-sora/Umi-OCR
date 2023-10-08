import QtQuick 2.15

QtObject {
    property string optKey: "RapidOCR"

    // 全局配置
    property var globalOptions: {
        "title": qsTr("RapidOCR（本地）"),
        "type": "group",

        "path": {
            "title": qsTr("引擎exe路径"),
            "type": "file",
            "default": "lib/RapidOCR-json/RapidOCR-json.exe",
            "selectExisting": true, // 选择现有
            "selectFolder": false, // 选择文件
            "dialogTitle": qsTr("RapidOCR 引擎exe路径"),
        },
    }

    // 局部配置
    property var localOptions: {
        "title": qsTr("文字识别（RapidOCR）"),
        "type": "group",

        "language": {
            "title": qsTr("语言/模型库"),
            "optionsList": [],
        },
        "angle": {
            "title": qsTr("纠正文本方向"),
            "default": false,
            "toolTip": qsTr("启用方向分类，识别倾斜或倒置的文本。可能降低识别速度。")
        },
    }
}