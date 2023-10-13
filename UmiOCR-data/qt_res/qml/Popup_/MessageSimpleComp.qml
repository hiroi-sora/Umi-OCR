// =============================================
// =============== 简单消息的界面 ===============
// =============================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15 // 阴影

import "../Widgets"

Rectangle {
    id: spMsg

    property var onHided: undefined // 关闭函数，外部传入
    function show(title, msg, time=5000, icon="bell") {
        textTitle.text = title
        textMsg.text = msg
        nowTime = 0
        allTime = time>0?time:1 // 防止除0
        timerProgressBar.percent = 0
        iconComp.icon = icon // 图标
        timer.start() // 启动计时器
    }

    property int allTime: 1 // 总时间
    property int nowTime: 0 // 当前时间
    property int interval: 10 // 间隔刷新
    property int shadowWidth: qmlapp.enabledEffect ? size_.spacing*3 : 0 // 边缘阴影宽度
    Timer {
        id: timer
        interval: spMsg.interval // 间隔
        running: false
        repeat: true // 重复执行
        onTriggered: {
            spMsg.nowTime += spMsg.interval
            timerProgressBar.percent = spMsg.nowTime/spMsg.allTime
            if(spMsg.nowTime>=spMsg.allTime) {
                timer.stop() // 停止计时器
                if(typeof onHided === "function")
                    onHided() // 调用关闭函数
                return
            }
        }
    }

    width: size_.line * 20
    height: textTitle.height + textMsg.height+size_.spacing*2
    color: theme.specialBgColor
    radius: qmlapp.enabledEffect ? size_.panelRadius : 0
    // 内容组件
    Item {
        anchors.fill: parent
        anchors.margins: size_.spacing
        // 倒计时 ▽按钮
        HProgressBar {
            id: timerProgressBar
            anchors.top: parent.top
            anchors.right: parent.right
            height: size_.smallLine
            width: size_.smallLine*2
            color: theme.coverColor1
            highlightColor: theme.coverColor2
            radius: size_.btnRadius
            percent: 0
            // 鼠标悬浮背景
            Rectangle {
                id: btnHoverBg
                visible: false
                anchors.fill: parent
                color: theme.coverColor2
                radius: size_.btnRadius
            }
            // 下箭头图标
            Icon_ {
                anchors.fill: parent
                icon: "down"
                color: theme.bgColor
            }
        }
        // 标题图标
        Icon_ {
            id: iconComp
            anchors.top: parent.top
            anchors.left: parent.left
            color: theme.specialTextColor
            height: size_.line
            width: size_.line
        }
        // 标题文字
        Text_ {
            id: textTitle
            anchors.top: parent.top
            anchors.left: iconComp.right
            anchors.leftMargin: size_.line*0.5
            height: size_.line
            verticalAlignment: Text.AlignVCenter // 垂直居中
        }
        // 内容文字
        Text_ {
            id: textMsg
            anchors.top: textTitle.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.topMargin: size_.smallSpacing
            color: theme.subTextColor
            font.pixelSize: size_.smallText
            wrapMode: TextEdit.Wrap // 尽量在单词边界处换行
            maximumLineCount: 2 // 限制显示两行
            height: text=="" ? 0:undefined // 无文字时高为0，有文字时自动高度

        }
    }
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onEntered: {
            btnHoverBg.visible = true
        }
        onExited: {
            btnHoverBg.visible = false
        }
        function mouseClicked() {
            timer.stop() // 停止计时器
            if(typeof onHided === "function")
                onHided() // 调用关闭函数
        }
        // 单击隐藏弹窗
        onClicked: mouseClicked()
        // 双击弹出主窗，隐藏弹窗
        onDoubleClicked: {
            qmlapp.mainWin.setVisibility(true) // 主窗可见
            mouseClicked()
        }
    }
    // 边缘阴影
    layer.enabled: shadowWidth>0
    layer.effect: DropShadow {
        transparentBorder: true
        color: theme.coverColor4
        samples: shadowWidth
    }
}