// ================================================
// =============== 主题切换的逻辑管理 ===============
// ================================================

import QtQuick 2.15

Item {
    ThemeLight{ id: light }
    ThemeDark{ id: dark }

    Component.onCompleted: {
        console.log("主题管理器初始化完毕")
        theme = light
    }
}