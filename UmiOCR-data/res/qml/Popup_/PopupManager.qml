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

    // ========================= 【内部】 =========================

    MessageWin{ id: messageWin }
    MessageSimple { id: messageSimple }
}