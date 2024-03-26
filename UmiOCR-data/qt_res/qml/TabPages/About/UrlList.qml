// 链接水平列表

import QtQuick 2.15
import QtQuick.Controls 2.15

import ".."
import "../../Widgets"

Flow {
    id: uRoot
    property string title: ""
    property var urlList: [] // {"text", "url"}
    property int textSize: size_.text

    anchors.left: parent.left
    anchors.right: parent.right
    // spacing: size_.spacing
    spacing: 0

    Text_ {
        height: textSize + size_.spacing * 2
        verticalAlignment: Text.AlignVCenter
        text: title + "   • "
        font.pixelSize: textSize
    }
    // Item { height: 1; width: size_.spacing }

    Repeater {
        model: urlList

        UrlButton {
            height: textSize + size_.spacing * 2
            text_:  urlList[index].text
            url: urlList[index].url
            textSize: uRoot.textSize
        }
    }
}