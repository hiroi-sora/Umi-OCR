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
    }

    // 图片组件的状态改变
    function imageStatusChanged(s) {
        // 已就绪
        if(s == Image.Ready) {
            imageW = showImage.sourceSize.width // 记录图片宽高
            imageH = showImage.sourceSize.height
            imageScaleFull() // 初始大小
        }
        else {
            imageW = imageH = 0
            imageScale = 1 
        }
    }

    // 展示图片及 OCR结果
    function setSourceResult(source, res) {
        setSource(source)
        // 格式转换
        if(res.code == 100 && res.data.length > 0) {
            let tbs = []
            let sText = "" 
            for(let i in res.data) {
                const d = res.data[i]
                const info = {
                    x: d.box[0][0],
                    y: d.box[0][1],
                    x2: d.box[2][0],
                    y2: d.box[2][1],
                    width: d.box[2][0] - d.box[0][0],
                    height: d.box[2][1] - d.box[0][1],
                    text: d.text,
                    selected: false, // 是否选中
                }
                sText += d.text + "\n"
                tbs.push(info)
            }
            textBoxes = tbs
            hasTextBoxes = true
            retainSelected = false
            if(sText) {
                sText = sText.slice(0, -1) // 去除结尾换行
                selectTextEdit.text = sText
            }
        }
    }

    // ========================= 【处理】 =========================

    // 缩放，传入 flag>0 放大， <0 缩小 ，0回归100%。以相框中心为锚点。
    function imageScaleAddSub(flag, step=0.1) {
        if(showImage.status != Image.Ready) return
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

        // 目标锚点
        let gx = -flickable.width/2
        let gy = -flickable.height/2
        // 目标锚点在图片中的原比例
        let s1x = (flickable.contentX-gx)/showImageContainer.width
        let s1y = (flickable.contentY-gy)/showImageContainer.height
        // 目标锚点在图片中的新比例，及差值
        imageScale = s // 更新缩放
        let s2x = (flickable.contentX-gx)/showImageContainer.width
        let s2y = (flickable.contentY-gy)/showImageContainer.height
        let sx = s2x-s1x
        let sy = s2y-s1y
        // 实际长度差值
        let lx = sx*showImageContainer.width
        let ly = sy*showImageContainer.height
        // 偏移
        flickable.contentX -= lx
        flickable.contentY -= ly
    }

    // 图片填满组件
    function imageScaleFull() {
        if(showImage.source == "") return
        imageScale = Math.min(flickable.width/imageW, flickable.height/imageH)
        // 图片中心对齐相框
        flickable.contentY =  - (flickable.height - showImageContainer.height)/2
        flickable.contentX =  - (flickable.width - showImageContainer.width)/2
    }

    // 选中坐标处的文字
    function lookTextBox(x, y, isAdd=false) {
        let sText = "", sFlag = ""
        for(let i=0, l=textBoxes.length; i<l; i++) {
            const tb = textBoxes[i]
            if(x >= tb.x && x <= tb.x2 && y >= tb.y && y <= tb.y2) {
                if(tb.selected == false) {
                    textBoxRepeater.itemAt(i).isSelected = true
                    tb.selected = true
                }
                sText += tb.text+"\n"
                sFlag += i.toString()
            }
            else {
                if(tb.selected == true) {
                    if(isAdd) {
                        sText += tb.text+"\n"
                        sFlag += i.toString()
                    }
                    else {
                        tb.selected = false
                        textBoxRepeater.itemAt(i).isSelected = false
                    }
                }
            }
        }
        if(isAdd && sFlag=="") { // 增模式下为空，关闭选中保持
            retainSelected = false
            return
        }
        if(!isAdd && retainSelected) // 保持上一轮选中
            return
        if(isAdd) { // 增模式下不为空，启用选中保持
            retainSelected = true
        }
        if(sText) { // 刷新选中文字
            sText = sText.slice(0, -1) // 去除结尾换行
            selectTextEdit.text = sText
        }
    }

    
    // ======================== 【布局】 =========================

    property real imageScale: 1.0 // 图片缩放比例
    property int imageW: 0 // 图片宽高
    property int imageH: 0
    property bool hasTextBoxes: false // 当前有无文本块
    property bool showTextBoxes: false // 显示文本框
    property var textBoxes: [] // 文本框列表
    property bool retainSelected: false // 保留选中状态

    // 图片区域
    Rectangle {
        id: flickableContainer
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: selectTextContainer.top
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
                    onStatusChanged: imageStatusChanged(status)

                    // OCR 结果文本框容器
                    Item {
                        visible: hasTextBoxes && showTextBoxes

                        Repeater {
                            id: textBoxRepeater
                            model: textBoxes
                            Rectangle {
                                property var info: textBoxes[index]
                                property bool isSelected: false
                                x: info.x
                                y: info.y
                                width: info.width
                                height: info.height
                                // border.width: 1
                                border.width: imageScale>1?1:1/imageScale
                                border.color: "red"
                                color: "#00000000"
                                Rectangle { // 选中指示
                                    visible: parent.isSelected
                                    anchors.fill: parent
                                    border.width: 5
                                    border.color: "red"
                                    color: "#00000000"
                                }
                            }
                        }
                    }

                    // 监听点击和拖拽
                    MouseArea {
                        id: inMouseArea
                        visible: hasTextBoxes && showTextBoxes
                        anchors.fill: parent
                        acceptedButtons: Qt.RightButton
                        hoverEnabled: true
                        onPositionChanged : {
                            lookTextBox(mouse.x, mouse.y, pressed)
                        }
                        onPressed: {
                            lookTextBox(mouse.x, mouse.y, pressed)
                            flickable.interactive = false // 禁止移动
                        }
                        onReleased: {
                            flickable.interactive = true
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

        // 监听滚轮缩放
        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.NoButton
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

    // 文本区域
    Rectangle {
        id: selectTextContainer
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: bottomCtrl.top
        anchors.leftMargin: size_.spacing
        anchors.rightMargin: size_.spacing
        color: theme.bgColor
        border.width: 1
        border.color: theme.coverColor3
        height: (hasTextBoxes && showTextBoxes) ? size_.smallText*5:0

        ScrollView {
            id: selectScrollView
            anchors.fill: parent
            anchors.margins: size_.smallSpacing
            contentWidth: width // 内容宽度
            clip: true // 溢出隐藏

            TextEdit {
                id: selectTextEdit
                width: selectScrollView.width // 与内容宽度相同
                textFormat: TextEdit.PlainText // 纯文本
                wrapMode: TextEdit.Wrap // 尽量在单词边界处换行
                readOnly: false // 可编辑
                selectByMouse: true // 允许鼠标选择文本
                selectByKeyboard: true // 允许键盘选择文本
                color: theme.textColor
                font.pixelSize: size_.smallText
                font.family: theme.dataFontFamily
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
                text_: showTextBoxes ? qsTr("隐藏文本")+" 🔽" : qsTr("显示文本")+" 🔼"
                onClicked: showTextBoxes = !showTextBoxes
                visible: hasTextBoxes
            }
        }
        // 右
        Row {
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom


            // 复制文字
            IconButton {
                visible: hasTextBoxes && showTextBoxes
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: height
                icon_: "paste"
                color: theme.textColor
                onClicked: {
                    qmlapp.utilsConnector.copyText(selectTextEdit.text)
                }
                toolTip: qsTr("复制文本")
            }
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