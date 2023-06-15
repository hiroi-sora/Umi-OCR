// =============================================
// =============== 重叠选项卡面板 ===============
// =============================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15

Item {
    clip: true

    // 模型选项卡
    /* 每一项：
    {   "key": 标识,
        "title": 标题,
        "component": 组件 }  */
    property var tabsModel: []
    
    // 上方 选项栏
    Item {
        id: "topContainer"
        
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: theme.textSize * 2

        TabBar {
            id: bar
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            
            
            Repeater {
                model: tabsModel

                TabButton {
                    property string text_: modelData.title
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom

                    contentItem: Text_ {
                        text: parent.text_
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        color: parent.pressed ? theme.coverColor4 : (
                            parent.hovered ? theme.coverColor2 : theme.coverColor0
                        )
                    }
                }
            }
            
            // 内圆角裁切
            layer.enabled: true
            layer.effect: OpacityMask {
                maskSource: Rectangle {
                    radius: theme.btnRadius
                    width: bar.width
                    height: bar.height
                }
            }
        }
    }

    // 下方 选项页
    SwipeView {
        id: swipeView
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: topContainer.bottom
        anchors.bottom: parent.bottom
        anchors.topMargin: theme.spacing
        currentIndex: bar.currentIndex
        interactive: false // 禁止直接滑动视图本身
        
        Repeater {
            model: tabsModel

            Item {
                Component.onCompleted: {
                    if(modelData.component) {
                        modelData.component.parent = this
                    }
                    else {
                        const newObject = Qt.createQmlObject(`
                            import QtQuick 2.0
                            Rectangle {
                                color: "red"
                                anchors.fill: parent
                            }
                            `,this
                        );
                    }
                }
            }
        }
    }
}