// =======================================
// =============== 截图窗口 ===============
// =======================================

import QtQuick 2.15
import QtQuick.Window 2.15


Window {
    id: win

    property string imgID: "" // 图片id
    property var onClosed: undefined // 关闭函数，外部传入

    visible: true
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint // 无边框+置顶

    // 底层，图片
    Image {
        anchors.fill: parent
        source: "image://pixmapprovider/"+imgID
    }
    // 叠加层，暗
    Rectangle {
        anchors.fill: parent
        color: "#22000000"
        border.width: 50
        border.color: "red"
    }
    // 鼠标触控层
    MouseArea {
        anchors.fill: parent
        onClicked: {
            if(typeof onClosed === "function")
                onClosed(win.imgID) // 调用关闭函数
        }
    }
}