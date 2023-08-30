// =========================================
// =============== 水平进度条 ===============
// =========================================

import QtQuick 2.15
import QtGraphicalEffects 1.15

Rectangle {
    id: progressBarRoot
    property real percent: 0 // 百分比，0~1
    property color highlightColor: theme.yesColor // 高亮颜色
    color: theme.coverColor1 // 背景颜色
    radius: size_.btnRadius // 整体圆角
    Rectangle {
        width: percent * parent.width // 宽度动态计算
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        radius: parent.radius
        color: parent.highlightColor
    }

    // 内圆角裁切
    layer.enabled: true
    layer.effect: OpacityMask {
        maskSource: Rectangle {
            width: progressBarRoot.width
            height: progressBarRoot.height
            radius: progressBarRoot.radius
        }
    }
}