// ==============================================
// =============== 功能页：截图OCR ===============
// ==============================================

import QtQuick 2.15

import ".."
import "../../Widgets"

TabPage {
    id: tabPage

    // ========================= 【逻辑】 =========================

    // 开始截图
    function screenshot() {
        const grabList = tabPage.callPy("screenshot")
        ssWindowManager.create(grabList)
    }

    // 截图完毕
    function screenshotEnd(argd) {
        const clipID = tabPage.callPy("screenshotEnd", argd)
        if(clipID.startsWith("[Error]")) {
            qmlapp.popup.message(qsTr("截图裁切异常"), clipID, "error")
            return
        }
        console.log("裁切成功", clipID)
        showImage.source = "image://pixmapprovider/"+clipID
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
    ScreenshotWindowManager{
        id: ssWindowManager
        screenshotEnd: tabPage.screenshotEnd
    }

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
                id: showImage
                anchors.fill: parent
                fillMode: Image.PreserveAspectFit
                source: ""
            }
        }

        // 右面板
        rightItem: Panel {
            anchors.fill: parent
        }
    }
}