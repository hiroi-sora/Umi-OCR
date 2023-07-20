// ==================================================
// ===============     简单通知弹窗    ===============
// =============== 无确认，计时自动消失 ===============
// ==================================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15 // 阴影

import "../Widgets"

Item {
    // ========================= 【对外接口】 =========================

    function show(title, msg) {
        notificationPopup.show(title, msg)
    }

    // ========================= 【内置模式】 =========================
   
    Popup {
        id: notificationPopup

        // 显示通知弹窗
        function show(title, msg, time=3000) {
            if(opened) { // 已打开，则先关闭
                close()
            }
            notifySimpleComp.show(title, msg, time) // 传入信息
            open() // 开始
            if(!theme.enabledEffect) { // 无动画时，瞬间出现
                notifySimpleComp.y = showY
            }
        }
        // 隐藏通知弹窗
        function hide() {
            close()
        }
        // 属性
        padding: 0
        property real showY: -notifySimpleComp.height*1.5
        modal: false // 非模态层（不阻挡下方）
        parent: Overlay.overlay
        x: Math.round((parent.width - width) / 2)
        y: Math.round((parent.height - height))
        closePolicy: Popup.NoAutoClose // 不被系统关闭
        // 组件
        SimpleNotificationComp {
            id: notifySimpleComp
            onHided: notificationPopup.hide // 关闭事件
            anchors.horizontalCenter: parent.horizontalCenter
            y: notificationPopup.showY
        }
        // 进入动画
        enter: theme.enabledEffect ? enterAnime : null
        Transition {
            id: enterAnime
            NumberAnimation { 
                target: notifySimpleComp
                property: "y"
                duration: 200
                from: 0
                to: notificationPopup.showY
                easing.type: Easing.OutCubic
            }
        }
        // 关闭动画
        exit: theme.enabledEffect ? exitAnime : null
        Transition {
            id: exitAnime
            NumberAnimation { 
                target: notifySimpleComp
                property: "y"
                duration: 200
                from: notificationPopup.showY
                to: 0
                easing.type: Easing.InCubic
            }
        }
    }
}