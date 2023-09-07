// ==============================================
// =============== 功能页：批量OCR ===============
// ==============================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import ".."
import "../../Widgets"
import "../../Widgets/ResultLayout"
import "../../js/utils.js" as Utils

TabPage {
    id: tabPage
    // 配置
    BatchOCRConfigs { id: batchOCRConfigs } 
    configsComp: batchOCRConfigs

    // ========================= 【逻辑】 =========================

    // 文件表格模型
    property alias filesModel: filesTableView.filesModel
    property alias filesDict: filesTableView.filesDict
    property string msnState: "" // OCR任务状态， none init run stop
    property var missionInfo: {} // 当前任务信息，耗时等
    property string missionShow: "" // 当前任务信息展示字符串

    property string msnID: "" // 当前任务ID

    Component.onCompleted: {
        setMsnState("none")
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
        if(paths.length == 0){
            return
        }
        // 调用Python方法
        const isRecurrence = batchOCRConfigs.getValue("mission.recurrence")
        const res = tabPage.callPy("findImages", paths, isRecurrence)
        // 结果写入数据
        if(filesDict==undefined){
            filesDict = {}
        }
        for(let i in res){
            // 检查重复
            if(filesDict.hasOwnProperty(res[i])){
                continue
            }
            // 添加到字典中
            filesDict[res[i]] = {
                index: filesModel.rowCount
            }
            // 添加到表格中
            filesModel.appendRow({
                "filePath": res[i],
                "time": "",
                "state": "",
            })
        }
    }

    // 运行按钮按下
    function runBtnClick() {
        switch(msnState) {
            case "none": // 不在运行
                ocrStart()
                break
            case "run":  // 工作中
                ocrStop()
                break
        }
    }

    // 运行OCR
    function ocrStart() {
        let msnLength = Object.keys(filesDict).length
        if(msnLength <= 0)
            return
        setMsnState("init") // 状态：初始化任务
        // 刷新表格
        // 更改完 filesModel 后重新为 tableView 绑定模型，强制刷新表格UI渲染，避免格子丢失的问题
        filesTableView.tableView.model = undefined
        for(let path in filesDict){
            filesModel.setRow(filesDict[path].index, {
                    "filePath": path,
                    "time": "",
                    "state": qsTr("排队中"),
                })
        }
        filesTableView.tableView.model = filesModel
        // 刷新计数
        missionInfo = {
            startTime: new Date().getTime(), // 开始时间
            allNum: msnLength, // 总长度
            costTime: 0, // 当前耗时
            nowNum: 0, // 当前执行长度
        }
        missionProgress.percent = 0 // 进度条显示
        missionShow = `0s  0/${msnLength}  0%` // 信息显示
        // 开始运行
        const paths = Object.keys(filesDict)
        const argd = batchOCRConfigs.getConfigValueDict()
        msnID = tabPage.callPy("msnPaths", paths, argd)
        // 若tabPanel面板的下标没有变化过，则切换到记录页
        if(tabPanel.indexChangeNum < 2)
            tabPanel.currentIndex = 1
    }

    // 停止OCR
    function ocrStop() {
        _ocrStop()
        tabPage.callPy("msnStop")
    }

    function _ocrStop() {
        msnID = "" // 清除任务ID
        setMsnState("stop") // 设置结束中
        // 刷新表格，清空未执行的任务的状态
        for(let path in filesDict){
            const r = filesDict[path].index
            const row = filesModel.getRow(r)
            if(row.time === "") {
                filesModel.setRow(filesDict[path].index, {
                        "filePath": path,
                        "time": "",
                        "state": "",
                    })
            }
        }
        setMsnState("none") // 设置结束
    }

    // 关闭页面
    function closePage() {
        if(msnState !== "none") {
            const argd = {yesText: qsTr("依然关闭")}
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

    // ========================= 【python调用qml】 =========================

    /* 
    none  不在运行
    init  正在启动
    run   工作中
    stop  停止中
    */
    // 设置任务状态
    function setMsnState(flag) {
        msnState = flag
        switch(flag) {
            case "none": // 不在运行
                runBtn.text_ = qsTr("开始任务")
                runBtn.enabled = true
                break;
            case "init": // 正在启动
                runBtn.text_ = qsTr("启动中…")
                runBtn.enabled = false
                break;
            case "run":  // 工作中
                runBtn.text_ = qsTr("停止任务")
                runBtn.enabled = true
                break;
            case "stop": // 停止中
                runBtn.text_ = qsTr("停止中…")
                runBtn.enabled = false
                break;
        }
        console.log("set mission state:  ", flag)
    }

    // 准备开始一个任务
    function onOcrReady(path) {
        if(!filesDict.hasOwnProperty(path)){
            qmlapp.popup.message(qsTr("函数 onOcrReady 异常"), qsTr("qml任务队列不存在路径")+path.toString(), "error")
            return
        }
        // 刷新文件表格显示
        const r = filesDict[path].index
        const row = filesModel.getRow(r)
        filesModel.setRow(r, {
            "filePath": row.filePath,
            "time": "",
            "state": qsTr("处理中"),
        })
    }

    // 获取一个OCR的返回值
    function onOcrGet(path, res) {
        if(!filesDict.hasOwnProperty(path)){
            console.error("【Error】qml队列不存在路径！", path)
            return
        }
        // 刷新耗时显示
        const date = new Date();
        const currentTime = date.getTime()
        missionInfo.costTime = currentTime - missionInfo.startTime
        missionInfo.nowNum = missionInfo.nowNum + 1
        const costTime = (missionInfo.costTime/1000).toFixed(1)
        const nowNum = missionInfo.nowNum
        const percent = Math.floor(((nowNum/missionInfo.allNum)*100))
        missionProgress.percent = nowNum/missionInfo.allNum // 进度条显示
        missionShow = `${costTime}s  ${nowNum}/${missionInfo.allNum}  ${percent}%` // 信息显示
        const index = filesDict[path].index
        const time = res.time.toFixed(2)
        let state = ""
        switch(res.code){
            case 100:
                state = "√ "+res.score.toFixed(2);break
            case 101:
                state = "√ ---- ";break
            default:
                state = "× "+res.code;break
        }
        // 刷新文件表格显示
        filesModel.setRow(index, {
            "filePath": path,
            "time": time,
            "state": state,
        })
        // 提取文字，添加到结果表格
        res.title = res.fileName
        resultsTableView.addOcrResult(res)
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
            const simpleType = batchOCRConfigs.getValue("other.simpleNotificationType")
            qmlapp.popup.simple(qsTr("批量识别完成"), "", simpleType)
            // 任务完成后续操作：打开文件/文件夹
            const openWhat = {
                "openFile": batchOCRConfigs.getValue("postTaskActions.openFile"),
                "openFolder": batchOCRConfigs.getValue("postTaskActions.openFolder"),
            }
            tabPage.callPy("postTaskActions", openWhat)
            // 任务完成后续操作：系统关机/待机
            const actSys = batchOCRConfigs.getValue("postTaskActions.system")
            if(actSys) {
                let actStr = ""
                // 对话框：系统即将关机  继续关机 | 取消关机
                if(actSys==="shutdown") actStr = qsTr("关机")
                else if(actSys==="hibernate") actStr = qsTr("休眠")
                const argd = {yesText: qsTr("继续%1").arg(actStr), noText: qsTr("取消%1").arg(actStr)}
                const callback = (flag)=>{
                    if(flag) {
                        const d = {}
                        d[actSys] = true
                        tabPage.callPy("postTaskActions", d)
                    }
                }
                qmlapp.popup.dialogCountdown(qsTr("系统即将%1").arg(actStr), "", callback, "", argd)
            }
        }
        // 任务失败
        else if(msg.startsWith("[Error]")) {
            qmlapp.popup.message(qsTr("批量识别任务异常"), msg, "error")
        }
    }

    // ========================= 【布局】 =========================

    // 主区域：左右双栏面板。
    DoubleColumnLayout {
        anchors.fill: parent
        initSplitterX: 0.5

        // 左面板：控制板+文件表格
        leftItem: Panel {
            anchors.fill: parent

            // 上方控制板
            Item {
                id: ctrlPanel
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: size_.spacing
                height: size_.text * 2
                clip: true

                // 右边按钮
                Button_ {
                    id: runBtn
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.right: parent.right
                    width: size_.text * 6
                    bold_: true

                    bgColor_: theme.coverColor1
                    bgHoverColor_: theme.coverColor2
                    text_: "" // 动态变化
                    onClicked: tabPage.runBtnClick()
                }

                // 左上信息
                Item {
                    id: infoContainer
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.right: runBtn.left
                    anchors.rightMargin: size_.smallSpacing
                    height: size_.text * 1.3
                    clip: true

                    Text_ {
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        // anchors.rightMargin: size_.smallSpacing
                        
                        text: missionShow
                        color: theme.subTextColor
                    }
                }

                // 左下进度条
                Item {
                    id: progressContainer
                    anchors.top: infoContainer.bottom
                    anchors.left: parent.left
                    anchors.bottom: parent.bottom
                    anchors.right: runBtn.left
                    anchors.rightMargin: size_.smallSpacing
                    anchors.topMargin: size_.smallSpacing * 0.5

                    HProgressBar {
                        id: missionProgress
                        anchors.fill: parent
                        color: theme.bgColor
                        percent: 0
                    }
                }
            }

            // 下方文件表格
            FilesTableView{
                id: filesTableView
                anchors.top: ctrlPanel.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.margins: size_.spacing
                anchors.topMargin: size_.smallSpacing
                msnState: tabPage.msnState

                onAddImages: {
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
                        "component": batchOCRConfigs.panelComponent,
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
    DropArea {
        id: imgDropArea
        anchors.fill: parent
        onEntered: {
            qmlapp.popup.showMask(qsTr("松手放入图片"), "BatchOCR-DropImage")
        }
        onExited: {
            qmlapp.popup.hideMask("BatchOCR-DropImage")
        }
        onDropped: {
            qmlapp.popup.hideMask("BatchOCR-DropImage")
            if(drop.hasUrls){
                var urls = Utils.QUrl2String(drop.urls)
                addImages(urls)
            }
        }
    }
}