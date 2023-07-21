// ==============================================
// =============== 带确认的消息界面 ===============
// ==============================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import "../Widgets"

Rectangle {
    id: msgRoot

    property var onHided: undefined // 关闭函数，外部传入
    function show(title, msg) {
        textTitle.text = title
        textMsg.text = msg
    }

    width: theme.textSize * 20
    height: childrenRect.height+theme.textSize*4
    color: theme.bgColor
    radius: theme.panelRadius
    border.color: theme.coverColor4
    border.width: 2

    Item {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: theme.textSize*2
        
        height: childrenRect.height

        Text_ {
            id: textTitle
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: theme.textSize
            font.pixelSize: theme.largeTextSize
        }
        Text_ {
            id: textMsg
            anchors.top: textTitle.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.topMargin: theme.textSize
            wrapMode: TextEdit.Wrap // 尽量在单词边界处换行
        }
        Item {
            id: itemBottom
            anchors.top: textMsg.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: theme.textSize*2
            Button_ {
                anchors.horizontalCenter: parent.horizontalCenter
                bgColor_: theme.coverColor1
                text_: qsTr("知道了")
                onClicked: {
                    if(typeof onHided === "function")
                        onHided() // 调用关闭函数
                }
            }
        }
    }

}