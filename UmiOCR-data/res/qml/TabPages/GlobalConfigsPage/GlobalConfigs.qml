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
                "optionsList": [
                    ["default", qsTr("浅色")],
                    ["default1", qsTr("深色")],
                ],
            },
        },
    }
}