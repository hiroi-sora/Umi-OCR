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
    property int shadowWidth: theme.spacing * 3 // 边缘阴影宽度
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

    width: theme.textSize * 20
    height: childrenRect.height+theme.spacing*2
    color: theme.themeColor1
    radius: theme.panelRadius
    // 内容组件
    Item {
        height: childrenRect.height
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: theme.spacing
        // 倒计时 ▽按钮
        HProgressBar {
            id: timerProgressBar
            anchors.top: parent.top
            anchors.right: parent.right
            height: theme.smallTextSize
            width: theme.smallTextSize*2
            color: theme.coverColor1
            highlightColor: theme.coverColor2
            radius: theme.btnRadius
            percent: 0
            // 鼠标悬浮背景
            Rectangle {
                id: btnHoverBg
                visible: false
                anchors.fill: parent
                color: theme.coverColor2
                radius: theme.btnRadius
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
            color: theme.themeColor2
            height: theme.textSize
            width: theme.textSize
        }
        // 标题文字
        Text_ {
            id: textTitle
            anchors.top: parent.top
            anchors.left: iconComp.right
            anchors.leftMargin: theme.textSize*0.5
            height: theme.textSize
            verticalAlignment: Text.AlignVCenter // 垂直居中
        }
        // 内容文字
        Text_ {
            id: textMsg
            anchors.top: textTitle.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.topMargin: theme.smallSpacing
            color: theme.subTextColor
            font.pixelSize: theme.smallTextSize
            wrapMode: TextEdit.Wrap // 尽量在单词边界处换行
            maximumLineCount: 2 // 限制显示两行
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
            onClicked: {
                if(typeof onHided === "function")
                    onHided() // 调用关闭函数
            }
        }
    }
    // 边缘阴影
    layer.enabled: theme.enabledEffect && shadowWidth>0
    layer.effect: DropShadow {
        transparentBorder: true
        color: theme.coverColor4
        samples: shadowWidth
    }
}