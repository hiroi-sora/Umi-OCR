// 网页链接按钮

import QtQuick 2.15
import QtQuick.Controls 2.15

import "../../Widgets"

Button_ {
    id: btn
    property string url: ""
    // toolTip: url
    height: size_.text + size_.spacing * 2
    bgHoverColor_: theme.coverColor1
    
    contentItem: Text_ {
        text: btn.text_
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        color: theme.specialTextColor

        // 手动绘制下划线，减少抖动现象。不使用 font.underline
        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.bottomMargin: -2
            height: 1
            color: theme.specialTextColor
        }
    }

    onClicked: {
        Qt.openUrlExternally(url)
    }
}