// =========================================
// =============== 弹窗管理器 ===============
// =========================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15 // 阴影

import "../Widgets"

Item {
    // ========================= 【对外接口】 =========================

    // 显示简单通知，无需确认，计时自动消失
    function showSimple(title, msg) {
        messageSimple.show(title, msg)
        showMessage(title, msg) // TODO: 
    }

    // 显示带确认的通知弹窗
    function showMessage(title, msg) {
        message.show(title, msg)
    }

    Component.onCompleted: {
        qmlapp.initFuncs.push(()=>{showSimple("111", "222")})
    }
    

    // ========================= 【内部】 =========================

    Message{ id: message }
    MessageSimple { id: messageSimple }
}