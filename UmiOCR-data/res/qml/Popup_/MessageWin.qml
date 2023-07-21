// ==================================================
// ===============    外部通知弹窗    ===============
// ==================================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15

import "../Widgets"

Item {
    id: messageRoot
    // ========================= 【对外接口】 =========================

    // 显示一个消息
    function showMessage(title, msg, type="") {
        createWin(winMsg, title, msg, type)
    }


    // ========================= 【弹窗】 =========================

    property var winDict: {}
    // 生成一个弹窗，返回生成ID
    function createWin(winComponent, title, msg, type) {
        // 初始化字典
        if(winDict===undefined) winDict={}
        // 生成一个id
        const winId = (Date.now()+Math.random()).toString()
        // 生成组件，计入字典
        const obj = winComponent.createObject(this, {
            title: title, msg: msg, type: type, winId: winId})
        winDict[winId] = obj
    }
    // 关闭一个弹窗，传入生成ID
    function close(winId) {
        if(winDict.hasOwnProperty(winId)) {
            winDict[winId].destroy()
        }
    }
    
    // 只有单个确认键的普通消息
    Component {
        id: winMsg

        FramelessWindow {
            id: win
            property string title: ""
            property string msg: ""
            property string type: ""
            property string winId: ""

            visible: true
            width: msgComp.width+msgComp.shadowWidth
            height: msgComp.height+msgComp.shadowWidth
            color: "#00000000"

            // 消息盒组件
            MessageBox {
                id: msgComp
                anchors.centerIn: parent
                title: win.title // 标题
                msg: win.msg // 内容
                type: win.type // 类型
                btnsList: [ // 按钮列表
                    {"text": qsTr("确定"), "textColor": theme.themeColor3, "bgColor": theme.themeColor1},
                ]
                onClosed: win.close // 关闭函数
            }

            function close() {
                messageRoot.close(winId)
            }
        }
    }
}