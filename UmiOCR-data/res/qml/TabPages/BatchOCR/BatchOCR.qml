// ==============================================
// =============== 功能页：批量OCR ===============
// ==============================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import "../../Widgets"

Item {
    anchors.fill: parent

    // 主区域：左右双栏面板。
    DoubleColumnLayout {
        anchors.fill: parent
        initSplitterX: 500
        hideWidth: 50

        // 左面板：控制板+文件表格
        leftItem: Panel{
            anchors.fill: parent

            // 上方控制板
            Item{
                id: ctrlPanel
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: theme.spacing
                height: theme.textSize * 3
                clip: true

                // 右边按钮
                Button_ {
                    id: runBtn
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.right: parent.right
                    width: theme.textSize * 6

                    bgColor_: theme.coverColor1
                    bgHoverColor_: theme.coverColor2
                    text_: "开始任务" // TODO
                }

                // 左上信息
                Item {
                    id: infoContainer
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.right: runBtn.left
                    anchors.rightMargin: theme.smallSpacing
                    height: theme.textSize * 1.3
                    clip: true

                    Text_ {
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        // anchors.rightMargin: theme.smallSpacing
                        
                        text: "25s  33/100  33%"
                        color: theme.subTextColor
                    }
                }

                // 左下进度条
                Item {
                    id: progressContainer
                    anchors.top: infoContainer.bottom
                    anchors.left: parent.left
                    anchors.bottom: parent.bottom
                    anchors.right: runBtn.left
                    anchors.rightMargin: theme.smallSpacing
                    anchors.topMargin: theme.smallSpacing

                    HProgressBar {
                        anchors.fill: parent
                        color: theme.bgColor
                        percent: 0.3
                    }
                }
            }

            // 下方文件表格
            FilesTableView{
                anchors.top: ctrlPanel.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.margins: theme.spacing
                anchors.topMargin: theme.smallSpacing
            }
        }
        // 右面板：文字输出 & 设置
        rightItem: Panel{
            anchors.fill: parent

            Rectangle {
                id: testContainer
                anchors.fill: parent
                anchors.margins: theme.spacing
                color: theme.bgColor

                property string testStr: `测试文本测试文本测试文本`
                    
                ScrollView {
                    id: textScroll
                    anchors.fill: parent
                    anchors.margins: theme.spacing
                    contentWidth: width // 内容宽度
                    clip: true // 溢出隐藏

                        TextEdit {
                        text: testContainer.testStr
                        width: textScroll.width // 与内容宽度相同
                        textFormat: TextEdit.MarkdownText // md格式
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
        }
    }

    // 鼠标拖入图片
    DropArea {
        id: imgDropArea
        anchors.fill: parent;
        onDropped: {
            if(drop.hasUrls){
                let fileList = []
                for(let i in drop.urls){
                    let s = drop.urls[i]
                    if(s.startsWith("file:///"))
                        fileList.push(s.substring(8))
                }
                // TODO
                console.log("拖入文件：",fileList)
            }
        }

        // 背景
        Rectangle {
            id: dropAreaBg
            visible: imgDropArea.containsDrag 
            anchors.fill: parent
            color: theme.coverColor4

            Panel {
                color: theme.bgColor
                anchors.centerIn: parent
                implicitWidth: dragText.width*2
                implicitHeight: dragText.height*2
                
                Text_ {
                    id: dragText
                    anchors.centerIn: parent
                    text: qsTr("松手放入图片")
                }
            }
        }
    }
}