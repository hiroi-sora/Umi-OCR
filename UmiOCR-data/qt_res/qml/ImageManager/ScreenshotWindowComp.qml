// =======================================
// =============== 截图窗口 ===============
// =======================================

import QtQuick 2.15
import QtQuick.Window 2.15
import QtGraphicalEffects 1.15
import "../Widgets"

Window {
    id: win

    property string imgID: "" // 图片id
    property string screenName: "" // 显示器名称
    property var screenRatio: 1 // 屏幕缩放比
    property var screenshotEnd // 关闭函数，外部传入

    // 配置
    property int lineWidth: 1 // 线宽
    property color crossLineColor: "#00f91a" // 十字指示器的颜色
    property color clipBorderColor: "white" // 框选区边框的颜色

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

    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint // 无边框+置顶
    
    Component.onCompleted: {
        image.showImgID(imgID)
        visible = true // 窗口可见
        visibility = Window.Windowed
        raise() // 弹到最前层
        requestActivate() // 激活窗口
    }

    // 截图完毕，成功为true
    function ssEnd(okk) {
        visible = false // 先隐藏窗口
        let argd = {}
        if(okk) { // 成功
            // 乘以屏幕缩放比
            if(screenRatio !== 1) {
                clipX*=screenRatio; clipY*=screenRatio;
                clipW*=screenRatio; clipH*=screenRatio;
            }
            argd = {
                screenName: screenName,
                imgID: imgID, 
                clipX: clipX, 
                clipY: clipY, 
                clipW: clipW, 
                clipH: clipH,
            }
        }
        else {
            argd = {clipX:-1, clipY:-1, clipW:-1, clipH:-1}
        }
        // 向父级回报
        win.screenshotEnd(argd) 
    }

    // 底层，图片
    Image_ {
        id: image
        anchors.fill: parent
    }
    // 深色叠加层
    Rectangle {
        id: darkLayer
        anchors.fill: parent
        color: "#73000000"
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
    // 框选区边框
    Rectangle {
        visible: mouseStatus==1
        x: clipX
        y: clipY
        width: clipW
        height: clipH
        color: "#00000000"
        border.width: lineWidth
        border.color: clipBorderColor
    }
    // 十字指示器， mouseStatus==0 时启用
    Item {
        anchors.fill: parent
        visible: mouseArea.containsMouse && mouseStatus==0
        Rectangle { // 水平
            anchors.left: parent.left
            anchors.right: parent.right
            color: crossLineColor
            height: lineWidth
            y: mouseY-lineWidth
        }
        Rectangle { // 垂直
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            color: crossLineColor
            width: lineWidth
            x: mouseX-lineWidth
        }
    }
    // 鼠标触控层
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton | Qt.RightButton // 捕获左右键
        cursorShape: Qt.CrossCursor // 十字光标
        focus: true // 获取焦点

        // 按下
        onPressed: {
            if (mouse.button === Qt.RightButton) {
                return
            }
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
            if (mouse.button === Qt.RightButton) {
                ssEnd(false)
                return
            }
            if(mouseStatus == 1) {
                ssEnd(true)
            }
        }
    }
}