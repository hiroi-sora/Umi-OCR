// =========================================
// =============== 水平进度条 ===============
// =========================================

import QtQuick 2.15

Rectangle {
    property real percent: 0 // 百分比，0~1
    property color highlightColor: theme.highlightColor // 高亮颜色
    color: theme.coverColor1 // 背景颜色
    radius: theme.btnRadius
    clip: true
    Rectangle {
        width: percent * parent.width // 宽度动态计算
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        radius: parent.radius
        color: parent.highlightColor
    }
}