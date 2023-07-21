// ==================================================
// ===============    带确认通知弹窗    ===============
// ==================================================

import QtQuick 2.15
import QtQuick.Controls 2.15
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

    function close(winId) {
        if(winDict.hasOwnProperty(winId)) {
            winDict[winId].destroy()
        }
    }

    property var winDict: {}

    // ========================= 【外部弹窗】 =========================
    
    Component {
        id: msgWin

        Window {
            id: win
            visible: true

            // 鼠标拖拽移动窗口
            MouseArea {
                anchors.fill: parent
                property int ox: 0
                property int oy: 0
                onPressed: {
                    ox = mouse.x
                    oy = mouse.y
                }
                onPositionChanged: {
                    win.setX(win.x+mouse.x-ox)
                    win.setY(win.y+mouse.y-oy)
                }
            }

            property string title: ""
            property string msg: ""
            property string winId: ""
            width: msgComp.width+msgComp.shadowWidth
            height: msgComp.height+msgComp.shadowWidth
            flags: Qt.FramelessWindowHint // 无边框
            color: "#00000000"

            // 消息盒组件
            MessageBox {
                id: msgComp
                anchors.centerIn: parent
                title: win.title // 标题
                msg: win.msg // 内容
                btnsList: [ // 按钮列表
                    {"text":qsTr("确定"), "textColor": theme.themeColor3, "bgColor": theme.themeColor1},
                ]
                onClosed: win.close // 关闭函数
            }

            function close() {
                messageRoot.close(winId)
            }
        }
    }
}