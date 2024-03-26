// 网页链接按钮

import QtQuick 2.15
import QtQuick.Controls 2.15

import "../../Widgets"

Button_ {
    property string url: ""
    textColor_: theme.specialTextColor
    toolTip: url
    height: size_.text + size_.spacing * 2

    onClicked: {
        Qt.openUrlExternally(url)
    }
}