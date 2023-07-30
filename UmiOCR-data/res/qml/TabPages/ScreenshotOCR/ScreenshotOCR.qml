// ==============================================
// =============== 功能页：截图OCR ===============
// ==============================================

import QtQuick 2.15

import ".."
import "../../Widgets"

TabPage {
    id: tabPage

    // ========================= 【逻辑】 =========================

    function screenshot() {
        const grabList = tabPage.callPy("screenshot")
        ssWindowManager.create(grabList)
    }
    
    // TODO: 测试用
    Timer {
        interval: 200
        running: true
        onTriggered: {
            screenshot()
        }
    }

    // 截图窗口管理器
    ScreenshotWindowManager{ id: ssWindowManager }

    // ========================= 【布局】 =========================

    // 左控制栏
    Rectangle {
        id: leftCtrlPanel
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.margins: theme.spacing
        width: 32

        Column {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: theme.spacing

            Item {
                anchors.left: parent.left
                anchors.right: parent.right
                height: width
            }

            IconButton {
                anchors.left: parent.left
                anchors.right: parent.right
                height: width
                icon_: "screenshot"
                color: theme.textColor
                toolTip: qsTr("屏幕截图")
                onClicked: {
                    tabPage.screenshot()
                }
            }
            IconButton {
                anchors.left: parent.left
                anchors.right: parent.right
                height: width
                icon_: "paste"
                color: theme.textColor
                toolTip: qsTr("粘贴图片")
            }
        }
        // color: "red"
    }
    // 主区域：双栏面板
    DoubleColumnLayout {
        anchors.left: leftCtrlPanel.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        initSplitterX: 0.5

        // 左面板
        leftItem: Panel {
            anchors.fill: parent

            Image {
                anchors.fill: parent
                source: "image://pixmapprovider/123"
            }
        }

        // 右面板
        rightItem: Panel {
            anchors.fill: parent
        }
    }
}