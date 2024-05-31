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
    function runFinished(allNum) { // 任务开始，传入总任务数
        state_ = "run"
        isWaiting = false
        timer.start() // 新开始计时
        msnNowNum = 0 // 刷新任务计数
        msnAllNum = allNum
        timer.updateNumber() // 刷新任务计数文本
    }
    function pauseFinished() { // 暂停
        state_ = "pause"
        isWaiting = false
        timer.pause() // 暂停计时
        timer.updateNumber() // 刷新任务计数文本
    }
    function resumeFinished() { // 恢复
        state_ = "run"
        isWaiting = false
        timer.resume() // 恢复计时
        timer.updateNumber() // 刷新任务计数文本
    }
    function stopFinished() { // 停止
        state_ = "stop"
        isWaiting = false
        timer.pause() // 暂停计时
        timer.updateNumber() // 刷新任务计数文本
    }
    function msnStep(step=1) { // 任务计数步进
        msnNowNum += step
        if(msnNowNum > msnAllNum) msnNowNum = msnAllNum
        timer.updateNumber() // 刷新任务计数文本
    }

    // 任务状态
    property string state_: "stop" // 当前状态， stop run pause
    property bool isWaiting: false // 等待回调中
    // 任务计数
    property int msnAllNum: 0 // 总任务数
    property int msnNowNum: 0 // 当前已完成任务数
    clip: true

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
        Item {
            id: btn1
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            width: qmlapp.enabledEffect?ctrlRight.width_:(
                state_==="stop"?ctrlRight.width_:ctrlRight.width_*0.5)

            Button_ {
                visible: state_ === "stop" && !isWaiting
                anchors.fill: parent
                bold_: true
                bgColor_: theme.coverColor1
                bgHoverColor_: theme.coverColor2
                text_: qsTr("开始任务")
                onClicked: {
                    if(isWaiting) return
                    isWaiting = true
                    Qt.callLater(runClicked)
                }
            }
            IconButton {
                visible: state_ !== "stop" || isWaiting
                anchors.fill: parent
                color: theme.textColor
                bgColor_: theme.coverColor1
                bgHoverColor_: theme.coverColor2
                margins: size_.spacing
                icon_: isWaiting?"wait":(state_==="run" ? "pause" : "run")
                toolTip: (state_==="run" ? qsTr("暂停任务\n暂停后可以待机或休眠。\n但是关机或退出软件，将会丢弃任务内容。") :
                    qsTr("继续任务"))
                onClicked: {
                    if(isWaiting) return
                    isWaiting = true
                    switch(state_) {
                        case "run": Qt.callLater(pauseClicked); return;
                        case "pause": Qt.callLater(resumeClicked); return;
                    }
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
        IconButton {
            id: btn2
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.left: btn1.right
            anchors.leftMargin: size_.smallSpacing
            visible: width > 1
            color: theme.noColor
            bgColor_: theme.coverColor1
            bgHoverColor_: theme.coverColor2
            margins: size_.spacing
            icon_: isWaiting?"wait":"stop"
            toolTip: qsTr("终止任务\n放弃未完成的内容。")
            onClicked: {
                if(isWaiting) return
                isWaiting = true
                Qt.callLater(stopClicked)
            }
        }
    }
    // 左：文字/进度条
    Item {
        id: ctrlLeft
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: ctrlRight.left
        anchors.rightMargin: size_.spacing
        Item {
            id: ctrlLeftTop
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: size_.line

            Row {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.right: parent.right
                spacing: size_.line

                // 计时器、任务计数器
                Text_ {
                    id: timer
                    text: `${strState}  ${strTime}  ${strNumber}`
                    color: timer_.running?theme.textColor:(missionCtrl.msnNowNum<missionCtrl.msnAllNum?theme.noColor:theme.yesColor)
                    font.pixelSize: size_.smallText
                    verticalAlignment: Text.AlignVCenter // 垂直居中
                    property string strState: "" // 状态文本， "已暂停"
                    property string strTime: "" // 时间文本
                    property string strNumber: "" // 任务数量文本， 23/100
                    // 新开始计时
                    function start() {
                        timer_.running = true
                        startStamp = getTimestamp()
                        runTime = pauseTime = 0
                        updateTime()
                    }
                    // 暂停
                    function pause() {
                        timer_.running = false
                        pauseStartStamp = getTimestamp()
                        updateTime()
                    }
                    // 恢复计时
                    function resume() {
                        timer_.running = true
                        const t = getTimestamp()
                        pauseTime += t-pauseStartStamp // 累加暂停时长
                        updateTime()
                    }
                    // 获取时间戳
                    function getTimestamp() {
                        return (new Date()).getTime() / 1000
                    }
                    // 刷新时间
                    function updateTime() {
                        if(runTime < 0.1) {
                            strTime = "" // 时间太短，不显示
                            return
                        }
                        let s = ""
                        let minutes = Math.floor(runTime / 60)
                        let seconds = Math.floor(runTime % 60)
                        if(minutes < 10) minutes = "0"+minutes
                        if(seconds < 10) seconds = "0"+seconds
                        strTime = minutes + ':' + seconds
                    }
                    // 刷新数量、显示文本
                    function updateNumber() {
                        // n="23/100" , p="已停止"
                        let n = `${missionCtrl.msnNowNum}/${missionCtrl.msnAllNum}`
                        let p = ""
                        // 运行中
                        if(missionCtrl.state_ === "run") {
                            if(missionCtrl.msnNowNum < missionCtrl.msnAllNum)
                                p = qsTr("正在运行")
                            else
                                p = qsTr("正在保存") // 所有任务处理完毕，但任务队列未返回结束
                        }
                        // 暂停中
                        else if(missionCtrl.state_ === "pause") {
                            p = qsTr("已暂停")
                        }
                        // 已停止
                        else if(missionCtrl.state_ === "stop") {
                            if(missionCtrl.msnNowNum <= 0)
                                n = p = ""
                            else if(missionCtrl.msnNowNum < missionCtrl.msnAllNum)
                                p = qsTr("任务停止")
                            else
                                p = qsTr("任务完成")
                        }
                        // 刷新
                        timer.strNumber = n
                        timer.strState = p
                        if(missionCtrl.msnAllNum > 0)
                            missionProgress.percent = missionCtrl.msnNowNum/missionCtrl.msnAllNum
                    }

                    property real startStamp // 开始时间戳，秒
                    property real pauseStartStamp // 本次暂停开始的时间戳，秒
                    property real pauseTime // 暂停时长，秒
                    property real runTime // 运行时长，秒
                    property bool isPause: false // 是否正在暂停
                    Timer {
                        id: timer_
                        interval: 100 // 更新间隔
                        repeat: true
                        running: false
                        onTriggered: {
                            // 刷新运行时长
                            const timestamp = timer.getTimestamp()
                            timer.runTime = timestamp-timer.startStamp-timer.pauseTime
                            timer.updateTime()
                        }
                    }
                }
            }
        }

        HProgressBar {
            id: missionProgress
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottomMargin: size_.line * 0.1
            height: size_.line * 0.5
            highlightColor: missionCtrl.state_==="run"?theme.yesColor:theme.coverColor4
            color: theme.bgColor
            percent: 0
        }
    }
}