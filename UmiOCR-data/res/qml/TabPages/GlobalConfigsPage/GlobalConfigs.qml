// =========================================
// =============== 全局配置项 ===============
// =========================================

import QtQuick 2.15
import "../../Configs"

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
    }
}