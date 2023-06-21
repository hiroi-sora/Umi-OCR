// ==============================================
// =============== 标准按钮外观样式 ===============
// ==============================================

import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: btn
    // ========================= 【可调参数】 =========================
    property string text_: ""
    property bool bold_: false
    property color textColor_: theme.textColor

    property color bgColor_: theme.coverColor0
    property color bgPressColor_: theme.coverColor4
    property color bgHoverColor_: theme.coverColor2

    contentItem: Text_ {
        text: btn.text_
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        color: btn.textColor_
        font.bold: btn.bold_
    }

    background: Rectangle {
        anchors.fill: parent
        radius: theme.btnRadius
        color: parent.pressed ? parent.bgPressColor_ : (
            parent.hovered ? parent.bgHoverColor_ : parent.bgColor_
        )
    }
    MouseArea {
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
}