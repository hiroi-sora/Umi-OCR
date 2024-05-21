// ==============================================
// =============== 功能页：批量OCR ===============
// ==============================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import ".."
import "../../Widgets"
import "../../Widgets/ResultLayout"
import "../../Widgets/IgnoreArea"

TabPage {
    id: tabPage

    // ========================= 【逻辑】 =========================

    property int errorNum: 0 // 异常的任务个数
    property string msnID: "" // 当前任务ID

    Component.onCompleted: {
    }
    // TODO: 测试用
    // Timer {
    //     interval: 200
    //     running: true
    //     onTriggered: {
    //         addImages(
    //             [
    //                 "D:/Pictures/Screenshots/test",
    //             ]
    //         )
    //         console.log("自动添加！！！！！！！！！！！！！")
    //         // ocrStart()
    //     }
    // }

    // 将需要查询的图片路径列表paths发送给python。传入值是没有 file:/// 开头的纯字符串的列表。
    function addImages(paths) {
        if(ctrlPanel.state_ !== "stop") return
        // 调用Python方法
        const isRecurrence = configsComp.getValue("mission.recurrence")
        const res = qmlapp.utilsConnector.findImages(paths, isRecurrence)
        if(res.length <= 0){
            return
        }
        // 加入表格
        for(let i in res) {
            filesTableView.add({ path: res[i], time: "", state: "" })
        }
    }

    // 运行OCR
    function ocrStart() {
        let msnLength = filesTableView.rowCount
        if(msnLength <= 0) {
            ctrlPanel.stopFinished()
            return
        }
        // 刷新表格
        for(let i = 0; i < msnLength; i++) {
            filesTableView.set(i, { time: "", state: qsTr("排队") })
        }
        // 刷新计数
        errorNum = 0 // 异常任务个数
        // 开始运行
        const paths = filesTableView.getColumnsValue("path")
        const argd = configsComp.getValueDict()
        msnID = tabPage.callPy("msnPaths", paths, argd)
        // 若tabPanel面板的下标没有变化过，则切换到记录页
        if(tabPanel.indexChangeNum < 2)
            tabPanel.currentIndex = 1
        ctrlPanel.runFinished(msnLength)
    }

    // 停止OCR
    function ocrStop() {
        _ocrStop()
        tabPage.callPy("msnStop")
        ctrlPanel.stopFinished()
    }

    function _ocrStop() {
        msnID = "" // 清除任务ID
        // 刷新表格，清空未执行的任务的状态
        let msnLength = filesTableView.rowCount
        for(let i = 0; i < msnLength; i++) {
            const row = filesTableView.get(i)
            if(row.time === "") {
                filesTableView.setProperty(i, "state", "")
            }
        }
    }

    // 关闭页面
    function closePage() {
        if(ctrlPanel.state_ !== "stop") {
            const argd = { yesText: qsTr("依然关闭") }
            const callback = (flag)=>{
                if(flag) {
                    ocrStop()
                    delPage()
                }
            }
            qmlapp.popup.dialog("", qsTr("任务正在进行中。\n要结束任务并关闭页面吗？"), callback, "warning", argd)
        }
        else {
            delPage()
        }
    }

    // 预览
    function msnPreview(path) {
        const argd = configsComp.getValueDict()
        tabPage.callPy("msnPreview", path, argd)
    }

    // ========================= 【python调用qml】 =========================

    // 准备开始一个任务
    function onOcrReady(path) {
        // 刷新表格显示
        filesTableView.setProperty(path, "state", qsTr("处理"))
    }

    // 获取一个OCR的返回值
    function onOcrGet(path, res) {
        const time = res.time.toFixed(2)
        let state = ""
        switch(res.code){
            case 100:
                state = "√ "+res.score.toFixed(2);break
            case 101:
                state = "√ ---- ";break
            default:
                state = "× "+res.code
                errorNum++ // 异常任务数量+1
                break
        }
        // 刷新表格显示
        filesTableView.set(path, { "time": time, "state": state })
        // 提取文字，添加到结果表格
        res.title = res.fileName
        resultsTableView.addOcrResult(res)
        ctrlPanel.msnStep(1) // 任务计数器步进
    }

    // 任务队列完毕
    function onOcrEnd(msg, thisMsnID) {
        // msg: [Success] [Warning] [Error]
        if(msnID !== thisMsnID) { // 返回的任务ID不等于前端展示的任务ID，则不处理
            return
        }
        _ocrStop()
        // 任务成功
        if(msg.startsWith("[Success]")) {
            let errMsg = ""
            if(errorNum > 0) { // 有异常任务
                errMsg = qsTr("%1 张图片识别失败！").arg(errorNum)
            }
            const simpleType = configsComp.getValue("other.simpleNotificationType")
            qmlapp.popup.simple(qsTr("批量识别完成"), errMsg, simpleType)
            // 任务完成后续操作
            qmlapp.globalConfigs.utilsDicts.postTaskHardwareCtrl(
                configsComp.getValue("postTaskActions.system")
            )
        }
        // 任务失败
        else if(msg.startsWith("[Error]")) {
            qmlapp.popup.message(qsTr("批量识别任务异常"), msg, "error")
        }
        ctrlPanel.stopFinished()
    }

    // 预览
    function onPreview(path, res) {
        ignoreArea.getPreview(res, path, "")
    }
    // 路径转文件名
    function path2name(path) {
        const parts = path.split("/")
        return parts[parts.length - 1]
    }
    // 文件表格中单击路径
    function onClickPath(index) {
        let info = filesTableView.get(index)
        let fileName = path2name(info.path)
        let res = resultsTableView.getResult(fileName)
        let data = undefined, text = undefined
        if(res) {
            if(res.source)
                data = JSON.parse(res.source)
            if(res.resText)
                text = res.resText
        }
        previewImage.show(info.path, data, text)
    }

    // ========================= 【布局】 =========================

    // 配置
    configsComp: BatchOCRConfigs {
        // 点按钮打开忽略区域
        onClickIgnoreArea: {
            if(filesTableView.rowCount > 0) {
                const path = filesTableView.get(0).path
                console.log("打开路径", path)
                ignoreArea.showPath(path)
            }
            else {
                ignoreArea.show()
            }
        }
    }
    // 主区域：左右双栏面板。
    DoubleRowLayout {
        saveKey: "BatchOCR_1"
        anchors.fill: parent
        initSplitterX: 0.5

        // 左面板：控制板+文件表格
        leftItem: Panel {
            anchors.fill: parent

            // 上方控制板
            MissionCtrlPanel {
                id: ctrlPanel
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: size_.spacing
                height: size_.line * 2

                onRunClicked: tabPage.ocrStart()
                onPauseClicked: {
                    tabPage.callPy("msnPause")
                    pauseFinished()
                }
                onResumeClicked: {
                    tabPage.callPy("msnResume")
                    resumeFinished()
                }
                onStopClicked: tabPage.ocrStop()
            }

            // 下方文件表格
            FilesTableView {
                id: filesTableView
                anchors.top: ctrlPanel.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.margins: size_.spacing
                anchors.topMargin: size_.smallSpacing
                headers: [
                    {key: "path", title: qsTr("图片"), left: true, display:path2name,
                        btn: true, onClicked:onClickPath},
                    {key: "time", title: qsTr("耗时"), },
                    {key: "state", title: qsTr("状态"), },
                ]
                openBtnText: qsTr("打开图片")
                clearBtnText: qsTr("清空")
                defaultTips: qsTr("拖入图片或文件夹")
                fileDialogTitle: qsTr("请选择图片")
                fileDialogNameFilters: [qsTr("图片")+" (*.jpg *.jpe *.jpeg *.jfif *.png *.webp *.bmp *.tif *.tiff)"]
                isLock: ctrlPanel.state_ !== "stop"
                onAddPaths: {
                    tabPage.addImages(paths)
                }
            }
        }
        // 右面板：文字输出 & 设置
        rightItem: Panel {
            id: rightPanel
            anchors.fill: parent

            // 结果面板
            ResultsTableView {
                id: resultsTableView
                anchors.fill: parent
                visible: false
            }

            // 配置项控制板
            TabPanel {
                id: tabPanel
                anchors.fill: parent
                anchors.margins: size_.spacing

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
                ]
            }
        }
    }

    // 鼠标拖入图片
    DropArea_ {
        anchors.fill: parent
        callback: tabPage.addImages
    }

    // 预览面板
    PreviewImage {
        id: previewImage
        anchors.fill: parent
    }

    // 忽略区域编辑器
    IgnoreArea {
        id: ignoreArea
        anchors.fill: parent
        pathPreview: msnPreview
        configsComp: tabPage.configsComp
        configKey: "tbpu.ignoreArea"
    }
}