// ===========================================
// =============== 上下双栏布局 ===============
// ===========================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {

    // ========================= 【可调参数】 =========================

    property QtObject topItem // 上元素
    property QtObject bottomItem // 下元素
    property real hideHeight: 40 // 一个栏小于该值时隐藏
    property real initSplitterY: 0.5 // 分割线初始位置。>1时为像素，0~1为比例。
    property string saveKey: "" // 如果非空，则缓存 hideTB 参数。
    property real margins: size_.spacing // 边缘空白

    // 只读信息
    property int hideTB: 0 // 0为不隐藏，1为隐藏上边，2为隐藏下边

    // ===============================================================
    id: doubleCC
    // 上下元素变化时，挂到容器下
    onTopItemChanged: topItem.parent = topContainer
    onBottomItemChanged: bottomItem.parent = bottomContainer

    Item {
        id: doubleColumn
        anchors.fill: parent
        anchors.margins: parent.margins

        property alias hideHeight: doubleCC.hideHeight
        property alias splitterY: splitter.y // 分割线当前位置
        property bool isInitialized: false // 当前是否初始化完毕
        Component.onCompleted: { // 初始化分割线位置
            if(parent.initSplitterY <= 0)
                parent.initSplitterY = 0.5 // 默认值0.5
            Qt.callLater(() => { // 延迟一个事件循环，再进行位置初始化
                isInitialized = true // 标记初始化完成
                let hideFlag = 0
                if(doubleCC.saveKey) { // 取hide缓存
                    const layoutDict = qmlapp.globalConfigs.getValue("window.doubleLayout")
                    const f = layoutDict[doubleCC.saveKey]
                    if(f !== undefined) hideFlag = f
                }
                toTB(hideFlag)
            })
        }
        property int bottomMax: height - splitter.height // 下边缘位置

        function setHideTB(h) {
            if(doubleCC.hideTB === h) return
            doubleCC.hideTB = h
            // 缓存状态
            if(doubleCC.saveKey) {
                let layoutDict = qmlapp.globalConfigs.getValue("window.doubleLayout")
                layoutDict[doubleCC.saveKey] = doubleCC.hideTB
                qmlapp.globalConfigs.setValue("window.doubleLayout", layoutDict)
            }
        }
        // 检查上下隐藏
        function toHide(isHeightChanged = false){
            if(!isInitialized) return // 防止初始化完成之前自动触发
            if(isHeightChanged && doubleCC.hideTB === 2) { // 总体高改变时下吸附
                splitterY = height - splitter.height
                return
            }
            if(splitterY+splitter.height > (height - hideHeight)){ // 隐藏下边
                topContainer.visible = true
                bottomContainer.visible = false
                setHideTB(2)
                splitterY = height - splitter.height
            }
            else if(splitterY < hideHeight){ // 隐藏上边
                topContainer.visible = false
                bottomContainer.visible = true
                setHideTB(1)
                splitterY = 0
            }
            else{
                topContainer.visible = true
                bottomContainer.visible = true
                setHideTB(0)
            }

        }
        // 去到上下。flag: 0 初始 1 上 2 下
        function toTB(flag) {
            if(flag === 0)
                toInitPosition()
            else if(flag === 1)
                splitterY = hideHeight-1
            else if(flag === 2)
                splitterY = height-splitter.height-hideHeight+1
            toHide()
        }
        // 去到初始位置
        function toInitPosition() {
            if(parent.initSplitterY >= 0 && parent.initSplitterY <= 1)
                splitterY = height * parent.initSplitterY
            else
                splitterY = parent.initSplitterY
        }
        // 拖拽分割线，或者调整整体宽度，都会触发检查隐藏
        onSplitterYChanged: toHide()
        onHeightChanged: toHide(true)

        // 上容器
        Item{
            id: topContainer
            anchors.bottom: splitter.top
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            onVisibleChanged: {
                topItem.parent = visible?topContainer:hideContainer
            }
            // 外框
            Rectangle {
                anchors.fill: parent
                z: 10
                color: "#00000000"
                border.width: 1
                border.color: theme.coverColor4
            }
        }
        // 中间拖动条
        Item{
            id: splitter
            anchors.left: parent.left
            anchors.right: parent.right
            height: 0
            y: 0 // 位置可变换
            z: 1

            // 分割线 拖拽、悬停
            MouseArea {
                id: splitterMouseArea
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.right: parent.right
                // 平常高为分隔栏高度，按下拖拽时高度增加防止鼠标出界
                height: pressed ? doubleCC.height : size_.spacing*2
                hoverEnabled: true // 鼠标悬停时，分割线颜色变深
                cursorShape: Qt.SizeVerCursor // 鼠标指针为双箭头
                // 拖拽
                drag.target: splitter
                drag.axis: Drag.YAxis
                drag.minimumY: 0
                drag.maximumY: doubleColumn.bottomMax
                drag.smoothed: false // 无阈值，一拖就动
            }
            // 分割线 视觉展示
            Rectangle {
                id: splitterShow
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.right: parent.right
                radius: height
                height: size_.spacing
                visible: splitterMouseArea.containsMouse || splitterMouseArea.drag.active || doubleCC.hideTB!==0
                color: splitterMouseArea.pressed ? theme.coverColor4 : theme.coverColor2
            }
        }

        // 下容器
        Item{
            id: bottomContainer
            anchors.top: splitter.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            onVisibleChanged: {
                bottomItem.parent = visible?bottomContainer:hideContainer
            }
            // 外框
            Rectangle {
                anchors.fill: parent
                z: 10
                color: "#00000000"
                border.width: 1
                border.color: theme.coverColor4
            }
        }

        // 隐藏容器
        Item {
            id: hideContainer
            visible: false
            height: Math.max(doubleCC.height, 400)
            anchors.left: parent.left
            anchors.right: parent.right
        }
    }
}