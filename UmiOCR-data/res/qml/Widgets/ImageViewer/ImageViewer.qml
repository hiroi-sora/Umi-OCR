// ============================================
// =============== OCR图片浏览器 ===============
// ============================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import "../"

Item {
    // ========================= 【接口】 =========================

    // 设置图片源，展示一张图片
    function setSource(source) {
        showImage.source = source
        imageScaleAddSub(0)
    }

    // 缩放，传入 flag>0 放大， <0 缩小 ，0回归100%
    function imageScaleAddSub(flag, step=0.1) {
        // 计算缩放比例
        if (flag === 0) { // 复原
            imageScale = 1.0
        }
        else if (flag > 0) {  // 放大
            imageScale = (imageScale + step).toFixed(1)
            if(imageScale > 2) imageScale = 2
        }
      
        else {  // 缩小
            imageScale = (imageScale - step).toFixed(1)
            if(imageScale < 0.1) imageScale = 0.1
        }
        // 计算缩放宽高
        const w = showImage.sourceSize.width * imageScale
        const h = showImage.sourceSize.height * imageScale
        // 计算偏移量
        const offsetX = (showImage.width - w) / 2
        const offsetY = (showImage.height - h) / 2
        // 应用缩放和偏移
        showImage.width = w
        showImage.height = h
        flickable.contentX = (w - flickable.width)/2
        flickable.contentY = (h - flickable.height)/2
    }
    
    // ========================= 【布局】 =========================

    property real imageScale: 1.0 // 图片比例

    // 图片区域
    Rectangle {
        id: showImageContainer
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: bottomCtrl.top
        anchors.margins: theme.spacing
        anchors.bottomMargin: 0
        color: theme.bgColor

        // 滑动区域，自动监听左键拖拽
        Flickable {
            id: flickable
            anchors.fill: parent
            contentWidth: showImage.width
            contentHeight: showImage.height
            clip: true
            boundsBehavior: Flickable.DragOverBounds
            
            Image {
                id: showImage
                fillMode: Image.Stretch
            }

            // 滚动条
            ScrollBar.vertical: ScrollBar { }
            ScrollBar.horizontal: ScrollBar { }
        }

        // 监听更多鼠标事件
        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.RightButton
            // 滚轮缩放
            onWheel: {
                if (wheel.angleDelta.y > 0) {
                    imageScaleAddSub(1)  // 放大
                }
                else {
                    imageScaleAddSub(-1)  // 缩小
                }
            }
        }
    }

    // 底部控制栏
    Item {
        id: bottomCtrl
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: theme.spacing
        height: theme.textSize

        Row {
            anchors.fill: parent
            spacing: theme.smallSpacing

            Text_ {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                text: (imageScale*100).toFixed(0) + "%"
            }
        }
    }
}