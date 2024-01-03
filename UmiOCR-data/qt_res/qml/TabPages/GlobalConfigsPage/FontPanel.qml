// ===========================================
// =============== 字体修改面板 ===============
// ===========================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import "../../Widgets"

ModalLayer {
    id: fRoot
    property var fontsList: []
    
    // 主要UI文字字体，内容可控，可以用裁切的ttf
    property string fontFamily: ""
    // 数据显示文字字体，内容不可控，用兼容性好的系统字体
    property string dataFontFamily: ""
    // 不可加载的字体
    property var illegalFonts: ["", "Terminal", "System", "Small Fonts", "Script", "Roman", "MS Serif", "MS Sans Serif", "Modern", "Fixedsys"]
    
    function setFontFamily(f) {
        fontFamily = f
        qmlapp.globalConfigs.setValue("ui.fontFamily", f)
    }
    function setDataFontFamily(f) {
        dataFontFamily = f
        qmlapp.globalConfigs.setValue("ui.dataFontFamily", f)
    }

    Component.onCompleted: {
        // 将此组件的引用传入全局设置
        qmlapp.globalConfigs.fontPanel = this
        fontFamily = qmlapp.globalConfigs.getValue("ui.fontFamily")
        dataFontFamily = qmlapp.globalConfigs.getValue("ui.dataFontFamily")
    }

    contentItem: Item {
        id: content
        anchors.fill: parent
    }
    Loader {
        id: panelLoader
        asynchronous: true
        sourceComponent: com
        active: fRoot.visible
    }
    Component {
        id: com
        DoubleRowLayout {
            parent: content
            anchors.fill: parent
            initSplitterX: 0.5

            Component.onCompleted: {
                // 获取字体列表，过滤出以中文字符开头的字体
                let fList = Qt.fontFamilies()
                let newList = fList.filter(function(str) {
                    return /^[\u4e00-\u9fa5]/.test(str);
                })
                // 补充剩余字体
                for(let i in fList) {
                    if(illegalFonts.includes(fList[i]))
                        continue
                    if(!newList.includes(fList[i]))
                        newList.push(fList[i])
                }
                // 将当前选中的移到最前面
                const i1 = newList.indexOf(dataFontFamily)
                if (i1 > -1) {
                    newList.splice(i1, 1)
                    newList.unshift(dataFontFamily)
                }
                const i2 = newList.indexOf(fontFamily)
                if (i2 > -1 && i2 !== i1) {
                    newList.splice(i2, 1)
                    newList.unshift(fontFamily)
                }
                fRoot.fontsList = newList
            }

            leftItem: Panel {
                anchors.fill: parent
                clip: true

                Row {
                    id: leftTop
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.margins: size_.spacing
                    anchors.topMargin: 0
                    anchors.rightMargin: size_.spacing * 3
                    spacing: size_.spacing
                    height: size_.line * 2

                    // Text_ {
                    //     anchors.top: parent.top
                    //     anchors.bottom: parent.bottom
                    //     verticalAlignment: Text.AlignVCenter
                    //     text: qsTr("设置为：")
                    // }
                    Text_ {
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        width: size_.line * 3
                        text: qsTr("界面")
                    }
                    Text_ {
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        width: size_.line * 3
                        text: qsTr("内容")
                        font.family: theme.dataFontFamily
                    }
                }
                Panel {
                    anchors.top: leftTop.bottom
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.margins: size_.spacing
                    anchors.topMargin: 0
                    color: theme.bgColor

                    TableView {
                        id: leftTable
                        anchors.fill: parent
                        anchors.margins: size_.spacing
                        clip: true
                        model: fRoot.fontsList
                        contentWidth: width // 内容宽度
                        rowSpacing: size_.spacing // 行间隔
                        flickableDirection: Flickable.VerticalFlick // 只允许垂直滚动
                        columnWidthProvider: ()=>leftTable.width

                        delegate: Rectangle {
                            height: size_.line * 2
                            implicitHeight: height
                            width: leftTable.width
                            color: fontMouseArea.containsMouse?theme.coverColor2:"#00000000"

                            Text_ {
                                text: modelData
                                anchors.fill: parent
                                anchors.leftMargin: size_.spacing
                                verticalAlignment: Text.AlignVCenter
                                font.family: modelData
                            }
                            MouseArea {
                                id: fontMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                            }
                            // 右边，内容字体
                            IconButton {
                                id: btn2
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                anchors.right: parent.right
                                anchors.margins: size_.smallSpacing
                                color: theme.yesColor
                                bgColor_: theme.coverColor1
                                width: size_.line * 3
                                borderWidth: 1
                                borderColor: theme.specialTextColor
                                bgHoverColor_: theme.coverColor3
                                icon_: dataFontFamily===modelData?"yes":""
                                onClicked: setDataFontFamily(modelData)
                            }
                            // 左边，界面字体
                            IconButton {
                                id: btn1
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                anchors.right: btn2.left
                                anchors.margins: size_.smallSpacing
                                anchors.rightMargin: size_.spacing
                                color: theme.yesColor
                                bgColor_: theme.coverColor1
                                width: size_.line * 3
                                borderWidth: 1
                                borderColor: theme.specialTextColor
                                bgHoverColor_: theme.coverColor3
                                icon_: fontFamily===modelData?"yes":""
                                onClicked: setFontFamily(modelData)
                            }
                        }
                    }
                }
            }
            rightItem: Panel {
                anchors.fill: parent

                Item {
                    anchors.fill: parent
                    anchors.margins: size_.spacing * 3

                    Column {
                        anchors.fill: parent
                        spacing: size_.line

                        Text_ {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            wrapMode: Text.Wrap
                            font.family: fontFamily
                            text: qsTr("界面字体：\n软件中大部分UI的字体。")
                        }

                        Text_ {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            wrapMode: Text.Wrap
                            font.family: dataFontFamily
                            text: qsTr("内容字体：\n识别结果内容的字体。")
                        }

                    }
                }
            }
        }
    }
    
}
