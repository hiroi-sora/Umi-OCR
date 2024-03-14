// ===============================================
// =============== Markdown渲染视图 ===============
// ===============================================

import QtQuick 2.15
import QtQuick.Controls 2.15

ScrollView {
    id: mdView
    contentWidth: width // 内容宽度
    clip: true // 溢出隐藏
    property string text: "" // 要显示的文本
    // 内部
    property var regexes: undefined // 正则

    // 初始化
    function init() {
        // 初始化 字符串替换正则
        const replacements = [
            // 双换行
            ["\n\n", "\n\n　  \n\n"],
            // Markdown 链接转 HTML 链接
            ["\\[(.*?)\\]\\((.*?)\\)", `<a href="\$2"><font color="${theme.specialTextColor}">\$1</font></a>`]
        ]
        regexes =  replacements.map(([search, replacement]) => ({
            regex: new RegExp(search, "g"), replacement
        }))
    }
    // 将标准MD格式转化为qml支持渲染的格式
    function getQmlText() {
        let t = text
        // 正则替换
        if(!regexes) init()
        regexes.forEach(({ regex, replacement }) => {
            t = t.replace(regex, replacement)
        })
        return t
    }
    // 外部文本刷新时，更新内部文本
    onTextChanged: {
        textEdit.text = getQmlText()
    }

    TextEdit_ {
        id: textEdit
        text: ""
        width: mdView.width // 与内容宽度相同
        textFormat: TextEdit.MarkdownText // md格式
        readOnly: true // 只读

        // 点击链接 link
        onLinkActivated: {
            const argd = {
                yesText: qsTr("打开网页"),
            }
            const callback = (flag)=>{
                if(flag)
                    Qt.openUrlExternally(link)
            }
            qmlapp.popup.dialog(qsTr("链接"), link, callback, "", argd)
        }
        onLinkHovered: {} // 链接悬停，空事件，自动改变鼠标光标
    }
}