// =========================================
// =============== 弹窗管理器 ===============
// =========================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15 // 阴影

import "../Widgets"

Item {
    property string gYesText: qsTr("确认") // 全局确定文本
    property string gNoText: qsTr("取消") // 全局取消文本

    // ========================= 【对外接口】 =========================

    // 显示简单通知，无需确认，计时自动消失
    function simple(title, msg, showType="default") {
        messageSimple.show(title, msg, showType)
    }

    // 显示带确认的通知弹窗
    // type可选: ""默认， "warning"警告， "error"错误
    function message(title, msg, type="") {
        messageWin.showMessage(title, msg, type)
    }

    // 带“不再提示”的通知弹窗
    // mid: 唯一标识一个提示
    function messageMemory(mid, title, msg, type="") {
        messageWin.showMessageMemory(mid, title, msg, type)
    }

    // 双选项对话窗（确定|取消）。需要传入回调函数，返回true/false
    // argd： {"yesText":"确定", "noText": "取消"}
    function dialog(title, msg, callback, type="", argd={}) {
        let yesText=gYesText, noText=gNoText
        if(argd.hasOwnProperty("yesText"))
            yesText = argd.yesText
        if(argd.hasOwnProperty("noText"))
            noText = argd.noText
        messageWin.showDialog(title, msg, callback, yesText, noText, type)
    }

    // 双选项对话窗，带倒计时，结束后调用确定按钮
    // argd： {"yesText":"确定", "noText": "取消", "time": 10}
    function dialogCountdown(title, msg, callback, type="", argd={}) {
        let yesText=gYesText, noText=gNoText, time=10000
        if(argd.hasOwnProperty("yesText"))
            yesText = argd.yesText
        if(argd.hasOwnProperty("noText"))
            noText = argd.noText
        if(argd.hasOwnProperty("time"))
            time = argd.time
        messageWin.showDialogCountdown(title, msg, callback, yesText, noText, type, time)
    }

    // 展示遮罩层
    function showMask(msg="", id="") {
        maskLayer.showMask(msg, id)
    }

    // 隐藏指定id的遮罩层
    function hideMask(id="") {
        maskLayer.hideMask(id)
    }

    // ========================= 【内部】 =========================

    MessageBoxWin{ id: messageWin }
    MessageSimple { id: messageSimple }
    MaskLayer{ id: maskLayer }
}