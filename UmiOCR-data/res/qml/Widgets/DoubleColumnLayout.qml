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
    property real hideWidth: 5 // 一个栏小于该值时隐藏
    property real initSplitterX: 0.5 // 分割线初始位置。>1时为像素，0~1为比例。

    // ===============================================================
    id: doubleColumnCon
    // 左右元素变化时，挂到容器下
    onLeftItemChanged: leftItem.parent = leftContainer
    onRightItemChanged: rightItem.parent = rightContainer

    Item {
        id: doubleColumn
        anchors.fill: parent
        anchors.margins: theme.spacing

        property alias hideWidth: doubleColumnCon.hideWidth
        property bool isHideWidth: false // hideWidth触发时为true
        property alias splitterX: splitter.x // 分割线当前位置
        property alias splitterWidth: splitter.width // 分割线宽度
        Component.onCompleted: { // 分割线初始时设为一半
            if(parent.initSplitterX <= 0)
                parent.initSplitterX = 0.5 // 默认值0.5
            if(parent.initSplitterX > 0 && parent.initSplitterX < 1)
                splitterX = width * parent.initSplitterX - theme.spacing * 2
            else
                splitterX = parent.initSplitterX
        }
        property int rightMax: width - splitter.width // 右边缘位置

        // 检查左右隐藏
        function toHide(){
            if(splitterX+splitterWidth > (width - hideWidth)){ // 隐藏右边
                leftContainer.visible = true
                rightContainer.visible = false
                isHideWidth = true
                if(splitterX > rightMax)
                    splitterX = rightMax
            }
            else if(splitterX < hideWidth){ // 隐藏左边
                leftContainer.visible = false
                rightContainer.visible = true
                isHideWidth = true
            }
            else{
                leftContainer.visible = true
                rightContainer.visible = true
                isHideWidth = false
            }

        } // 拖拽分割线，或者调整整体宽度，都会触发检查隐藏
        onSplitterXChanged: toHide()
        onWidthChanged: toHide()
        // 左容器
        Item{
            id: leftContainer
            anchors.right: splitter.left
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
        }

        // 中间拖动条
        Item{
            id: splitter
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.topMargin: theme.spacing
            anchors.bottomMargin: theme.spacing
            width: theme.spacing
            x: 0 // 位置可变换
            property bool isHover: false // 是否鼠标悬停

            // 拖拽、悬停
            MouseArea {
                anchors.fill: parent
                hoverEnabled: true // 鼠标悬停时，分割线颜色变深
                onEntered: parent.isHover = true
                onExited: parent.isHover = false
                cursorShape: Qt.SizeHorCursor // 鼠标指针为双箭头
                // 拖拽
                drag.target: splitter
                drag.axis: Drag.XAxis
                drag.minimumX: 0
                drag.maximumX: doubleColumn.rightMax
            }

            // 视觉展示
            Rectangle{
                id: splitterShow
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: theme.spacing * 0.3
                radius: theme.btnRadius
                color: parent.isHover ? theme.coverColor4 : 
                    (doubleColumn.isHideWidth ? theme.coverColor2 : "#00000000")
            }
        }

        // 右容器
        Item{
            id: rightContainer
            anchors.left: splitter.right
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
        }
    }
}