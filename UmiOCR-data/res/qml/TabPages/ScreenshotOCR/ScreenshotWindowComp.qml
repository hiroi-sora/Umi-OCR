// =======================================
// =============== 截图窗口 ===============
// =======================================

import QtQuick 2.15
import QtQuick.Window 2.15
import QtGraphicalEffects 1.15


Window {
    id: win

    property string imgID: "" // 图片id
    property var onClosed: undefined // 关闭函数，外部传入
    property int crossLineWidth: 2 // 十字指示器的宽度
    property color crossLineColor: "green" // 十字指示器的颜色

    // 鼠标状态， 0 等待 ， 1 拖拽中
    property int mouseStatus: 0
    // status==0时为当前鼠标位置，status==1时为拖拽开始位置
    property int mouseX: -1
    property int mouseY: -1
    // 裁切区域的左上角坐标和宽高
    property int clipX: -1
    property int clipY: -1
    property int clipW: -1
    property int clipH: -1

    visible: true
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint // 无边框+置顶

    // 底层，图片
    Image {
        anchors.fill: parent
        source: "image://pixmapprovider/"+imgID
    }
    // 深色叠加层
    Rectangle {
        id: darkLayer
        anchors.fill: parent
        color: "#44000000"
        // 遮罩，拖拽时扣除框选区域
        layer.enabled: mouseStatus==1
        layer.effect: OpacityMask {
            invert: true // 取反
            maskSource: Item {
                width: darkLayer.width
                height: darkLayer.height
                Rectangle {
                    x: clipX
                    y: clipY
                    width: clipW
                    height: clipH
                }
            }
        }
    }
    // 边框
    Rectangle{
        anchors.fill: parent
        color: "#00000000"
        border.width: 5
        border.color: "red"
    }
    // 十字指示器， mouseStatus==0 时启用
    Item {
        anchors.fill: parent
        visible: mouseArea.containsMouse && mouseStatus==0
        Rectangle { // 水平
            anchors.left: parent.left
            anchors.right: parent.right
            color: crossLineColor
            height: crossLineWidth
            y: mouseY-crossLineWidth
        }
        Rectangle { // 垂直
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            color: crossLineColor
            width: crossLineWidth
            x: mouseX-crossLineWidth
        }
    }
    // 鼠标触控层
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true

        // 按下
        onPressed: {
            if(mouseStatus == 0) {
                mouseStatus = 1
                win.mouseX = mouse.x
                win.mouseY = mouse.y
                win.clipX = mouse.x
                win.clipY = mouse.y
            }
        }
        // 移动
        onPositionChanged: {
            // 正常移动
            if(mouseStatus == 0) {
                win.mouseX = mouse.x
                win.mouseY = mouse.y
            }
            // 拖拽
            else if(mouseStatus == 1) {
                // 右
                if(mouse.x > win.mouseX) {
                    win.clipX = win.mouseX
                    win.clipW = mouse.x - win.mouseX
                    if(win.clipX + win.clipW > win.width) // 防右越界
                        win.clipW = win.width - win.clipX
                }
                // 左
                else {
                    win.clipX = mouse.x
                    win.clipW = win.mouseX - mouse.x
                    if(win.clipX < 0) { // 防左越界
                        win.clipX = 0
                        win.clipW = win.mouseX
                    }
                }
                // 下
                if(mouse.y > win.mouseY) {
                    win.clipY = win.mouseY
                    win.clipH = mouse.y - win.mouseY
                    if(win.clipY + win.clipH > win.height) // 防下越界
                        win.clipH = win.height - win.clipY
                }
                // 上
                else {
                    win.clipY = mouse.y
                    win.clipH = win.mouseY - mouse.y
                    if(win.clipY < 0) { // 防上越界
                        win.clipY = 0
                        win.clipH = win.mouseY
                    }
                }
            }
        }
        // 松开
        onReleased: {
            if(mouseStatus == 1) {
                console.log("结束，", clipX, clipY, clipW, clipH)
                if(typeof win.onClosed === "function")
                    win.onClosed() // 调用关闭函数
            }
        }
    }
}