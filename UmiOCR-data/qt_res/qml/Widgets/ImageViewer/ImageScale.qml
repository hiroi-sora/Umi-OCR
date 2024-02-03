// ==================================================
// =============== 可缩放的图片预览组件 ===============
// ==================================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import ".."

Rectangle {
    id: iRoot
    // ========================= 【接口】 =========================

    // 可设置
    property real scaleMax: 2.0 // 比例上下限
    property real scaleMin: 0.1 // 比例上下限
    property QtObject overlayLayer // 图片叠加层
    property var border: bRect.border // 边框
    // 只读
    property alias showImage: showImage // 图片组件
    property real scale: 1.0 // 图片缩放比例
    property int imageSW: 0 // 图片原始宽高
    property int imageSH: 0
    // 子类重写
    property var beforeShow: undefined // 展示图片之前执行的操作

    // 设置图片源，展示一张图片
    function setSource(source) {
        if(source) {
            // 特殊字符#替换为%23
            if(source.startsWith("file:///") && source.includes("#"))
                source = source.replace(new RegExp("#", "g"), "%23");
            showImage.source = source // 设置源
        }
        else
            showImage.source = ""
    }

    // 传入路径，展示图片
    function showPath(path) {
        if(beforeShow) beforeShow()
        showImage.showPath(path)
    }

    // 传入imgID，展示图片
    function showImgID(imgID) {
        if(beforeShow) beforeShow()
        showImage.showImgID(imgID)
    }

    // 清空展示
    function clear() {
        if(beforeShow) beforeShow()
        // showImage.clear()
        showImage.source = ""
        imageSW = imageSH = 0
    }

    // 复制当前图片
    function copyImage() {
        if(showImage.source == "") return
        const res = qmlapp.imageManager.copyImage(showImage.source)
        if(res === "[Success]")
            qmlapp.popup.simple(qsTr("复制图片"), "")
        else
            qmlapp.popup.simple(qsTr("复制图片失败"), res)
    }

    // 保存当前图片
    function saveImage() {
        if(showImage.source == "") return
        saveDialog.open()
    }

    FileDialog_ {
        id: saveDialog
        title: qsTr("保存图片")
        selectExisting: false
        selectFolder: false
        folder: shortcuts.desktop // 默认放桌面
        nameFilters: ["*.png", "*.jpg"]
        onAccepted: {
            if(!fileUrl) {
                console.log("文件对话框：未选择任何文件")
                return
            }
            let filePath = fileUrl
            const res = qmlapp.imageManager.saveImage(showImage.source, filePath)
            if(res.startsWith("[Success]"))
                qmlapp.popup.simple(qsTr("保存图片"), res)
            else
                qmlapp.popup.simple(qsTr("保存图片失败"), res)
        }
    }

    // ========================= 【处理】 =========================

    Component.onCompleted: {
        // 叠加层挂父级
        if(overlayLayer && overlayLayer.hasOwnProperty("parent"))
            overlayLayer.parent = showImage
    }
    

    // 图片组件的状态改变
    function imageStatusChanged(s) {
        // 已就绪
        if(s == Image.Ready) {
            imageSW = showImage.sourceSize.width // 记录图片原始宽高
            imageSH = showImage.sourceSize.height
            imageFullFit() // 初始大小
        }
        else {
            imageSW = imageSH = 0
            iRoot.scale = 1 
        }
    }

    // 缩放，传入 flag>0 放大， <0 缩小 ，0回归100%。以相框中心为锚点。
    function imageScaleAddSub(flag, step=0.1) {
        if(showImage.status != Image.Ready) return
        // 计算缩放比例
        let s = 1.0 // flag==0 时复原
        if (flag > 0) {  // 放大
            s = (iRoot.scale + step).toFixed(1)
            // 禁止大于上限 或 图片填满大小（裁切）
            const max = Math.max(flickable.width/imageSW, flickable.height/imageSH, scaleMax)
            if(s > max) s = max
        }
        else if(flag < 0) {  // 缩小
            s = (iRoot.scale - step).toFixed(1)
            // 禁止小于下限 或 图片填满大小（不裁切）
            const min = Math.min(flickable.width/imageSW, flickable.height/imageSH, scaleMin)
            if(s < min) s = min
        }

        // 目标锚点
        let gx = -flickable.width/2
        let gy = -flickable.height/2
        // 目标锚点在图片中的原比例
        let s1x = (flickable.contentX-gx)/showImageContainer.width
        let s1y = (flickable.contentY-gy)/showImageContainer.height
        // 目标锚点在图片中的新比例，及差值
        iRoot.scale = s // 更新缩放
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

    // 图片填满组件，不裁切
    function imageFullFit() {
        if(showImage.source == "" || imageSW <= 0) return
        iRoot.scale = Math.min(flickable.width/imageSW, flickable.height/imageSH)
        // 图片中心对齐相框
        flickable.contentY =  - (flickable.height - showImageContainer.height)/2
        flickable.contentX =  - (flickable.width - showImageContainer.width)/2
    }
    
    // ======================== 【布局】 =========================
    color: theme.bgColor


    // 滑动区域，显示图片，监听左键拖拽
    Flickable {
        id: flickable
        anchors.fill: parent
        contentWidth: showImageContainer.width
        contentHeight: showImageContainer.height
        clip: true
        
        // 图片容器，大小不小于滑动区域
        Item {
            id: showImageContainer
            width: Math.max( imageSW * iRoot.scale , flickable.width )
            height: Math.max( imageSH * iRoot.scale , flickable.height )
            Image_ {
                id: showImage
                anchors.centerIn: parent
                scale: iRoot.scale
                onStatusChanged: imageStatusChanged(status)
            }
        }

        // 滚动条
        ScrollBar.vertical: ScrollBar { }
        ScrollBar.horizontal: ScrollBar { }
    }

    // 监听滚轮缩放
    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.NoButton
        // 滚轮缩放
        onWheel: {
            if (wheel.angleDelta.y > 0) {
                imageScaleAddSub(1) // 放大
            }
            else {
                imageScaleAddSub(-1) // 缩小
            }
        }
    }

    // 边框
    Rectangle {
        id: bRect
        anchors.fill: parent
        color: "#00000000"
        border.width: 1
        border.color: theme.coverColor4
    }
}