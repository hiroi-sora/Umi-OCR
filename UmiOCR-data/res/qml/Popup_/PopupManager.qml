// =========================================
// =============== 弹窗管理器 ===============
// =========================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15 // 阴影

import "../Widgets"

Item {
    // ========================= 【对外接口】 =========================

    // 显示简单通知
    function showSimple(title, msg) {
        simpleNotificationPopup.show(title, msg)
    }

    // ========================= 【内部】 =========================

    SimpleNotificationPopup { id:simpleNotificationPopup }
}