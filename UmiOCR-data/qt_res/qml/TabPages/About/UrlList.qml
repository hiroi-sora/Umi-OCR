// 链接水平列表

import QtQuick 2.15
import QtQuick.Controls 2.15

import ".."
import "../../Widgets"

Item {
    id: uRoot
    property string title: ""
    property var urlList: [] // {"text", "url"}
    property int textSize: size_.text

    anchors.left: parent.left
    anchors.right: parent.right
    height: flow.height

    Text_ {
        id: lText
        anchors.left: parent.left
        anchors.top: parent.top
        height: textSize + size_.spacing * 2
        verticalAlignment: Text.AlignVCenter
        text: title + "   • "
        font.pixelSize: textSize
    }

    Flow {
        id: flow
        anchors.left: lText.right
        anchors.right: parent.right
        spacing: 0
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
}