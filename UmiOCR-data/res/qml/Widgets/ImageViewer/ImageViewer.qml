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
        hasTextBoxes = false
        // 特殊字符#替换为%23
        if(source.startsWith("file:///") && source.includes("#")) {
            source = source.replace(new RegExp("#", "g"), "%23");
        }
        showImage.source = source // 设置源
        if(showImage.source == "") {
            imageScale = 1.0
            return
        }
        imageW = showImage.sourceSize.width // 记录图片宽高
        imageH = showImage.sourceSize.height
        imageScaleFull()
    }

    // 展示图片及 OCR结果
    function setSourceResult(source, res) {
        setSource(source)
        // 格式转换
        if(res.code == 100 && res.data.length > 0) {
            let tbs = []
            for(let i in res.data) {
                const d = res.data[i]
                const info = {
                    x: d.box[0][0],
                    y: d.box[0][1],
                    width: d.box[2][0] - d.box[0][0],
                    height: d.box[2][1] - d.box[0][1],
                    text: d.text
                }
                tbs.push(info)
            }
            textBoxes = tbs
            hasTextBoxes = true
        }
    }

    // ========================= 【处理】 =========================

    // 根据中心位置，更新Image的图片实际位置
    function updateImageXY() {
        flickable.contentY =  - (flickable.height - showImageContainer.height)/2
        flickable.contentX =  - (flickable.width - showImageContainer.width)/2
    }

    // 缩放，传入 flag>0 放大， <0 缩小 ，0回归100%
    function imageScaleAddSub(flag, step=0.1) {
        if(showImage.source == "") return
        // 计算缩放比例
        let s = 1.0 // flag==0 时复原
        if (flag > 0) {  // 放大
            s = (imageScale + step).toFixed(1)
            const imageFullScale = Math.max(flickable.width/imageW, flickable.height/imageH)
            const max = Math.max(imageFullScale, 2.0) // 禁止超过200%或图片填满大小
            if(s > max) s = max
        }
        else if(flag < 0) {  // 缩小
            s = (imageScale - step).toFixed(1)
            if(s < 0.1) s = 0.1
        }
        imageScale = s
        updateImageXY()
    }

    // 图片填满组件
    function imageScaleFull() {
        if(showImage.source == "") return
        imageScale = Math.min(flickable.width/imageW, flickable.height/imageH)
        updateImageXY()
    }

    
    // ======================== 【布局】 =========================

    property real imageScale: 1.0 // 图片缩放比例
    property int imageW: 0 // 图片宽高
    property int imageH: 0
    property bool hasTextBoxes: false // 当前有无文本块
    property bool showTextBoxes: true // 显示文本框
    property var textBoxes: [] // 文本框列表

    // 图片区域
    Rectangle {
        id: flickableContainer
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: bottomCtrl.top
        anchors.margins: size_.spacing
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

                    // OCR 结果文本框容器
                    Item {
                        visible: hasTextBoxes && showTextBoxes

                        Repeater {
                            model: textBoxes
                            Rectangle {
                                property var info: textBoxes[index]
                                x: info.x
                                y: info.y
                                width: info.width
                                height: info.height
                                // border.width: 1
                                border.width: imageScale>1?1:1/imageScale
                                border.color: "red"
                                color: "#00000000"
                            }
                        }
                    }
                }
            }

            // 滚动条
            ScrollBar.vertical: ScrollBar { }
            ScrollBar.horizontal: ScrollBar { }
        }

        // 边框
        Rectangle {
            anchors.fill: parent
            color: "#00000000"
            border.width: 1
            border.color: theme.coverColor3
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
        anchors.margins: size_.spacing
        height: size_.text*1.5
        clip: true

        // 左
        Row {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            Button_ {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                textSize: size_.smallText
                text_: showTextBoxes ? qsTr("显示文本")+" 🔼" : qsTr("隐藏文本")+" 🔽"
                onClicked: showTextBoxes = !showTextBoxes
                visible: hasTextBoxes
            }
        }
        // 右
        Row {
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            // 保存
            // IconButton {
            //     anchors.top: parent.top
            //     anchors.bottom: parent.bottom
            //     width: height
            //     icon_: "save"
            //     color: theme.textColor
            //     onClicked: imageScaleFull()
            //     toolTip: qsTr("保存图片")
            // }
            // 适合宽高
            IconButton {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: height
                icon_: "full_screen"
                color: theme.textColor
                onClicked: imageScaleFull()
                toolTip: qsTr("适应窗口")
            }
            // 1:1
            IconButton {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: height
                icon_: "one_to_one"
                color: theme.textColor
                onClicked: imageScaleAddSub(0)
                toolTip: qsTr("实际大小")
            }
            // 百分比显示
            Text_ {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignRight
                text: (imageScale*100).toFixed(0) + "%"
                color: theme.subTextColor
                width: size_.text * 2.7
            }
        }
    }
}