// =============================================
// =============== 参数项组件基类 ===============
// =============================================

import QtQuick 2.15
// import QtQuick.Controls 2.15
import "../Widgets"

Item {
    property string title: "" // 标题
    anchors.left: parent.left
    anchors.right: parent.right
    height: theme.textSize + theme.spacing

    Text_ {
        text: title
        anchors.left: parent.left
        anchors.leftMargin: theme.smallSpacing
        anchors.verticalCenter: parent.verticalCenter
    }
    Rectangle {
        id: bgRectangle
        visible: false
        anchors.fill: parent
        color: theme.coverColor1
        radius: theme.btnRadius
    }
    MouseArea { // 鼠标悬停在一行上时，高亮一行
        anchors.fill: parent
        hoverEnabled: true
        onEntered: bgRectangle.visible = true
        onExited: bgRectangle.visible = false
    }
}