// ==============================================
// =============== 任务进度控制面板 ===============
// ==============================================

import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: missionCtrl
    // 信号
    signal runClicked // 点击 运行
    signal pauseClicked // 点击 暂停
    signal resumeClicked // 点击 恢复
    signal stopClicked // 点击 停止
    // 通知回调
    function runFinished() { // 开始
        state_ = "run"
        isWaiting = false
        // TODO: 清空、开始计时
    }
    function pauseFinished() { // 暂停
        state_ = "pause"
        isWaiting = false
        // TODO：暂停计时
    }
    function resumeFinished() { // 恢复
        state_ = "run"
        isWaiting = false
        // TODO：恢复计时计时
    }
    function stopFinished() { // 停止
        state_ = "stop"
        isWaiting = false
        // TODO：暂停计时
    }

    // 当前状态， stop run pause
    property string state_: "stop"
    // 等待回调中
    property bool isWaiting: false

    // 右：开始/暂停/停止按钮
    Item {
        id: ctrlRight
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        // 右栏宽度
        property real width_: size_.line * 8
        width: width_

        // 开始/暂停/恢复 按钮
        Button_ {
            id: btn1
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            width: qmlapp.enabledEffect?ctrlRight.width_:(
                state_==="stop"?ctrlRight.width_:ctrlRight.width_*0.5)
            bold_: true

            bgColor_: theme.coverColor1
            bgHoverColor_: theme.coverColor2
            text_: isWaiting?"...":(
                state_==="stop"?qsTr("开始任务"):(
                    state_==="run"?qsTr("暂停"):qsTr("恢复")
                )
            )
            onClicked: {
                if(isWaiting) return
                isWaiting = true
                switch(state_) {
                    case "stop": runClicked(); return;
                    case "run": pauseClicked(); return;
                    case "pause": resumeClicked(); return;
                }
            }
            // 动画
            PropertyAnimation on width { // 折叠一半
                running: qmlapp.enabledEffect && state_!=="stop"
                to: ctrlRight.width_*0.5
                duration: 80
                easing.type: Easing.InCubic
            }
            PropertyAnimation on width { // 展开全部
                running: qmlapp.enabledEffect && state_==="stop"
                to: ctrlRight.width_
                duration: 80
                easing.type: Easing.OutCubic
            }
        }
        // 停止 按钮
        Button_ {
            id: btn2
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.left: btn1.right
            anchors.leftMargin: size_.smallSpacing
            visible: width > 1
            bold_: true
            bgColor_: theme.coverColor1
            bgHoverColor_: theme.coverColor2
            textColor_: theme.noColor
            text_: isWaiting?"...":qsTr("停止")
            toolTip: qsTr("终止任务，放弃未完成的内容")
            onClicked: {
                if(isWaiting) return
                isWaiting = true
                stopClicked()
            }
        }
    }
    // 左：文字/进度条
    Item {
        id: ctrlLeft
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.right: ctrlRight.left
        anchors.left: parent.left
    }
}