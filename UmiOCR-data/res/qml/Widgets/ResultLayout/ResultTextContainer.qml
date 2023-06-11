// =======================================
// =============== 结果文本 ===============
// =======================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../"

Item {
    id: resultRoot

    property alias textLeft: textLeft.text
    property alias textRight: textRight.text
    property alias textMain: textMain.text

    implicitHeight: resultTop.height+resultBottom.height+theme.smallSpacing+theme.spacing

    Item {
        id: resultTop
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: theme.smallSpacing
        anchors.rightMargin: theme.smallSpacing
        height: theme.smallTextSize

        // 图片名称
        Text_ {
            id: textLeft
            anchors.left: parent.left
            anchors.right: textRight.left
            anchors.rightMargin: theme.spacing
            color: theme.subTextColor
            font.pixelSize: theme.smallTextSize
            clip: true
            elide: Text.ElideLeft
        }
        // 备用，显示状态
        Text_ {
            id: textRight
            anchors.right: parent.right
            color: theme.subTextColor
            font.pixelSize: theme.smallTextSize
        }
    }

    // 主要文字内容
    Rectangle {
        id: resultBottom
        color: theme.bgColor
        anchors.top: resultTop.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.topMargin: theme.smallSpacing
        radius: theme.baseRadius
        height: textMain.height

        TextEdit {
            id: textMain
            
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: theme.smallSpacing
            anchors.rightMargin: theme.smallSpacing
            wrapMode: TextEdit.Wrap // 尽量在单词边界处换行
            readOnly: true // 只读
            selectByMouse: true // 允许鼠标选择文本
            selectByKeyboard: true // 允许键盘选择文本
            color: theme.textColor
            font.pixelSize: theme.textSize
            font.family: theme.fontFamily
        }
    }
}