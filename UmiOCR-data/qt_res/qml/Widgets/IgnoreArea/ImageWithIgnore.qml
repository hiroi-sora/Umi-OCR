// ====================================================
// =============== 可框选的增强Image组件 ===============
// ====================================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import "../ImageViewer"

ImageScale {
    id: iRoot
    property bool showOverlay: true // 显示叠加层
    property int lineWidth: 1 // 线宽
    property color crossLineColor: "#00f91a" // 十字指示器的颜色

    beforeShow: () => {
        textBoxes = [] // 清空旧文本块
    }
    // 展示文本块
    function showTextBoxes(res) {
        beforeShow()
        // 提取文本框
        if(res.code == 100 && res.data.length > 0) {
            let tbs = []
            for(let i in res.data) {
                const d = res.data[i]
                const info = {
                    x: d.box[0][0],
                    y: d.box[0][1],
                    width: d.box[2][0] - d.box[0][0],
                    height: d.box[2][1] - d.box[0][1],
                    text: d.text,
                }
                tbs.push(info)
            }
            textBoxes = tbs
        }
    }
    // 显示/隐藏叠加层
    function switchOverlay() {
        showOverlay = !showOverlay
    }

    // 撤销
    function revokeIg() {
        let bs = ig1Boxes
        if(bs.length > 0)
            bs.pop()
        ig1Boxes = bs
    }
    // 清空
    function clearIg() {
        ig1Boxes = []
    }

    property var textBoxes: [] // 文本块列表
    property var ig1Boxes: [] // 忽略区域1

    // 文本框叠加层
    overlayLayer: Item {
        id: oRoot
        anchors.fill: parent
        visible: showOverlay
        property real borderWidth: Math.max(1, 1/iRoot.scale)

        // 文本块
        Repeater {
            model: textBoxes
            Rectangle {
                x: modelData.x
                y: modelData.y
                width: modelData.width
                height: modelData.height
                color: "#00000000"
                border.width: oRoot.borderWidth
                border.color: "#000"
                Rectangle {
                    anchors.fill: parent
                    anchors.margins: oRoot.borderWidth
                    color: "#22000000"
                    border.width: oRoot.borderWidth
                    border.color: "#FFF"
                }
            }
        }

        // 忽略区域1
        Repeater {
            model: ig1Boxes
            Rectangle {
                x: modelData.x
                y: modelData.y
                width: modelData.width
                height: modelData.height
                color: "#99000000"
                border.width: oRoot.borderWidth
                border.color: "#FFFF00"
            }
        }
    }
    // 十字线与当前选区
    Item {
        id: cross
        anchors.fill: parent
        clip: true
        property int min: -2147480000
        property int px: cross.min // 十字线
        property int py: cross.min
        property int ax: cross.min // 当前选区
        property int ay: cross.min
        property int aw: cross.min
        property int ah: cross.min
        Rectangle {
            visible: y > cross.min
            color: crossLineColor
            anchors.left: parent.left
            anchors.right: parent.right
            y: cross.py
            height: lineWidth
        }
        Rectangle {
            visible: x > cross.min
            color: crossLineColor
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            x: cross.px
            width: lineWidth
        }
        Rectangle {
            visible: x>cross.min && y>cross.min
            x: cross.ax
            y: cross.ay
            width: cross.aw
            height: cross.ah
            border.width: lineWidth
            border.color: crossLineColor
            color: "#00000000"
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        // 拖拽起始和结束的坐标
        property int startX: -1
        property int startY: -1
        property int endX: -1
        property int endY: -1
        acceptedButtons: Qt.LeftButton | Qt.RightButton

        // 添加选区框
        function addSelectBox() {
            let bs = ig1Boxes
            let x1 = cross.ax, y1 = cross.ay, x2 = x1 + cross.aw, y2 = y1 + cross.ah
            cross.ax = cross.ay = cross.aw = cross.ah = cross.min
            const p1 = oRoot.mapFromItem(mouseArea, x1, y1)
            const p2 = oRoot.mapFromItem(mouseArea, x2, y2)
            x1 = p1.x; y1 = p1.y; x2 = p2.x; y2 = p2.y;
            bs.push({
                "x": x1,
                "y": y1,
                "width": x2 - x1,
                "height": y2 - y1,
            })
            ig1Boxes = bs
        }
        // 按下
        onPressed: {
            cross.px = cross.py = cross.min
            if(iRoot.imageSW===0 || iRoot.imageSH===0) {
                startX = startY = endX = endY = -1
                return
            }
            if (mouse.button === Qt.LeftButton) {
                mouse.accepted = false
            }
            else if (mouse.button === Qt.RightButton) {
                startX = mouseX
                startY = mouseY
                endX = endY = 0
            }
        }
        // 移动
        onPositionChanged: {
            if(iRoot.imageSW===0 || iRoot.imageSH===0) {
                return
            }
            endX = mouseX
            endY = mouseY
            if(pressed) {
                cross.px = cross.py = cross.min
                // 更新选区框
                if(startX < endX) {
                    cross.ax = startX
                    cross.aw = endX - startX
                }
                else {
                    cross.ax = endX
                    cross.aw = startX - endX
                }
                if(startY < endY) {
                    cross.ay = startY
                    cross.ah = endY - startY
                }
                else {
                    cross.ay = endY
                    cross.ah = startY - endY
                }
            }
            else {
                cross.px = mouseX
                cross.py = mouseY
            }
        }
        // 抬起
        onReleased: {
            if(iRoot.imageSW===0 || iRoot.imageSH===0) {
                return
            }
            cross.px = endX = mouseX
            cross.py = endY = mouseY
            mouseArea.addSelectBox()
            startX = startY = endX = endY = -1
        }
        // 离开
        onExited: {
            cross.px=cross.py=cross.ax=cross.ay=cross.min
        }
    }
}