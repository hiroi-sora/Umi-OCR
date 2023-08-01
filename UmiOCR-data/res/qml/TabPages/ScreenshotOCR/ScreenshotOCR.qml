// ==============================================
// =============== 功能页：截图OCR ===============
// ==============================================

import QtQuick 2.15

import ".."
import "../../Widgets"
import "../../Widgets/ResultLayout"

TabPage {
    id: tabPage
    // 配置
    ScreenshotOcrConfigs { id: screenshotOcrConfigs } 
    configsComp: screenshotOcrConfigs

    // ========================= 【逻辑】 =========================

    // 开始截图
    function screenshot() {
        const grabList = tabPage.callPy("screenshot")
        ssWindowManager.create(grabList)
    }

    // 截图完毕
    function screenshotEnd(argd) {
        const x = argd["clipX"], y = argd["clipY"], w = argd["clipW"], h = argd["clipH"]
        if(x < 0 || y < 0 || w <= 0 || h <= 0) // 裁切区域无实际像素
            return
        const configDict = screenshotOcrConfigs.getConfigValueDict()
        const clipID = tabPage.callPy("screenshotEnd", argd, configDict)
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
        // running: true
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

            TabPanel {
                id: tabPanel
                anchors.fill: parent
                anchors.margins: theme.spacing

                // 结果面板
                ResultsTableView {
                    id: resultsTableView
                    anchors.fill: parent
                    visible: false
                }

                tabsModel: [
                    {
                        "key": "configs",
                        "title": qsTr("设置"),
                        "component": screenshotOcrConfigs.panelComponent,
                    },
                    {
                        "key": "ocrResult",
                        "title": qsTr("记录"),
                        "component": resultsTableView,
                    },
                ]
            }
        }
    }
}