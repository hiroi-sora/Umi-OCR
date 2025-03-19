// =========================================
// =============== 全屏遮罩层 ===============
// =========================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import "../Widgets"

Popup {

    // 展示遮罩层。同一个id重复调用时，可刷新显示文本。
    function showMask(msg="", id="") {
        if(msgDict === undefined)
            msgDict = {}
        if(!(id in msgDict)) // 新加入的id
            idList.push(id)
        msgDict[id] = msg // 刷新消息字典
        message = msg // 刷新消息显示
        visible = true // 开启显示状态
    }

    // 隐藏指定id的遮罩层
    function hideMask(id="") {
        if(id in msgDict) { // id已记录，则移除对应项
            delete msgDict[id]
            const index = idList.indexOf(id)
            if(index !== -1)
                idList.splice(index, 1)
        }
        // 不存在激活的id时，解除显示状态
        if(idList.length === 0) {
            visible = false
        }
        // 否则，寻找上一个激活的id，刷新显示文本
        else {
            const lastID = idList[idList.length - 1]
            const msg = msgDict[lastID] || ""
            message = msg
        }
    }

    property string message: ""
    property var idList: [] // 存放所有已显示的id，有序
    property var msgDict: {} // key为id，value为消息文本

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
            width: textMetrics.width > maxWidth ? maxWidth : implicitWidth // 宽度根据内容自适应，不超过 maxWidth
            wrapMode: textMetrics.width > maxWidth ? Text.Wrap : Text.NoWrap
        }
    }

    // 文本宽度测量器，不可见
    Text_ { // TextMetrics不准确，只能用普通Text
        id: textMetrics
        visible: false
        text: message
    }
}