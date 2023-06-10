// =======================================
// =============== 结果文本 ===============
// =======================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import "../"


Item {
    anchors.left: parent.left
    anchors.right: parent.right
    // width: 100
    height: theme.smallTextSize + textPanel.height
    
    Text_ {
        id: top
        anchors.top: parent.top
        color: theme.subTextColor
        font.pixelSize: theme.smallTextSize
        text: "title!!!"
    }
    Rectangle {
        id: textPanel
        color: theme.bgColor
        anchors.top: top.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        // anchors.bottom: parent.bottom
        radius: theme.baseRadius
        height: textEdit.height

            
        TextEdit {
            id: textEdit
            text: "11223333"
            
            anchors.left: parent.left
            anchors.right: parent.right
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