// ===============================================
// =============== 鼠标区域 悬停背景 ===============
// ===============================================

import QtQuick 2.15

MouseArea {
    property color color_: theme.coverColor1 // 悬停颜色
    property real radius_: theme.btnRadius // 圆角

    anchors.fill: parent
    hoverEnabled: true
    onEntered: bgRectangle.visible = true
    onExited: bgRectangle.visible = false
    Rectangle {
        id: bgRectangle
        visible: false
        anchors.fill: parent
        color: theme.coverColor1
        radius: radius_
    }
}