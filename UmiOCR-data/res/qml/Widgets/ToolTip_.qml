// =========================================
// =============== 悬浮提示窗 ===============
// =========================================

import QtQuick 2.15
import QtQuick.Controls 2.15


ToolTip {
    id: rootToolTip

    delay: 500
    timeout: 0 // 不自动关闭

    contentItem: Text { // 前景文字
        text: rootToolTip.text
        font.family: theme.fontFamily
        font.pixelSize: theme.smallTextSize
        color: theme.textColor
    }

    background: Rectangle { // 背景矩形
        color: theme.bgColor
        border.color: theme.coverColor4
        radius: theme.btnRadius
    }
}
