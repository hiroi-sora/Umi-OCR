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

    // 带“不再提示”的消息
    // mid: 唯一标识一个提示
    function showMessageMemory(mid, title, msg, type) {
        // 检查全局设置记忆列表中，是否已记录mid
        const midList = qmlapp.globalConfigs.getValue("window.messageMemory")
        if(midList.includes(mid)) // 已记录则不再弹出
            return
        const argd = {
            mid: mid, title:title, msg:msg, type:type
        }
        createWin(winMsgMemory, argd)
    }

    // 显示一个双选项对话窗
    function showDialog(title, msg, callback, yesText, noText, type) {
        const argd = {
            title:title, msg:msg, callback:callback, yesText:yesText, noText:noText, type:type
        }
        createWin(winDialog, argd)
    }

    // 显示一个双选项带倒计时对话窗
    function showDialogCountdown(title, msg, callback, yesText, noText, type, time) {
        const argd = {
            title:title, msg:msg, callback:callback, yesText:yesText, noText:noText, type:type, time:time
        }
        createWin(winDialogCountdown, argd)
    }


    // ========================= 【弹窗】 =========================
    
    // 主按钮颜色
    function getYesColor(type) {
        switch(type) {
            case "warning":
            case "error":
                return  theme.noColor
            default:
                return theme.specialTextColor
        }
    }

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
        // 显示遮罩层
        qmlapp.popup.showMask("", winId)
    }
    // 关闭一个弹窗，传入生成ID
    function close(winId) {
        if(winDict.hasOwnProperty(winId)) {
            winDict[winId].destroy()
        }
        // 隐藏遮罩层
        qmlapp.popup.hideMask(winId)
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
                    {"text": qsTr("确定"), "textColor": theme.specialTextColor, "bgColor": theme.specialBgColor},
                ]
                onClosed: win.close // 关闭函数
            }

            function close() {
                messageRoot.close(winId)
            }
        }
    }

    // 带“不再提示”的记忆消息
    Component {
        id: winMsgMemory

        FramelessWindow {
            id: win
            property string title: ""
            property string msg: ""
            property string type: ""
            property string winId: ""
            property string mid: ""

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
                    {"text": qsTr("不再提示"), "value": true, "textColor": theme.specialTextColor, "bgColor": theme.specialBgColor},
                    {"text": qsTr("知道了"), "value": false, "textColor": theme.subTextColor, "bgColor": theme.bgColor},
                ]
                onClosed: (value)=>{
                    if(value) {
                        // 将mid添加到全局设置记忆列表中
                        let midList = qmlapp.globalConfigs.getValue("window.messageMemory")
                        midList.push(mid)
                        qmlapp.globalConfigs.setValue("window.messageMemory", midList)
                    }
                    messageRoot.close(winId) // 关闭窗口
                }
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
                    {"text": yesText, "value": true, "textColor": messageRoot.getYesColor(win.type), "bgColor": theme.specialBgColor},
                    // 取消
                    {"text": noText, "value": false, "textColor": theme.subTextColor, "bgColor": theme.bgColor},
                ]
                onClosed: (value)=>{
                    callback(value)
                    messageRoot.close(winId) // 关闭窗口
                }
            }
        }
    }

    // 带倒计时的双键对话框
    Component {
        id: winDialogCountdown

        FramelessWindow {
            id: win
            property string title: ""
            property string msg: ""
            property string type: ""
            property string winId: ""
            property string yesText: ""
            property string yesTextTime: "" // 带倒计时的确定文本
            property string noText: ""
            property int time: 10000
            property int nowTime: 0
            property int interval: 1000
            property var callback // 回调函数

            visible: true
            width: msgComp.width+msgComp.shadowWidth
            height: msgComp.height+msgComp.shadowWidth
            color: "#00000000"

            
            Component.onCompleted: {
                win.yesTextTime = win.yesText+` (${win.time*0.001})`
                win.nowTime = win.time
                timer.running = true
            }

            Timer {
                id: timer
                interval: win.interval // 间隔
                running: false
                repeat: true // 重复执行
                onTriggered: {
                    win.nowTime -= win.interval
                    win.yesTextTime = win.yesText+` (${win.nowTime*0.001})`
                    if(win.nowTime<=0) {
                        timer.stop() // 停止计时器
                        callback(true) // 回调
                        messageRoot.close(winId) // 关闭窗口
                        return
                    }
                }
            }

            MessageBox {
                id: msgComp
                anchors.centerIn: parent
                title: win.title // 标题
                msg: win.msg // 内容
                type: win.type // 类型
                btnsList: [ // 按钮列表
                    // 确认
                    {"text": yesTextTime, "value": true, "textColor": messageRoot.getYesColor(win.type), "bgColor": theme.specialBgColor},
                    // 取消
                    {"text": noText, "value": false, "textColor": theme.subTextColor, "bgColor": theme.bgColor},
                ]
                onClosed: (value)=>{
                    timer.running = false // 停止计时器
                    callback(value)
                    messageRoot.close(winId) // 关闭窗口
                }
            }
        }
    }
}