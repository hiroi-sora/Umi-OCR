// ==========================================================
// =============== 可显示OCR文本的增强Image组件 ===============
// ==========================================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import ".."

Image_ {
    overlayLayer: Item {
        anchors.fill: parent

        Rectangle {
            x: 100
            y: 50
            width: 70
            height: 300
            color: theme.coverColor4

            TextEdit_ {
                id: textEdit
                text: "在这个例子中，globalMouseArea 是一个全局的 MouseArea，它捕获所有的鼠标事件。当鼠标在 m1 中被按下时，它会开始拖动 m1。当鼠标在 m2 中被释放时，它会停止拖动，并输出一条消息。"
                anchors.fill: parent
                readOnly: true // 只读
                font.pixelSize: 10 // 初始：10像素
                // onTextChanged: resetFontSize()
                // 获取当前字体大小下，文字区域与组件区域的面积比例
                function getAreaScale() {
                    if(contentWidth===0 || contentHeight===0)
                        return 0
                    return (width * height) / (contentWidth * contentHeight)
                }
                // 重设字体大小，以适合组件大小
                function resetFontSize() {
                    console.log("================")
                    let s = getAreaScale()
                    font.pixelSize *= Math.sqrt(s)
                    // if(s > 1) font.pixelSize ++
                    // else font.pixelSize --
                    console.log(width, height, contentWidth, contentHeight )
                    console.log(s, font.pixelSize)
                    console.log("================")
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: textEdit.resetFontSize()
                }
            }
        }
        Text_ {
            text: "测试测试"
        }
        
    }
}