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
        },
        // OCR接口全局设定
        "ocr": ocrManager.globalOptions
    }

    OcrManager { id: ocrManager }
    property alias ocrManager: ocrManager
}