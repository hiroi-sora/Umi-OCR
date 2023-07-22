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
    function simple(title, msg) {
        messageSimple.show(title, msg)
    }

    // 显示带确认的通知弹窗
    // type可选: ""默认， "warning"警告， "error"错误
    function message(title, msg, type="") {
        messageWin.showMessage(title, msg, type)
    }

    // 双选项对话窗（确定|取消）。需要传入回调函数，返回true/false
    function dialog(title, msg, callback, type="", argd={}) {
        let yesText=qsTr("确认"), noText=("取消")
        if(argd.hasOwnProperty("yesText"))
            yesText = argd.yesText
        if(argd.hasOwnProperty("noText"))
            noText = argd.noText
        messageWin.showDialog(title, msg, callback, yesText, noText, type)
    }

    // ========================= 【内部】 =========================

    MessageWin{ id: messageWin }
    MessageSimple { id: messageSimple }
}