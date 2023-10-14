// ===========================================
// =============== 字体修改面板 ===============
// ===========================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import "../Widgets"

Rectangle {
    id: fontPanelRoot
    visible: false
    color: theme.coverColor4
    property var fontsList: []
    
    Component.onCompleted: {
        // 将此组件的引用传入全局设置
        qmlapp.globalConfigs.fontPanel = this
    }
    
    MouseArea {
        anchors.fill: parent
        onWheel: {} // 拦截滚轮事件
        hoverEnabled: true // 拦截悬停事件
        onClicked: fontPanelRoot.visible = false // 单击关闭面板
    }

    // 动态加载
    property bool load: true
    onVisibleChanged: {
        if (load && visible) {
            load = false
            Qt.callLater(()=>{
                panelLoader.sourceComponent = com
            })
        }
    }
    Loader { id: panelLoader }
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
                    if(!newList.includes(fList[i]))
                        newList.push(fList[i])
                }
                fontPanelRoot.fontsList = newList
            }
            parent: fontPanelRoot
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
                    
                    Panel {
                        anchors.fill: parent
                        anchors.margins: size_.spacing
                        color: theme.bgColor

                        ScrollView {
                            id: scrollView
                            anchors.fill: parent
                            anchors.margins: size_.spacing
                            clip: true

                            Column {
                                anchors.fill: parent
                                spacing: size_.smallSpacing

                                Repeater {
                                    model: fontPanelRoot.fontsList
                                    Rectangle {
                                        height: size_.line * 2
                                        width: scrollView.width
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
