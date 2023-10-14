// ===========================================
// =============== 字体修改面板 ===============
// ===========================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import "../Widgets"

Rectangle {
    id: fRoot
    // visible: false
    color: theme.coverColor4
    property var fontsList: []
    
    // 主要UI文字字体，内容可控，可以用裁切的ttf
    property string fontFamily: ""
    // 数据显示文字字体，内容不可控，用兼容性好的系统字体
    property string dataFontFamily: ""
    // 不可加载的字体
    property var illegalFonts: ["", "Terminal", "System", "Small Fonts", "Script", "Roman", "MS Serif", "MS Sans Serif", "Modern", "Fixedsys"]
    
    Component.onCompleted: {
        // 将此组件的引用传入全局设置
        qmlapp.globalConfigs.fontPanel = this
        fontFamily = qmlapp.globalConfigs.getValue("ui.fontFamily")
        dataFontFamily = qmlapp.globalConfigs.getValue("ui.dataFontFamily")
    }
    
    MouseArea {
        anchors.fill: parent
        onWheel: {} // 拦截滚轮事件
        hoverEnabled: true // 拦截悬停事件
        onClicked: fRoot.visible = false // 单击关闭面板
    }

    Loader {
        id: panelLoader
        asynchronous: true
        sourceComponent: com
        active: fRoot.visible
    }
    Component {
        id: com
        Panel {
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
            parent: fRoot
            anchors.fill: parent
            anchors.margins: size_.line * 2
            color: theme.bgColor
            MouseArea {
                anchors.fill: parent
                onClicked: {}
            }

            DoubleColumnLayout {
                anchors.fill: parent
                initSplitterX: 0.5
                leftItem: Panel {
                    anchors.fill: parent

                    Row {
                        id: leftTop
                        anchors.top: parent.top
                        anchors.right: parent.right
                        anchors.margins: size_.spacing
                        spacing: size_.spacing
                        height: size_.line * 2

                        Text_ {
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            text: qsTr("将字体设置为：")
                        }
                        Text_ {
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: size_.line * 3
                            text: qsTr("界面")
                        }
                        Text_ {
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: size_.line * 3
                            text: qsTr("内容")
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

                        Text_{
                            anchors.centerIn: parent
                            visible: panelLoader.status != Loader.Ready
                            text: qsTr("加载字体中……")
                        }

                        ScrollView {
                            id: leftScroll
                            visible: panelLoader.status == Loader.Ready
                            anchors.fill: parent
                            anchors.margins: size_.spacing
                            clip: true

                            Column {
                                anchors.fill: parent
                                spacing: size_.smallSpacing

                                Repeater {
                                    model: fRoot.fontsList
                                    Rectangle {
                                        height: size_.line * 2
                                        width: leftScroll.width
                                        color: fontMouseArea.containsMouse?theme.coverColor2:"#00000000"

                                        Text_ {
                                            text: modelData
                                            anchors.fill: parent
                                            anchors.leftMargin: size_.spacing
                                            verticalAlignment: Text.AlignVCenter
                                            // font.family: modelData
                                            font.family: index < 50 ? modelData : theme.fontFamily
                                        }
                                        MouseArea {
                                            id: fontMouseArea
                                            anchors.fill: parent
                                            hoverEnabled: true
                                        }
                                        IconButton {
                                            id: btn2
                                            anchors.top: parent.top
                                            anchors.bottom: parent.bottom
                                            anchors.right: parent.right
                                            anchors.margins: size_.smallSpacing
                                            color: theme.specialTextColor
                                            bgColor_: theme.specialBgColor
                                            width: size_.line * 3
                                            borderWidth: 1
                                            borderColor: theme.specialTextColor
                                            icon_: fontFamily===modelData?"yes":""
                                            onClicked: fontFamily=modelData
                                        }
                                        IconButton {
                                            id: btn1
                                            anchors.top: parent.top
                                            anchors.bottom: parent.bottom
                                            anchors.right: btn2.left
                                            anchors.margins: size_.smallSpacing
                                            anchors.rightMargin: size_.spacing
                                            color: theme.specialTextColor
                                            bgColor_: theme.specialBgColor
                                            width: size_.line * 3
                                            borderWidth: 1
                                            borderColor: theme.specialTextColor
                                            icon_: dataFontFamily===modelData?"yes":""
                                            onClicked:  dataFontFamily=modelData
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                rightItem: Panel {
                    anchors.fill: parent

                    Text_ {
                        text: "切换字体功能，开发中…………"
                    }
                }
            }
        }
    }
    
}
