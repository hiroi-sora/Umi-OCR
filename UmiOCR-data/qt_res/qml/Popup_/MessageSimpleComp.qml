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
    property int shadowWidth: size_.spacing * 3 // 边缘阴影宽度
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

    width: size_.text * 20
    height: textTitle.height + textMsg.height+size_.spacing*2
    color: theme.themeColor1
    radius: size_.panelRadius
    // 内容组件
    Item {
        anchors.fill: parent
        anchors.margins: size_.spacing
        // 倒计时 ▽按钮
        HProgressBar {
            id: timerProgressBar
            anchors.top: parent.top
            anchors.right: parent.right
            height: size_.smallText
            width: size_.smallText*2
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
            color: theme.themeColor3
            height: size_.text
            width: size_.text
        }
        // 标题文字
        Text_ {
            id: textTitle
            anchors.top: parent.top
            anchors.left: iconComp.right
            anchors.leftMargin: size_.text*0.5
            height: size_.text
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
        onClicked: {
            timer.stop() // 停止计时器
            if(typeof onHided === "function")
                onHided() // 调用关闭函数
        }
    }
    // 边缘阴影
    layer.enabled: qmlapp.enabledEffect && shadowWidth>0
    layer.effect: DropShadow {
        transparentBorder: true
        color: theme.coverColor4
        samples: shadowWidth
    }
}