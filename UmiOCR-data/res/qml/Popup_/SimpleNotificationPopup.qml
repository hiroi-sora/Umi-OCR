// ==================================================
// ===============     简单通知弹窗    ===============
// =============== 无确认，计时自动消失 ===============
// ==================================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15 // 阴影
import QtQuick.Window 2.15

import "../Widgets"

Item {
    // ========================= 【对外接口】 =========================

    function show(title, msg) {
        notificationPopup.show(title, msg)
        notificationWindow.show(title, msg)
    }

    // ========================= 【内置模式】 =========================
   
    Popup {
        id: notificationPopup

        // 显示通知弹窗
        function show(title, msg, time=3000) {
            if(opened) { // 已打开，则先关闭
                close()
            }
            nscPopup.show(title, msg, time) // 传入信息
            open() // 开始
            if(!theme.enabledEffect) { // 无动画时，瞬间出现
                nscPopup.y = showY
            }
        }
        // 隐藏通知弹窗
        function hide() {
            close()
        }
        // 属性
        padding: 0
        property real showY: -nscPopup.height*1.5
        modal: false // 非模态层（不阻挡下方）
        parent: Overlay.overlay
        x: Math.round((parent.width - width) / 2)
        y: Math.round((parent.height - height))
        closePolicy: Popup.NoAutoClose // 不被系统关闭
        // 组件
        SimpleNotificationComp {
            id: nscPopup
            onHided: notificationPopup.hide // 关闭事件
            anchors.horizontalCenter: parent.horizontalCenter
            y: notificationPopup.showY
        }
        // 进入动画
        enter: theme.enabledEffect ? enterAnimePop : null
        Transition {
            id: enterAnimePop
            NumberAnimation { 
                target: nscPopup
                property: "y"
                duration: 200
                from: 0
                to: notificationPopup.showY
                easing.type: Easing.OutCubic
            }
        }
        // 关闭动画
        exit: theme.enabledEffect ? exitAnimePop : null
        Transition {
            id: exitAnimePop
            NumberAnimation { 
                target: nscPopup
                property: "y"
                duration: 200
                from: notificationPopup.showY
                to: 0
                easing.type: Easing.InCubic
            }
        }
    }

    // ========================= 【外置模式】 =========================
    Window {
        id: notificationWindow

        // 显示通知弹窗
        function show(title, msg, time=3000) {
            let screenWidth = Screen.width
            let screenHeight = Screen.height
            x = (screenWidth - width) / 2 // 水平居中

            nscWindow.show(title, msg, time) // 传入信息
            if(theme.enabledEffect) { // 出现动画
                enterAnimeWin.start()
            }
            else { // 无动画时，y瞬间出现
                y = screenHeight-showY
            }
            visible = true
        }
        // 隐藏通知弹窗
        function hide() {
            if(theme.enabledEffect) { // 关闭动画
                exitAnimeWin.start()
            }
            else { // 无动画时，瞬间关闭
                visible = false
            }
        }
        // 属性
        property real showY: nscWindow.height+100 // 显示位置高度
        visible: false
        flags: Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint // 无边框，置顶
        color: "#00000000"
        width: nscWindow.width+nscWindow.shadowWidth // 长宽要加上阴影宽度
        height: nscWindow.height+nscWindow.shadowWidth
        Component.onCompleted: y=Screen.height-showY // 初始y值，防止theme未加载导致第一次调用异常
        SimpleNotificationComp {
            id: nscWindow
            anchors.centerIn: parent
            onHided: notificationWindow.hide // 关闭事件
        }
        // 进入动画
        ParallelAnimation {
            id: enterAnimeWin
            running: false
            NumberAnimation { 
                target: notificationWindow
                property: "y"
                duration: 200
                from: Screen.height
                to: Screen.height-notificationWindow.showY
                easing.type: Easing.OutCubic
            }
        }
        // 关闭动画
        ParallelAnimation {
            id: exitAnimeWin
            running: false
            onStopped: {
                notificationWindow.visible = false
            }
            NumberAnimation { 
                target: notificationWindow
                property: "y"
                duration: 200
                from: Screen.height-notificationWindow.showY
                to: Screen.height
                easing.type: Easing.InCubic
            }
        }
    }
}