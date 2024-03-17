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
    property int shadowWidth: qmlapp.enabledEffect ? size_.spacing*3 : 0 // 边缘阴影宽度
    property string icon: "bell" // 图标
    property string iconColorKey: "specialTextColor" // 图标前景颜色
    property string iconBgColorKey: "coverColor1" // 图标背景颜色
    property var btnsList: [ // 按钮列表
        // text 显示文本， value 点击返回的值， textColor 文本颜色， bgColor 背景颜色
        {"text":qsTr("取消"), "value": false, "textColor": theme.subTextColor, "bgColor": theme.bgColor},
        {"text":qsTr("确定"), "value": true, "textColor": theme.specialTextColor, "bgColor": theme.specialBgColor},
    ]
    // 自动类型参数
    Component.onCompleted: {
        switch(type) {
            case "warning":
                icon = "warning"
                iconColorKey = "noColor"
                if(title==="")
                    title=qsTr("警告")
                break
            case "error":
                icon = "no"
                iconColorKey = "noColor"
                if(title==="")
                    title=qsTr("发生了一点小问题")
                break
        }
    }
    

    // ===========================================================

    width: size_.line * 25
    height: childrenRect.height
    color: theme.bgColor
    radius: qmlapp.enabledEffect ? size_.panelRadius : 0

    // 列布局
    Column {
        anchors.left: parent.left
        anchors.right: parent.right
        spacing: size_.spacing
        // 顶部占位
        Item {
            width: 1
            height: 1
        }
        // 图标
        Rectangle {
            width: size_.line*3
            height: size_.line*3
            anchors.horizontalCenter: parent.horizontalCenter
            color: theme[iconBgColorKey]
            radius: 99999

            Icon_ {
                width: parent.height*0.6
                height: parent.height*0.6
                anchors.centerIn: parent
                color: theme[iconColorKey]
                icon: msgRoot.icon
            }
        }
        // 标题
        Text_ {
            id: textTitle
            anchors.horizontalCenter: parent.horizontalCenter
            font.pixelSize: size_.largeText
            visible: title!==""
            text: title
        }
        // 内容
        Text_ {
            id: textMsg
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: size_.line
            wrapMode: TextEdit.Wrap // 尽量在单词边界处换行
            horizontalAlignment: Text.AlignHCenter // 水平居中
            visible: msg!==""
            text: msg
        }
        // 下层小按钮
        Item {
            anchors.left: parent.left
            anchors.right: parent.right
            height: type==="error"?size_.line:1
            // 错误
            Row {
                visible: type==="error"
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.right: parent.right
                anchors.rightMargin: size_.spacing
                Button_ {
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    text_: qsTr("复制")
                    textSize: size_.smallText
                    textColor_: theme.subTextColor
                    onClicked: {
                        qmlapp.utilsConnector.copyText(msg)
                        qmlapp.popup.simple(qsTr("已复制报错信息 %1").arg(msg.length), qsTr("请前往 Issues 页面寻找解答或反馈"))
                    }
                }
                Button_ {
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    property string issueUrl: UmiAbout.reportIssueUrl
                    text_: "Issues"
                    toolTip: issueUrl
                    textSize: size_.smallText
                    textColor_: theme.subTextColor
                    onClicked: {
                        Qt.openUrlExternally(issueUrl)
                    }
                }
            }
        }
        // 底部按钮
        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            height: size_.line*2+size_.spacing*2
            color: theme.coverColor1
        
            Row {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.margins: size_.spacing

                property real lrMargin: size_.spacing*4
                spacing: size_.spacing
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
    layer.enabled: shadowWidth>0
    layer.effect: DropShadow {
        transparentBorder: true
        color: theme.coverColor4
        samples: shadowWidth
    }
}