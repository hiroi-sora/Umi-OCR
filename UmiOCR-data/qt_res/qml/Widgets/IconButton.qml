// =======================================
// =============== 图标按钮 ===============
// =======================================

import QtQuick 2.15

Button_ {
    property string icon_: ""
    property color color: theme.subTextColor

    contentItem: Icon_ {
        anchors.fill: parent
        anchors.margins: parent.height * 0.1
        
        icon: icon_
        color: parent.color
    }
}