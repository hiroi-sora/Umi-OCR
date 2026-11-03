// ==============================================
// =============== 截图OCR的配置项 ===============
// ==============================================

import QtQuick 2.15
import "../../Configs"

Configs {
    category_: "ScreenshotOCR"
    property bool translationEnabled: false
    property string translationSource: "en"
    property string translationTarget: "zh-CN"
    property string translationProvider: "google"
    signal translationOptionsChanged()
    function languageName(code) {
        if(code === "auto") return qsTr("自动检测")
        for(let i = 0; i < translationLanguages.length; i++) {
            if(translationLanguages[i][0] === code) return translationLanguages[i][1]
        }
        return code
    }
    property var translationLanguages: [
        ["en", qsTr("英语")], ["zh-CN", qsTr("简体中文")],
        ["zh-TW", qsTr("繁体中文")], ["ja", qsTr("日语")],
        ["ko", qsTr("韩语")], ["fr", qsTr("法语")],
        ["de", qsTr("德语")], ["es", qsTr("西班牙语")],
        ["ru", qsTr("俄语")], ["pt", qsTr("葡萄牙语")],
        ["it", qsTr("意大利语")], ["ar", qsTr("阿拉伯语")],
        ["vi", qsTr("越南语")], ["th", qsTr("泰语")]
    ]

    configDict: {
        // OCR参数
        "ocr": qmlapp.globalConfigs.ocrManager.deploy(this, "ocr"), 

        // 后处理
        "tbpu": {
            "title": qsTr("OCR文本后处理"),
            "type": "group",

            "parser": qmlapp.globalConfigs.utilsDicts.getTbpuParser(),
        },

        "translation": {
            "title": qsTr("识别后翻译（联网）"),
            "type": "group",
            "enabled": {
                "title": qsTr("启用翻译"),
                "toolTip": qsTr("开启后将识别文字发送至所选在线翻译服务，在译文页显示结果。"),
                "default": false,
                "onChanged": (value) => { translationEnabled = value; translationOptionsChanged() },
            },
            "source": {
                "title": qsTr("源语言"),
                "default": "en",
                "optionsList": [["auto", qsTr("自动检测")]].concat(translationLanguages),
                "onChanged": (value) => { translationSource = value; translationOptionsChanged() },
            },
            "target": {
                "title": qsTr("目标语言"),
                "default": "zh-CN",
                "optionsList": translationLanguages,
                "onChanged": (value) => { translationTarget = value; translationOptionsChanged() },
            },
            "provider": {
                "title": qsTr("免费翻译服务"),
                "optionsList": [["google", "Google"], ["mymemory", "MyMemory"]],
                "toolTip": qsTr("Google 免费端点需要可访问的网络；MyMemory 有每日免费额度且需指定源语言。"),
                "onChanged": (value) => { translationProvider = value; translationOptionsChanged() },
            },
        },

        "hotkey": {
            "title": qsTr("快捷键"),
            "type": "group",

            "screenshot": {
                "title": qsTr("屏幕截图"),
                "type": "hotkey",
                // 默认热键
                "default": UmiAbout.app.system==="win32" ?
                            "win+alt+c" : "alt+c",
                "eventTitle": "<<screenshot>>", // 触发事件标题
            },
            "paste": {
                "title": qsTr("粘贴图片"),
                "type": "hotkey",
                "default": UmiAbout.app.system==="win32" ?
                            "win+alt+v" : "alt+v",
                "eventTitle": "<<paste>>",
            },
            "reScreenshot": {
                "title": qsTr("重复截图"),
                "toolTip": qsTr("重新截取上一次截图的范围"),
                "type": "hotkey",
                "default": "",
                "eventTitle": "<<reScreenshot>>",
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
