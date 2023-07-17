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
        "component": 选项卡组件
        选项卡组件中可有一个属性ctrlBar，指向一个控制栏子组件。这个子组件将会父级移动到选项卡的控制栏。
         }  */
    property var tabsModel: []
    
    // 上方 选项栏
    Item {
        id: topContainer
        
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: theme.textSize * 2

        // 左：选项栏
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
                    checkable: true
                    width: contentText.contentWidth + theme.textSize*2

                    contentItem: Text_ {
                        id: contentText
                        text: parent.text_
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        color: parent.checked ? theme.textColor : theme.subTextColor
                        font.bold: parent.checked
                    }
                    background: Rectangle {
                        anchors.fill: parent
                        color: theme.bgColor
                        Rectangle {
                            anchors.fill: parent
                            color: parent.checked ? theme.coverColor4 : (
                                parent.hovered ? theme.coverColor3 : theme.coverColor2
                            )
                        }
                    }

                    // 选中的动画
                    property bool runAni: false
                    onCheckedChanged: {
                        runAni = checked
                    }
                    SequentialAnimation{ // 串行动画
                        running: theme.enabledEffect && runAni
                        // 动画1：放大
                        NumberAnimation{
                            target: contentText
                            property: "scale"
                            to: 1.3
                            duration: 80
                            easing.type: Easing.OutCubic
                        }
                        // 动画2：缩小
                        NumberAnimation{
                            target: contentText
                            property: "scale"
                            to: 1
                            duration: 150
                            easing.type: Easing.InCubic
                        }
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
        // 右：每个卡的控制栏
        SwipeView {
            id: ctrlSwipeView
            anchors.left: bar.right
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            clip: true

            currentIndex: bar.currentIndex
            interactive: false // 禁止直接滑动视图本身
            Component.onCompleted:{
                if(!theme.enabledEffect) // 关闭动画
                    contentItem.highlightMoveDuration = 0
            }
            
            Repeater {
                model: tabsModel

                Item { // 控制栏子组件父级重定向
                    Component.onCompleted: {
                        if(modelData.component.ctrlBar) {
                            modelData.component.ctrlBar.parent = this
                            modelData.component.ctrlBar.anchors.fill = this
                        }
                    }
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
        anchors.topMargin: theme.smallSpacing
        currentIndex: bar.currentIndex
        interactive: false // 禁止直接滑动视图本身
        Component.onCompleted:{
            if(!theme.enabledEffect) // 关闭动画
                contentItem.highlightMoveDuration = 0
        }
        
        Repeater {
            model: tabsModel

            Item {
                Component.onCompleted: {
                    modelData.component.parent = this
                    modelData.component.visible = true
                }
            }
        }
    }
}