// =======================================
// =============== 默认提示 ===============
// =======================================

import QtQuick 2.15

// 提示
Item {
    property string tips: "" // 提示文本
    property var visibleFlag // 只要该变量改变，就永久隐藏该组件
    property bool first: true

    onVisibleFlagChanged: {
        if(first) first = false
        else visible = false
    }

    Text_ {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.margins: size_.spacing
        wrapMode: TextEdit.Wrap
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        text: tips
    }
}