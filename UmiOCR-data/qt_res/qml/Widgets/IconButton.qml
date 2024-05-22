// =======================================
// =============== 图标按钮 ===============
// =======================================
// 宽高可外部定义

import QtQuick 2.15

Button_ {
    property string icon_: ""
    property color color: theme.subTextColor
    property real margins: Math.min(height * 0.1, size_.spacing)

    contentItem: Icon_ {
        anchors.fill: parent
        anchors.margins: parent.margins

        icon: icon_
        color: parent.color
    }
}