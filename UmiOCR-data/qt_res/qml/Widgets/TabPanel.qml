// =============================================
// =============== 重叠选项卡面板 ===============
// =============================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15

Item {
    property alias currentIndex: bar.currentIndex // 当前下标
    property int indexChangeNum: 0 // 下标变化次数
    property bool isMenuTop: true  // t时控制菜单在顶部，f时在底部
    property real menuHeight: size_.line * 2 // 菜单栏高度

    onCurrentIndexChanged: indexChangeNum++

    // 模型选项卡
    /* 每一项：
    {   "key": 标识,
        "title": 标题,
        "component": 选项卡组件
        选项卡组件中可有一个属性ctrlBar，指向一个控制栏子组件。这个子组件将会父级移动到选项卡的控制栏。
         }  */
    property var tabsModel: []
    clip: true
    id: tabPanel

    function updateMenuTop() {
        // 菜单在顶部模式
        if(isMenuTop) {
            menuContainer.anchors.top = tabPanel.top
            menuContainer.anchors.bottom = undefined
            menuContainer.height = menuHeight
            swipeView.anchors.top = menuContainer.bottom
            swipeView.anchors.bottom = tabPanel.bottom
            swipeView.anchors.topMargin = size_.smallSpacing
            swipeView.anchors.bottomMargin = 0
        }
        // 菜单在底部模式
        else {
            menuContainer.anchors.top = undefined
            menuContainer.anchors.bottom = tabPanel.bottom
            menuContainer.height = menuHeight
            swipeView.anchors.top = tabPanel.top
            swipeView.anchors.bottom = menuContainer.top
            swipeView.anchors.topMargin = 0
            swipeView.anchors.bottomMargin = size_.smallSpacing
        }

    }
    onIsMenuTopChanged: updateMenuTop()
    Component.onCompleted: updateMenuTop()

    // 下方 选项页
    SwipeView {
        id: swipeView
        anchors.left: parent.left
        anchors.right: parent.right
        currentIndex: bar.currentIndex
        interactive: false // 禁止直接滑动视图本身
        Component.onCompleted: {
            if(!qmlapp.enabledEffect) // 关闭动画
                contentItem.highlightMoveDuration = 0
        }

        Repeater {
            model: tabsModel

            Item {
                visible: SwipeView.isCurrentItem
                Component.onCompleted: {
                    modelData.component.parent = this
                    modelData.component.visible = true
                }
            }
        }
    }

    // 选项栏
    Item {
        id: menuContainer
        anchors.left: parent.left
        anchors.right: parent.right
        // 在 updateMenuTop 中重设高度

        Rectangle { // 背景色
            anchors.fill: parent
            color: theme.bgColor
            Rectangle {
                anchors.fill: parent
                color: theme.coverColor1
            }
        }

        // 左：选项栏
        TabBar {
            id: bar
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            background: Rectangle {
                color: theme.bgColor
            }
            
            Repeater {
                model: tabsModel

                TabButton {
                    property string text_: modelData.title
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    checkable: true
                    width: contentText.contentWidth + size_.line*2

                    contentItem: Text_ {
                        id: contentText
                        text: parent.text_
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        color: parent.checked ? theme.textColor : theme.subTextColor
                        font.bold: parent.checked
                    }
                    background: MouseAreaBackgroud {
                        anchors.fill: parent
                        radius_: 0
                        cursorShape: Qt.PointingHandCursor

                        Rectangle {
                            anchors.fill: parent
                            color: parent.parent.checked ? theme.coverColor3 : theme.coverColor2
                        }
                    }

                    // 选中的动画
                    property bool runAni: false
                    onCheckedChanged: {
                        runAni = checked
                    }
                    SequentialAnimation{ // 串行动画
                        running: qmlapp.enabledEffect && runAni
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
                    radius: size_.btnRadius
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
                if(!qmlapp.enabledEffect) // 关闭动画
                    contentItem.highlightMoveDuration = 0
            }
            
            Repeater {
                model: tabsModel

                Item { // 控制栏子组件父级重定向
                    visible: SwipeView.isCurrentItem
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
}