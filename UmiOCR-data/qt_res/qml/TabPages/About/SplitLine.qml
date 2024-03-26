// 分割线

import QtQuick 2.15

Item {
    anchors.left: parent.left
    anchors.right: parent.right
    height: size_.line * 2

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        height: 2
        color: theme.coverColor2
    }
}