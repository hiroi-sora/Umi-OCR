// ==============================================
// =============== 图标+文字的按钮 ===============
// ==============================================

import QtQuick 2.15

Button_ {
    id: btn
    property string icon_: ""
    property string text_: ""
    property color color: theme.subTextColor
    width: size_.line + size_.smallSpacing * 2 + (text_ ? btnText.width + size_.smallSpacing * 0.5 : 0)
    implicitWidth: width

    contentItem: Item {
        anchors.fill: parent
        Icon_ {
            id: btnIcon
            icon: icon_
            height: size_.line
            width: size_.line
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: size_.smallSpacing
            color: btn.color
        }
        Text_ {
            id: btnText
            anchors.left: btnIcon.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: size_.smallSpacing * 0.5
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            text: text_
            width: text_ ? undefined : 0
            color: btn.color
        }
    }
}