// ===========================================
// =============== 左右双栏布局 ===============
// ===========================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {

    // ========================= 【可调参数】 =========================

    property QtObject leftItem // 左元素
    property QtObject rightItem // 右元素
    property real hideWidth: 80 // 一个栏小于该值时隐藏
    property real initSplitterX: 0.5 // 分割线初始位置。>1时为像素，0~1为比例。

    // 只读信息
    property int hideLR: 0 // 0为不隐藏，1为隐藏左边，2为隐藏右边

    // ===============================================================
    id: doubleCC
    // 左右元素变化时，挂到容器下
    onLeftItemChanged: leftItem.parent = leftContainer
    onRightItemChanged: rightItem.parent = rightContainer

    Item {
        id: doubleColumn
        anchors.fill: parent
        anchors.margins: size_.spacing

        property alias hideWidth: doubleCC.hideWidth
        property alias splitterX: splitter.x // 分割线当前位置
        Component.onCompleted: { // 初始化分割线位置
            if(parent.initSplitterX <= 0)
                parent.initSplitterX = 0.5 // 默认值0.5
            Qt.callLater(toInit) // 延迟一个事件循环，再进行位置初始化
        }
        property int rightMax: width - splitter.width // 右边缘位置

        // 检查左右隐藏
        function toHide(isWidthChanged = false){
            if(isWidthChanged && doubleCC.hideLR === 2) { // 总体宽度改变时右吸附
                splitterX = width - splitter.width
                return
            }
            if(splitterX+splitter.width > (width - hideWidth)){ // 隐藏右边
                leftContainer.visible = true
                rightContainer.visible = false
                doubleCC.hideLR = 2
                splitterX = width - splitter.width
            }
            else if(splitterX < hideWidth){ // 隐藏左边
                leftContainer.visible = false
                rightContainer.visible = true
                doubleCC.hideLR = 1
                splitterX = 0
            }
            else{
                leftContainer.visible = true
                rightContainer.visible = true
                doubleCC.hideLR = 0
            }

        }
        // 去到左右。flag: 0 初始 1 左 2 右
        function toLR(flag) {
            if(flag === 0)
                toInit()
            else if(flag === 1)
                splitterX = hideWidth-1
            else if(flag === 2)
                splitterX = width-splitter.width-hideWidth+1
            toHide()
        }
        // 去到初始位置
        function toInit() {
            if(parent.initSplitterX >= 0 && parent.initSplitterX <= 1)
                splitterX = width * parent.initSplitterX - size_.spacing * 2
            else
                splitterX = parent.initSplitterX
        }
        // 拖拽分割线，或者调整整体宽度，都会触发检查隐藏
        onSplitterXChanged: toHide()
        onWidthChanged: toHide(true)
        // 左容器
        Item{
            id: leftContainer
            anchors.right: splitter.left
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            onVisibleChanged: {
                leftItem.parent = visible?leftContainer:hideContainer
            }
        }

        // 中间拖动条
        Item{
            id: splitter
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.topMargin: size_.spacing
            anchors.bottomMargin: size_.spacing
            width: size_.spacing
            x: 0 // 位置可变换
            z: 1
            property bool isVisible: splitterMouseArea.containsMouse || btnsMouseArea.containsMouse || splitterMouseArea.drag.active || doubleCC.hideLR!==0

            // 分割线 拖拽、悬停
            MouseArea {
                id: splitterMouseArea
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.bottom: btnsMouseArea.top
                // 平常宽度为分隔栏宽度，按下拖拽时宽度增加防止鼠标出界
                width: pressed ? doubleCC.width : parent.width
                hoverEnabled: true // 鼠标悬停时，分割线颜色变深
                cursorShape: Qt.SizeHorCursor // 鼠标指针为双箭头
                // 拖拽
                drag.target: splitter
                drag.axis: Drag.XAxis
                drag.minimumX: 0
                drag.maximumX: doubleColumn.rightMax
                drag.smoothed: false // 无阈值，一拖就动

            }
            // 分割线 视觉展示
            Rectangle {
                id: splitterShow
                visible: splitter.isVisible
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: size_.spacing * 0.3
                radius: width
                color: splitterMouseArea.pressed ? theme.coverColor4 : theme.coverColor2
            }

            // 控制按钮 点击
            MouseArea {
                id: btnsMouseArea
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.bottom
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                width: containsMouse ? size_.line * 2 : parent.width 
                height: size_.line * (doubleCC.hideLR===0 ? 6 : 4)
                property int selectIndex: -1
                onExited: selectIndex = -1
                onPositionChanged: {
                    if(doubleCC.hideLR===0) {
                        if(mouse.y < size_.line * 2)
                            selectIndex = 1
                        else if(mouse.y < size_.line * 4)
                            selectIndex = 2
                        else
                            selectIndex = 0
                    }
                    else {
                        if(mouse.y < size_.line * 2)
                            selectIndex = doubleCC.hideLR===1 ? 2 : 1
                        else
                            selectIndex = 0
                    }
                }
                onClicked: doubleColumn.toLR(selectIndex)

                // 控制按钮 视觉
                Rectangle {
                    color: theme.specialBgColor
                    visible: (splitterMouseArea.containsMouse || btnsMouseArea.containsMouse) && !splitterMouseArea.drag.active
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    width: size_.line * 2
                    radius: size_.panelRadius

                    Column {
                        width: parent.width
                        Icon_ {
                            visible: doubleCC.hideLR!==1
                            width: parent.width
                            height: width
                            color: btnsMouseArea.selectIndex===1 ? theme.textColor:theme.specialTextColor
                            icon: "arrow_to_left"
                        }
                        Icon_ {
                            visible: doubleCC.hideLR!==2
                            width: parent.width
                            height: width
                            color: btnsMouseArea.selectIndex===2 ? theme.textColor:theme.specialTextColor
                            icon: "arrow_to_left"
                            mirror: true
                        }
                        Icon_ {
                            width: parent.width
                            height: width
                            color: btnsMouseArea.selectIndex===0 ? theme.textColor:theme.specialTextColor
                            icon: "arrow_to_center"
                        }
                    }
                }
            }

        }

        // 右容器
        Item{
            id: rightContainer
            anchors.left: splitter.right
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            onVisibleChanged: {
                rightItem.parent = visible?rightContainer:hideContainer
            }
        }

        // 隐藏容器
        Item {
            id: hideContainer
            visible: false
            width: 400
            anchors.top: parent.top
            anchors.bottom: parent.bottom
        }
    }
}