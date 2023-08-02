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
        showImage.source = source // 设置源
        imageW = showImage.sourceSize.width // 记录图片宽高
        imageH = showImage.sourceSize.height
        imageW2 = imageW*0.5
        imageH2 = imageH*0.5
        imageX = 0 // 中心位置归零
        imageY = 0
        imageScale = Math.min(flickable.width/imageW, flickable.height/imageH)
        updateImageXY()
    }

    // 根据中心位置，更新Image的图片实际位置
    function updateImageXY() {
        flickable.contentY = imageY - (flickable.height - showImageContainer.height)/2
        flickable.contentX = imageX - (flickable.width - showImageContainer.width)/2
    }

    // 缩放，传入 flag>0 放大， <0 缩小 ，0回归100%
    function imageScaleAddSub(flag, step=0.1) {
        // 计算缩放比例
        let s = 1.0 // flag==0 时复原
        if (flag > 0) {  // 放大
            s = (imageScale + step).toFixed(1)
            if(s > 2.0) s = 2.0
        }
        else if(flag < 0) {  // 缩小
            s = (imageScale - step).toFixed(1)
            if(s < 0.1) s = 0.1
        }
        imageScale = s
        updateImageXY()
    }
    
    // ======================== 【布局】 =========================

    property real imageScale: 1.0 // 图片缩放比例
    property real imageX: 0 // 图片偏移坐标，以 flickable 中心为原点
    property real imageY: 0
    property int imageW: 0 // 图片宽高
    property int imageH: 0
    property int imageW2: 0 // 图片宽高的一半
    property int imageH2: 0

    // 图片区域
    Rectangle {
        id: flickableContainer
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
            contentWidth: showImageContainer.width
            contentHeight: showImageContainer.height
            clip: true
            
            // 图片容器，大小不小于滑动区域
            Item {
                id: showImageContainer
                width: Math.max( imageW * imageScale , flickable.width )
                height: Math.max( imageH * imageScale , flickable.height )
                Image {
                    id: showImage
                    anchors.centerIn: parent
                    scale: imageScale
                }
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