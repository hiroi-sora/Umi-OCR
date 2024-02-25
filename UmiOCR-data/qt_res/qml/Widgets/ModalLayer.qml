// ===========================================
// =============== 模态弹窗基类 ===============
// ===========================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.0

Rectangle {
    id: mRoot
    visible: false
    color: theme.coverColor4
    property alias contentItem: mPanel.data
    property string closeText: qsTr("保存并返回") // 右上角关闭提示文本

    // Esc 退出
    focus: false
    onVisibleChanged: focus = visible
    Keys.enabled: true
    Keys.onEscapePressed: mRoot.visible = false
    Component.onCompleted: {
        if(!closeText)
            closeText = qsTr("返回")
        closeText += " (Esc)"
    }

    // 模糊效果
    // GaussianBlur {
    //     anchors.fill: parent
    //     source: mRoot.parent
    //     visible: qmlapp.enabledEffect
    //     cached: true
    //     radius: 8
    //     samples: 16
    // }
    // 底层鼠标事件
    MouseArea {
        id: bottomArea
        anchors.fill: parent
        onWheel: {} // 拦截滚轮事件
        hoverEnabled: true // 拦截悬停事件
        onClicked: mRoot.visible = false // 单击关闭面板
        cursorShape: Qt.PointingHandCursor
    }
    property bool inBottom: bottomArea.containsMouse
    // 关闭提示
    Item {
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.rightMargin: size_.line * 2
        anchors.topMargin: size_.line * 0.25
        Rectangle {
            id: closeIconRect
            anchors.right: parent.right
            width: size_.line * 1.5
            height: size_.line * 1.5
            radius: size_.btnRadius
            color: theme.bgColor
            Icon_ {
                anchors.fill: parent
                color: theme.noColor
                icon: "no"
            }
        }
        Text_ {
            visible: closeText
            anchors.right: closeIconRect.left
            anchors.rightMargin: size_.spacing
            anchors.verticalCenter: closeIconRect.verticalCenter
            text: closeText
            color: theme.bgColor
            font.pixelSize: size_.smallText
        }
    }

    // 内容面板
    Panel {
        id: mPanel
        anchors.fill: parent
        anchors.margins: size_.line * 2
        color: theme.bgColor
        // 面板拦截鼠标事件
        MouseArea {
            id: panelArea
            anchors.fill: parent
            // hoverEnabled: true
            onClicked: {}
        }
    }
}