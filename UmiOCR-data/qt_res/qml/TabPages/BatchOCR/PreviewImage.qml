// ===========================================
// =============== 图片预览面板 ===============
// ===========================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import "../../Widgets"
import "../../Widgets/ImageViewer"

ModalLayer {
    id: pRoot
    closeText: ""

    // 展示图片/文本
    function show(path, data, text) {
        visible = true
        imageText.showPath(path)
        if(data) {
            console.log("展示data", data)
            imageText.showTextBoxes(data)
        }
        if(text) {
            textEdit.text = text
        }
        else {
            textEdit.text = ""
        }
    }


    contentItem: DoubleRowLayout {
        anchors.fill: parent
        initSplitterX: 0.7
        leftItem: Panel {
            anchors.fill: parent
            clip: true
            // 顶部栏
            Item {
                id: leftTop
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: size_.smallSpacing
                height: size_.line + size_.smallSpacing
                // 靠右
                Row {
                    id: leftTopR
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.rightMargin: size_.spacing
                    spacing: size_.smallSpacing

                    // 显示文字
                    CheckButton {
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        text_: qsTr("文字")
                        toolTip: qsTr("在图片上叠加显示识别文字\n可在全局设置中设为默认关闭")
                        checked: imageText.showOverlay
                        enabledAnime: true
                        onCheckedChanged: imageText.showOverlay = checked
                    }

                    IconButtonBar {
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        btnList: [
                            {
                                icon: "menu",
                                onClicked: imageText.popupMenu,
                                toolTip: tr("右键菜单"),
                            },
                            {
                                icon: "save",
                                onClicked: imageText.saveImage,
                                toolTip: tr("保存图片"),
                            },
                            {
                                icon: "open_image",
                                onClicked: imageText.openImage,
                                toolTip: tr("用默认应用打开图片"),
                            },
                            {
                                icon: "full_screen",
                                onClicked: imageText.imageFullFit,
                                toolTip: tr("图片大小：适应窗口"),
                            },
                            {
                                icon: "one_to_one",
                                onClicked: imageText.imageScaleAddSub,
                                toolTip: tr("图片大小：实际"),
                            },
                        ]
                    }
                    // 百分比显示
                    Text_ {
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignRight
                        text: (imageText.scale*100).toFixed(0) + "%"
                        color: theme.subTextColor
                        width: size_.line * 2.5
                    }
                }
            }
            // 图片预览区域
            ImageWithText {
                id: imageText
                anchors.top: leftTop.bottom
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: size_.spacing
                anchors.topMargin: size_.smallSpacing
            }
        }
        rightItem: Panel {
            anchors.fill: parent
            Rectangle {
                anchors.fill: parent
                anchors.margins: size_.spacing
                color: theme.bgColor
                border.width: 1
                border.color: theme.coverColor4

                ScrollView {
                    id: textView
                    anchors.fill: parent
                    anchors.leftMargin: size_.spacing
                    anchors.rightMargin: size_.spacing
                    contentWidth: width // 内容宽度
                    clip: true // 溢出隐藏

                    TextEdit_ {
                        id: textEdit
                        width: textView.width
                    }
                }
            }
        }
    }
}
