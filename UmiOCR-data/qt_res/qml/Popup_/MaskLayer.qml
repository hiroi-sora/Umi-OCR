// =========================================
// =============== 全屏遮罩层 ===============
// =========================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import "../Widgets"

Popup {

    // 展示遮罩层
    function showMask(msg="", id="") {
        message = msg
        idList.push(id)
        visible = true
    }

    // 隐藏指定id的遮罩层
    function hideMask(id="") {
        const index = idList.indexOf(id)
        if(index !== -1) {
            idList.splice(index, 1)
        }
        // 所有显示id都删除时，才解除显示状态
        if(idList.length === 0) {
            visible = false
        }
    }

    property string message: ""
    property var idList: []

    visible: false
    modal: true // 阻止按键穿透
    closePolicy: Popup.NoAutoClose
    parent: Overlay.overlay
    anchors.centerIn: parent
    property int maxWidth: parent.width - size_.line*10
    width: text.width + size_.spacing*2
    height: text.height + size_.spacing*2
    
    // 背景
    background: Rectangle {
        visible: message!==""
        color: theme.bgColor
        radius: size_.panelRadius

        Text_ {
            id: text
            anchors.centerIn: parent
            text: message
            width: wrapMode === Text.Wrap ? maxWidth : implicitWidth
            wrapMode: implicitWidth > maxWidth ? Text.Wrap : Text.NoWrap
        } 
    }
}