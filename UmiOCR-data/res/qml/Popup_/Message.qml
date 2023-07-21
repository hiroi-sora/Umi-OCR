// ==================================================
// ===============    带确认通知弹窗    ===============
// ==================================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15 // 阴影
import QtQuick.Window 2.15

import "../Widgets"

Item {
    id: messageRoot
    // ========================= 【对外接口】 =========================

    function show(title, msg) {
        if(winDict===undefined) winDict={}
        // 生成一个id
        const winId = (Date.now()+Math.random()).toString()
        // 生成组件，计入字典
        const obj = msgWin.createObject(this, {
            title: title, msg: msg, winId: winId})
        winDict[winId] = obj
    }

    function hide(winId) {
        console.log("关闭弹窗对象", winId)
        if(winDict.hasOwnProperty(winId)) {
            winDict[winId].destroy()
        }
    }

    property var winDict: {}

    // ========================= 【外部弹窗】 =========================
    
    Component {
        id: msgWin

        Window  {
            visible: true

            MessageComp {
                id: msgComp
            }

            property string title: ""
            property string msg: ""
            property string winId: ""
            width: msgComp.width
            height: msgComp.height
            flags: Qt.FramelessWindowHint // 无边框
            color: "#00000000"
            Component.onCompleted: {
                msgComp.show(title, msg)
                msgComp.onHided = hide
            }

            function hide() {
                messageRoot.hide(winId)
            }
        }
    }
}