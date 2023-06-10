// ===========================================
// =============== 结果面板布局 ===============
// ===========================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../"

// 背景
Rectangle {
    color: "#00000000"

    ScrollView {
        id: textScroll
        anchors.fill: parent
        contentWidth: width // 内容宽度
        clip: true // 溢出隐藏

        ColumnLayout{
            anchors.fill: parent
            spacing: theme.spacing

            ResultTextContainer {}
            ResultTextContainer {}
            ResultTextContainer {}
            ResultTextContainer {}
            ResultTextContainer {}
            ResultTextContainer {}
            ResultTextContainer {}
            ResultTextContainer {}
            ResultTextContainer {}
            ResultTextContainer {}
            ResultTextContainer {}

            Item{height: 1} // 末尾，填充高度
        }

        // Item {
        //     anchors.left: parent.left
        //     anchors.right: parent.right
        //     height: theme.smallTextSize + textPanel.height
            
        //     Text_ {
        //         id: top
        //         anchors.top: parent.top
        //         color: theme.subTextColor
        //         font.pixelSize: theme.smallTextSize
        //         text: "title!!!"
        //     }
        //     Rectangle {
        //         id: textPanel
        //         color: theme.bgColor
        //         anchors.top: top.bottom
        //         anchors.left: parent.left
        //         anchors.right: parent.right
        //         // anchors.bottom: parent.bottom
        //         radius: theme.baseRadius
        //         height: 50
        //     }
        // }

        // TextEdit {
        //     text: "11223333"
        //     width: textScroll.width // 与内容宽度相同
        //     textFormat: TextEdit.MarkdownText // md格式
        //     wrapMode: TextEdit.Wrap // 尽量在单词边界处换行
        //     readOnly: true // 只读
        //     selectByMouse: true // 允许鼠标选择文本
        //     selectByKeyboard: true // 允许键盘选择文本
        //     color: theme.textColor
        //     font.pixelSize: theme.textSize
        //     font.family: theme.fontFamily
        // }
    }
}