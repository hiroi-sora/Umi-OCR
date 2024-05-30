// ==============================================
// =============== 标准按钮外观样式 ===============
// ==============================================

import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: btn
    // ========================= 【可调参数】 =========================
    property string text_: ""
    property string toolTip: "" // 鼠标悬停提示
    property bool bold_: false
    property int textSize: size_.text
    property color textColor_: theme.textColor

    property color bgColor_: "#00000000"
    property color bgPressColor_: theme.coverColor4
    property color bgHoverColor_: theme.coverColor2

    property int borderWidth: 0
    property color borderColor: theme.coverColor3
    property real radius: size_.btnRadius

    Component.onCompleted: {
        // 如果设定了提示，则加载提示组件
        if(btn.toolTip){
            toolTipLoader.sourceComponent = toolTip
        }
    }

    contentItem: Text_ {
        text: btn.text_
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font.pixelSize: btn.textSize
        color: btn.textColor_
        font.bold: btn.bold_
    }

    background: Rectangle {
        anchors.fill: parent
        radius: btn.radius
        color: parent.pressed ? parent.bgPressColor_ : (
            parent.hovered ? parent.bgHoverColor_ : parent.bgColor_
        )
        border.width: borderWidth
        border.color: borderColor
    }
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        // 穿透
        onPressed: {
            mouse.accepted = false
        }
        onReleased: {
            mouse.accepted = false
        }
    }
    // 提示
    Component {
        id: toolTip
        ToolTip_ {
            visible: btn.hovered
            text: btn.toolTip
        }
    }
    // ToolTip_ 的动态加载器
    Loader {
        id: toolTipLoader
        anchors.fill: parent
    }
}