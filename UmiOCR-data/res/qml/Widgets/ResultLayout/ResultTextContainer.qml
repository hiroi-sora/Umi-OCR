// =======================================
// =============== 结果文本 ===============
// =======================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../"

Item {
    id: resultRoot

    property string resStatus: "" // 状态， text / noText / error
    property alias textLeft: textLeft.text
    property alias textRight: textRight.text
    property alias textMain: textMain.text
    // 高度适应子组件
    implicitHeight: resultTop.height+resultBottom.height+theme.smallSpacing
    height: resultTop.height+resultBottom.height+theme.smallSpacing
    property var onTextHeightChanged // 当文字输入导致高度改变时，调用的函数

    onHeightChanged: { // 高度改变时，通知父级
        // 必须文本框获得焦点时才触发
        if(textMain.activeFocus && (typeof onTextHeightChanged === "function"))
            onTextHeightChanged()
    }

    // 顶部信息
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
        // 日期时间
        Text_ {
            id: textRight
            anchors.right: parent.right
            color: theme.subTextColor
            font.pixelSize: theme.smallTextSize
        }
    }

    // 下方主要文字内容
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
            readOnly: false // 可编辑
            selectByMouse: true // 允许鼠标选择文本
            selectByKeyboard: true // 允许键盘选择文本
            color: resStatus==="error"? theme.noColor:theme.textColor
            font.pixelSize: theme.textSize
            font.family: theme.fontFamily
        }
    }
}