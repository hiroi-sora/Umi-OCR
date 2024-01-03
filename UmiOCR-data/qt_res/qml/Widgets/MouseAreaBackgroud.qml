// ===============================================
// =============== 鼠标区域 悬停背景 ===============
// ===============================================

import QtQuick 2.15

MouseArea {
    property color color_: theme.coverColor1 // 悬停颜色
    property real radius_: size_.btnRadius // 圆角
    property bool hovered: false

    anchors.fill: parent
    hoverEnabled: true
    onEntered: {
        bgRectangle.visible = true
        hovered = true
    }
    onExited: {
        bgRectangle.visible = false
        hovered = false
    }
    // 事件穿透
    onClicked: {
        mouse.accepted = false
    }
    onPressed: {
        mouse.accepted = false
    }
    onReleased: {
        mouse.accepted = false
    }
    Rectangle {
        id: bgRectangle
        visible: false
        anchors.fill: parent
        color: color_
        radius: radius_
    }
}