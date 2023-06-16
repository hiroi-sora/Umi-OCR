// ================================================
// =============== TableView的滚动条 ===============
// ================================================


import QtQuick 2.15

Item {
    property var tableView // 传入表格组件

    anchors.right: parent.right
    anchors.top: tableView.top
    anchors.bottom: tableView.bottom
    width: theme.spacing
    visible: tableView.visibleArea.heightRatio < 1 // 总体可见
    property bool isHover: false
    
    Rectangle {
        id: scrollbar
        visible: false
        radius: theme.smallSpacing
        anchors.horizontalCenter: parent.horizontalCenter
        width: theme.smallSpacing
        color: mouseArea.pressed ? theme.coverColor4 : theme.coverColor2
        property real minHeight: width*2 // 最小高度

        property real originHeight: tableView.visibleArea.heightRatio * parent.height
        y: tableView.visibleArea.yPosition * (parent.height-(originHeight<minHeight?(minHeight-originHeight):0))
        height: Math.max(originHeight, minHeight)
        onYChanged: toShow()
        onHeightChanged: toShow()
    }

    function toShow() {
        scrollbar.visible = true
        timer.running = false
        if(!isHover) {
            toHide()
        }
    }
    function toHide() {
        timer.running = true
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        property real dragStartY: 0
        property real dragStartContentY: 0

        onEntered: {
            isHover = true
            toShow()
        }
        onExited: {
            isHover = false
            toHide()
        }
        onPressed: {
            if(height>0) {
                dragStartY = mouse.y
                let relativeY = mouse.y / height
                relativeY = Math.max(0, Math.min(relativeY, 1));
                let goY = relativeY * (tableView.contentHeight-height)
                tableView.contentY = goY
                dragStartContentY = goY
                console.log("鼠标位置", relativeY)
            }
        }
        // onPositionChanged: {
        //     if(pressed && height>0) {
        //         let relativeMoveY = (mouse.y-dragStartY) / height
        //         let realMoveY = relativeMoveY * tableView.contentHeight
        //         let goY = dragStartContentY + realMoveY
        //         goY = Math.max(0, Math.min(realMoveY, (tableView.contentHeight-height)));
        //         tableView.contentY = goY
        //         console.log("鼠标移动", goY)
        //     }
        // }
    }
    Timer {
        id: timer
        interval: 1000
        running: false

        onTriggered: {
            running=false
            scrollbar.visible = false
        }
    }
}

/*

规则：
鼠标进入滚动条区域，或页面被滚动时，高亮1
鼠标点击/拖拽滚动条区域，高亮2
鼠标离开滚动条区域，或页面停止滚动时，过一段时间，熄灭

*/