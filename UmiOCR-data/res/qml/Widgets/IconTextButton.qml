// ==============================================
// =============== 图标+文字的按钮 ===============
// ==============================================

import QtQuick 2.15

Button_ {
    id: btn
    property string icon_: ""
    property string text_: ""
    property color color: theme.subTextColor
    implicitWidth: btnIcon.width+btnText.width+theme.smallSpacing*1.5

    contentItem: Item {
        anchors.fill: parent
        Icon_ {
            id: btnIcon
            icon: icon_
            height: theme.textSize
            width: theme.textSize
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: theme.smallSpacing * 0.5
            color: btn.color
        }
        Text_ {
            id: btnText
            anchors.left: btnIcon.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: theme.smallSpacing * 0.5
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            text: text_
            color: btn.color
        }
    }
}