// ==============================================
// =============== 功能页：二维码 ===============
// ==============================================

import QtQuick 2.15

import ".."
import "../../Widgets"
import "../../Widgets/ResultLayout"
import "../../Widgets/ImageViewer"

TabPage {
    id: tabPage
    // 配置
    configsComp: QRCodeConfigs {}

    // ========================= 【逻辑】 =========================

    // 开始截图
    function screenshot() {
        qmlapp.imageManager.screenshot(screenshotEnd)
    }
    // 截图完毕
    function screenshotEnd(clipID) {
        popMainWindow()
        if(!clipID) {
            return
        }
        const configDict = configsComp.getValueDict()
        tabPage.callPy("scanImgID", clipID, configDict)
        qmlapp.tab.showTabPageObj(tabPage) // 切换标签页
    }

    // 开始粘贴
    function paste() {
        popMainWindow()
        const res = qmlapp.imageManager.getPaste()
        if(res.error) {
            qmlapp.popup.simple(qsTr("获取剪贴板异常"), res.error)
            return
        }
        if(res.text) {
            qmlapp.popup.simple(qsTr("剪贴板中为文本"), res.text)
            return
        }
        qmlapp.tab.showTabPageObj(tabPage) // 切换标签页
        if(res.imgID) { // 图片
            imageText.showImgID(res.imgID)
            const configDict = configsComp.getValueDict()
            tabPage.callPy("scanImgID", res.imgID, configDict)
        }
        else if(res.paths) { // 地址
            scanPaths(res.paths)
        }
    }

    // 对一批图片路径做扫码
    function scanPaths(paths) {
        paths = qmlapp.utilsConnector.findImages(paths, false)
        if(!paths || paths.length < 1) {
            qmlapp.popup.simple(qsTr("无有效图片"), "")
            return
        }
        const configDict = configsComp.getValueDict()
        const simpleType = configDict["other.simpleNotificationType"]
        qmlapp.popup.simple(qsTr("导入%1条图片路径").arg(paths.length), "", simpleType)
        imageText.showPath(paths[0])
        tabPage.callPy("scanPaths", paths, configDict)
    }

    // 弹出主窗口
    function popMainWindow() {
        // 等一回合再弹，防止与收回截图窗口相冲突
        if(configsComp.getValue("action.popMainWindow"))
            Qt.callLater(()=>qmlapp.mainWin.setVisibility(true))
    }

    // 生成二维码
    function writeBarcode(text) {
        if(!text || text.length===0)
            return
        setRunning(true)
        const configDict = configsComp.getValueDict()
        const format = configDict["writeBarcode.format"]
        const w = configDict["writeBarcode.width"]
        const h = configDict["writeBarcode.height"]
        const quiet_zone = configDict["writeBarcode.quiet_zone"]
        const ec_level = configDict["writeBarcode.ec_level"]
        const imgID = tabPage.callPy("writeBarcode", text, format, w, h, quiet_zone, ec_level)
        setRunning(false)
        if(imgID.startsWith("[Error]") || imgID.startsWith("[Warning]")) {
            if(imgID.startsWith("[Error] [")) {
                const msg = qsTr("参数有误，或输入内容不合规定。请参照报错指示修改：") +"\n"+ imgID
                qmlapp.popup.message(qsTr("生成二维码失败"), msg, "error")
            }
            else {
                qmlapp.popup.message(qsTr("生成二维码失败"), imgID, "error")
            }
            return
        }
        imageText.showImgID(imgID)
    }

    // ========================= 【python调用qml】 =========================

    // 获取一个扫码的返回值
    function onQRCodeGet(res, imgID="", imgPath="") {
        // 添加到结果
        if(imgID) // 图片类型
            imageText.showImgID(imgID)
        else if(imgPath) // 地址类型
            imageText.showPath(imgPath)
            // 路径转文件名
            const parts = imgPath.split("/")
            res.title = parts[parts.length - 1]
        imageText.showTextBoxes(res)
        const resText = resultsTableView.addOcrResult(res)
        // 若tabPanel面板的下标没有变化过，则切换到记录页
        if(tabPanel.indexChangeNum < 2)
            tabPanel.currentIndex = 1
        // 复制到剪贴板
        const copy = configsComp.getValue("action.copy")
        if(copy && resText!="") 
            qmlapp.utilsConnector.copyText(resText)
        // 弹出通知
        showSimple(res, resText, copy)
        // 升起主窗口
        popMainWindow()
    }

    // 任务完成后发送通知
    function showSimple(res, resText, isCopy) {
        // 获取弹窗类型
        let simpleType = configsComp.getValue("other.simpleNotificationType")
        if(simpleType==="default") {
            simpleType = qmlapp.globalConfigs.getValue("window.simpleNotificationType")
        }
        const code = res.code
        const time = res.time.toFixed(2)
        let title = ""
        resText = resText.replace(/\n/g, " ") // 换行符替换空格
        if(code === 100 || code === 101) { // 成功时，不发送内部弹窗
            if(simpleType==="inside" || simpleType==="onlyInside")
                if(qmlapp.mainWin.getVisibility()) 
                    return
        }
        if(code === 100) {
            if(isCopy) title = qsTr("已复制到剪贴板")
            else title = qsTr("识图完成")
        }
        else if(code === 101) {
            title = qsTr("无文字")
            resText = ""
        }
        else {
            title = qsTr("识别失败")
        }
        title += `  -  ${time}s`
        qmlapp.popup.simple(title, resText, simpleType)
    }

    // 设置运行状态
    function setRunning(flag) {
        running = flag
    }

    // ========================= 【事件管理】 =========================

    Component.onCompleted: {
        eventSub() // 订阅事件
    }
    // 关闭页面
    function closePage() {
        eventUnsub()
        delPage()
    }
    // 订阅事件
    function eventSub() {
        qmlapp.pubSub.subscribeGroup("<<qrcode_screenshot>>", this, "screenshot", ctrlKey)
        qmlapp.pubSub.subscribeGroup("<<qrcode_paste>>", this, "paste", ctrlKey)
        qmlapp.systemTray.addMenuItem("<<qrcode_screenshot>>", qsTr("扫描二维码"), screenshot)
    }
    // 取消订阅事件
    function eventUnsub() {
        qmlapp.systemTray.delMenuItem("<<qrcode_screenshot>>")
        qmlapp.pubSub.unsubscribeGroup(ctrlKey)
    }

    // ========================= 【布局】 =========================
    property bool running: false
    // 主区域：双栏面板
    DoubleRowLayout {
        id: doubleRowLayout
        saveKey: "QRCode_1"
        anchors.fill: parent
        initSplitterX: 0.5

        // 左面板
        leftItem: Panel {
            anchors.fill: parent
            clip: true
            // 顶部控制栏
            Item  {
                id: dLeftTop
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.topMargin: size_.smallSpacing
                height: size_.line * 1.5
                // 靠左
                Row {
                    id: dLeftTopL
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.leftMargin: size_.spacing
                    spacing: size_.smallSpacing

                    IconButtonBar {
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        btnList: [
                            {
                                icon: "screenshot",
                                onClicked: tabPage.screenshot,
                                color: theme.textColor,
                                toolTip: tr("屏幕截图"),
                            },
                            {
                                icon: "paste",
                                onClicked: tabPage.paste,
                                color: theme.textColor,
                                toolTip: tr("粘贴图片"),
                            },
                        ]
                    }
                }
                // 靠右
                Row {
                    id: dLeftTopR
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.rightMargin: size_.spacing
                    spacing: size_.smallSpacing
                    visible: dLeftTop.width > dLeftTopL.width + dLeftTopR.width

                    IconButtonBar {
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        btnList: [
                            {
                                icon: "menu",
                                onClicked: imageText.popupMenu,
                                toolTip: tr("右键菜单"),
                            },
                            {
                                icon: "save",
                                onClicked: imageText.saveImage,
                                toolTip: tr("保存图片"),
                            },
                            {
                                icon: "full_screen",
                                onClicked: imageText.imageFullFit,
                                toolTip: tr("图片大小：适应窗口"),
                            },
                            {
                                icon: "one_to_one",
                                onClicked: imageText.imageScaleAddSub,
                                toolTip: tr("图片大小：实际"),
                            },
                        ]
                    }
                    // 百分比显示
                    Text_ {
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignRight
                        text: (imageText.scale*100).toFixed(0) + "%"
                        color: theme.subTextColor
                        width: size_.line * 2.5
                    }
                }
            }
            // 图片预览区域
            ImageWithText {
                id: imageText
                anchors.top: dLeftTop.bottom
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: size_.spacing
                anchors.topMargin: size_.smallSpacing

                // 加载中 动态图标
                Loading {
                    text: "Running"
                    visible: running
                    anchors.centerIn: parent
                }
                // 提示
                DefaultTips {
                    visibleFlag: running
                    anchors.fill: parent
                    tips: qsTr("截图、拖入或粘贴二维码图片")
                }
            }
        }

        // 右面板
        rightItem: Panel {
            anchors.fill: parent

            TabPanel {
                id: tabPanel
                anchors.fill: parent
                anchors.margins: size_.spacing

                // 结果面板
                ResultsTableView {
                    id: resultsTableView
                    anchors.fill: parent
                    visible: false
                }

                //生成面板
                Item {
                    id: writePanel
                    anchors.fill: parent
                    visible: false
                    Item {
                        id: writePanelTop
                        anchors.top: parent.top
                        anchors.left: parent.left
                        anchors.right: parent.right
                        height: size_.line * 2 + size_.smallSpacing * 2
                        Button_ {
                            id: writePanelBtn1
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            anchors.left: parent.left
                            anchors.margins: size_.smallSpacing
                            text_: qsTr("设置")
                            onClicked: {
                                tabPanel.currentIndex = 0 // 转到设置面板
                                configsComp.panelComponent.scrollToGroup(3) // 滚动到生成设置
                            }
                        }
                        Row {
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            anchors.right: parent.right
                            anchors.margins: size_.smallSpacing
                            CheckButton {
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                text_: qsTr("自动刷新")
                                toolTip: qsTr("修改文字后，自动生成二维码/条形码")
                                visible: writePanelTop.width > writePanelBtn1.width+writePanelBtn2.width+this.width
                                textColor_: theme.textColor
                                checked: writeEdit.autoUpdate
                                enabledAnime: true
                                onCheckedChanged: {
                                    writeEdit.autoUpdate = checked
                                }
                            }
                            Button_ {
                                id: writePanelBtn2
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                text_: qsTr("刷新")
                                toolTip: qsTr("生成二维码/条形码")
                                onClicked: writeBarcode(writeEdit.text)
                            }
                        }
                    }
                    Rectangle {
                        anchors.top: writePanelTop.bottom
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        color: theme.bgColor
                        border.width: 1
                        border.color: theme.coverColor4
                        TextEdit_ {
                            id: writeEdit
                            anchors.fill: parent
                            anchors.margins: size_.spacing
                            // 自动刷新
                            property bool autoUpdate: true
                            // 文字输入改变时，等待一段时间，自动刷新
                            Timer {
                                id: writeEditTimer
                                interval: 500  // 0.5 秒
                                repeat: false
                                onTriggered: writeBarcode(writeEdit.text)
                            }
                            onTextChanged: {
                                if(autoUpdate) // 重启计时器
                                    writeEditTimer.restart()
                            }
                        }
                    }
                }

                tabsModel: [
                    {
                        "key": "configs",
                        "title": qsTr("设置"),
                        "component": configsComp.panelComponent,
                    },
                    {
                        "key": "ocrResult",
                        "title": qsTr("记录"),
                        "component": resultsTableView,
                    },
                    {
                        "key": "writePanel",
                        "title": qsTr("生成"),
                        "component": writePanel,
                    },
                ]
            }
        }
    }

    // 鼠标拖入图片
    DropArea_ {
        anchors.fill: parent
        callback: tabPage.scanPaths
    }
}