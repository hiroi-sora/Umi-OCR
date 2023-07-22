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
    function showMessage(title, msg, type) {
        const argd = {
            title:title, msg:msg, type:type
        }
        createWin(winMsg, argd)
    }

    // 显示一个双选项对话窗
    function showDialog(title, msg, callback, yesText, noText, type) {
        const argd = {
            title:title, msg:msg, callback:callback, yesText:yesText, noText:noText, type:type
        }
        createWin(winDialog, argd)
    }


    // ========================= 【弹窗】 =========================

    property var winDict: {}
    // 生成一个弹窗，返回生成ID
    function createWin(winComponent, argd) {
        // 初始化字典
        if(winDict===undefined) winDict={}
        // 生成一个id
        const winId = (Date.now()+Math.random()).toString()
        argd.winId = winId // 添加id
        // 生成组件，计入字典
        const obj = winComponent.createObject(this, argd)
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

    // 有两个键（确认/取消）的对话框
    Component {
        id: winDialog

        FramelessWindow {
            id: win
            property string title: ""
            property string msg: ""
            property string type: ""
            property string winId: ""
            property string yesText: ""
            property string noText: ""
            property var callback // 回调函数

            visible: true
            width: msgComp.width+msgComp.shadowWidth
            height: msgComp.height+msgComp.shadowWidth
            color: "#00000000"

            MessageBox {
                id: msgComp
                anchors.centerIn: parent
                title: win.title // 标题
                msg: win.msg // 内容
                type: win.type // 类型
                btnsList: [ // 按钮列表
                    // 确认
                    {"text": yesText, "value": true, "textColor": getYesColor(), "bgColor": theme.themeColor1},
                    // 取消
                    {"text": noText, "value": false, "textColor": theme.subTextColor, "bgColor": theme.bgColor},
                ]
                // 主按钮颜色
                function getYesColor() {
                    switch(type) {
                        case "warning":
                        case "error":
                            return  theme.noColor
                        default:
                            return theme.themeColor3
                    }
                }
                onClosed: (value)=>{
                    callback(value)
                    messageRoot.close(winId) // 关闭窗口
                }
            }
        }
    }
}