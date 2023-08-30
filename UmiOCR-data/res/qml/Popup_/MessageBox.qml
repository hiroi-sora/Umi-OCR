// ==============================================
// =============== 带确认的消息盒子 ===============
// ==============================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15 // 阴影

import "../Widgets"

Rectangle {
    id: msgRoot

    // ========================= 【参数】 =========================

    // 常规参数
    property string title: "" // 标题
    property string msg: "" // 内容
    property var onClosed: undefined // 关闭函数，外部传入
    property string type: "" // 可选：""默认， "warning"警告， "error"错误
    // 定制参数
    property int shadowWidth: theme.spacing * 3 // 边缘阴影宽度
    property string icon: "bell" // 图标
    property color iconColor: theme.themeColor2 // 图标前景颜色
    property color iconBgColor: theme.coverColor1 // 图标背景颜色
    property var btnsList: [ // 按钮列表
        // text 显示文本， value 点击返回的值， textColor 文本颜色， bgColor 背景颜色
        {"text":qsTr("取消"), "value": false, "textColor": theme.subTextColor, "bgColor": theme.bgColor},
        {"text":qsTr("确定"), "value": true, "textColor": theme.themeColor3, "bgColor": theme.themeColor1},
    ]
    // 自动类型参数
    Component.onCompleted: {
        switch(type) {
            case "warning":
                icon = "warning"
                iconColor = theme.noColor
                if(title==="")
                    title=qsTr("警告")
                break
            case "error":
                icon = "no"
                iconColor = theme.noColor
                if(title==="")
                    title=qsTr("发生了一点小问题")
                break
        }
    }
    

    // ===========================================================

    width: theme.textSize * 20
    height: childrenRect.height
    color: theme.bgColor
    radius: theme.panelRadius

    // 列布局
    Column {
        anchors.left: parent.left
        anchors.right: parent.right
        spacing: theme.spacing
        // 顶部占位
        Item {
            width: 1
            height: 1
        }
        // 图标
        Rectangle {
            width: theme.textSize*3
            height: theme.textSize*3
            anchors.horizontalCenter: parent.horizontalCenter
            color: iconBgColor
            radius: 99999

            Icon_ {
                width: parent.height*0.6
                height: parent.height*0.6
                anchors.centerIn: parent
                color: iconColor
                icon: msgRoot.icon
            }
        }
        // 标题
        Text_ {
            id: textTitle
            anchors.horizontalCenter: parent.horizontalCenter
            font.pixelSize: theme.largeTextSize
            visible: title!==""
            text: title
        }
        // 内容
        Text_ {
            id: textMsg
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: theme.textSize
            wrapMode: TextEdit.Wrap // 尽量在单词边界处换行
            horizontalAlignment: Text.AlignHCenter // 水平居中
            visible: msg!==""
            text: msg
        }
        // 底部占位
        Item {
            width: 1
            height: 1
        }
        // 底部按钮
        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            height: theme.textSize*2+theme.spacing*2
            color: theme.coverColor1
        
            Row {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.margins: theme.spacing

                property real lrMargin: theme.spacing*4
                spacing: theme.spacing
                property int childrenWidth: 10
                Component.onCompleted: { // 计算子级宽度
                    const n = btnsList.length
                    if(n==1){ // 单个按钮，宽度为一半
                        width = parent.width / 2
                        childrenWidth = width
                    }
                    else { // 多个按钮，宽度平均分配
                        width = parent.width - lrMargin
                        childrenWidth = (width - (n - 1) * spacing) / n
                    }
                }
                

                Repeater {
                    model: btnsList
                    Button_ {
                        property var info: btnsList[index]
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        width: parent.childrenWidth
                        text_: info.text
                        bgColor_: info.bgColor?info.bgColor:theme.bgColor
                        textColor_: info.textColor?info.textColor:theme.subTextColor
                        onClicked: {
                            if(typeof onClosed === "function")
                                onClosed(info.value) // 调用关闭函数
                        }
                    }
                }
            }
        }
        // 内圆角裁切
        layer.enabled: true
        layer.effect: OpacityMask {
            maskSource: Rectangle {
                width: msgRoot.width
                height: msgRoot.height
                radius: msgRoot.radius
            }
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