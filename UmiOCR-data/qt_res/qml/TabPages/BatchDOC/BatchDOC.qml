// ==================================================
// =============== 功能页：批量文档处理 ===============
// ==================================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import ".."
import "../../Widgets"
import "../../Widgets/ResultLayout"
import "../../Widgets/IgnoreArea"

/* 文档参数：
    path 路径
    pages 页数显示
    state 状态显示
    page_count 总页数
    range_start 范围开始
    range_end 范围结束
    is_encrypted 需要密码
    is_authenticate 密码正确
    password 密码
*/

TabPage {
    id: tabPage

    // ========================= 【逻辑】 =========================

    property string msnState: "" // 任务状态， none init run stop
    property string missionShow: "" // 当前任务信息展示字符串
    property var missionInfo: {} // 当前任务信息，耗时等
    /*
        startTime: new Date().getTime(), // 开始时间
        allNum: msnLength, // 总长度
        costTime: 0, // 当前耗时
        nowNum: 0, // 当前执行长度
    */

    property string msnID: "" // 当前任务ID

    Component.onCompleted: {
        missionInfo = {}
        setMsnState("none")
    }
    // TODO: 测试用
    Timer {
        interval: 200
        running: true
        onTriggered: {
            addDocs(
                [
                    // "D:/Pictures/Screenshots/test",
                    "../../PDF测试",
                ]
            )
            console.log("自动添加！！！！！！！！！！！！！")
            // ocrStart()
            // onClickDoc(0)
        }
    }

    // 添加一批文档。传入值是没有 file:/// 开头的纯字符串的列表。
    function addDocs(paths) {
        // 调用Python方法
        const isRecurrence = configsComp.getValue("mission.recurrence")
        const res = tabPage.callPy("addDocs", paths, isRecurrence)
        if(res.length <= 0){
            return
        }
        // 加入表格
        let encryptedCount = 0
        for(let i in res) {
            const info = res[i]
            filesTableView.add({
                // 显示：路径，状态，页范围
                path: info.path, pages: `1-${info.page_count}`,
                state: info.is_encrypted ? qsTr("加密") : "" ,
                // 数据
                page_count: info.page_count,
                range_start: 1,
                range_end: info.page_count,
                is_encrypted: info.is_encrypted, // 有密码
                is_authenticate: !info.is_encrypted, // 已解密（密码正确）
                password: "",
            })
            if(info.is_encrypted) encryptedCount++
        }
        if(encryptedCount > 0) {
            qmlapp.popup.simple(qsTr("%1个加密文档").arg(encryptedCount),
                qsTr("请点击文件名填写密码"))
        }
    }

    // 运行按钮按下
    function runBtnClick() {
        switch(msnState) {
            case "none": // 不在运行
                docStart()
                break
            case "run":  // 工作中
                docStop()
                break
        }
    }

    // 运行文档任务
    function docStart() {
        const fileCount = filesTableView.rowCount
        if(fileCount <= 0)
            return
        setMsnState("init") // 状态：初始化任务
        missionShow = ""
        // 获取信息
        const docs = filesTableView.getColumnsValues([
            "path","range_start", "range_end", "is_encrypted", "is_authenticate", "password"])
        let pathIndex = {} // 缓存路径到下标的映射
        for(let i = 0; i < fileCount; i++) {
            const d = docs[i]
            pathIndex[d.path] = i
            if(d.is_encrypted && !d.is_authenticate) {
                qmlapp.popup.message(qsTr("文档已加密"), qsTr("【%1】\n请点击文档名，设置密码").arg(d.path), "warning")
                setMsnState("none") // 状态：不在运行
                return
            }
        }
        const argd = configsComp.getValueDict()
        // 提交任务，获取任务信息
        const resList = tabPage.callPy("msnDocs", docs, argd)
        let errMsg = "" // 错误信息
        let allPages = 0 // 页总数
        // 判断任务添加结果，刷新表格
        for(let i in resList) {
            const res = resList[i]
            const path = res.path, msnID = res.msnID
            if(msnID.startsWith("[")) { // 添加任务失败
                filesTableView.setProperty(path, "state", qsTr("失败"))
                errMsg += `${path} - ${msnID}\n`
            }
            else { // 添加任务成果，增加计数
                filesTableView.setProperty(path, "state", qsTr("排队"))
                const d = docs[pathIndex[path]]
                allPages += d.range_end - d.range_start + 1
            }
        }
        missionProgress.percent = 0 // 进度条显示
        if(allPages > 0) { // 有成功的任务
            // 刷新计数
            missionInfo = {
                startTime: new Date().getTime(), // 开始时间
                allNum: allPages, // 总长度
                costTime: 0, // 当前耗时
                nowNum: 0, // 当前执行长度
            }
            missionShow = `0s  0/${allPages}  0%` // 信息显示
            // 若tabPanel面板的下标没有变化过，则切换到记录页
            if(tabPanel.indexChangeNum < 2)
                tabPanel.currentIndex = 1
            setMsnState("run") // 状态：运行中
        }
        else {
            missionInfo = {}
            missionShow = qsTr("任务失败")
            setMsnState("none") // 状态：不在运行
        }
        // 错误信息显示
        if(errMsg) {
            qmlapp.popup.message(qsTr("部分文档异常"), errMsg, "error")
        }
    }

    // 停止文档任务
    function docStop() {
        setMsnState("stop") // 设置结束中
        tabPage.callPy("msnStop")
        // 刷新表格，清空未执行的任务的状态
        let msnLength = filesTableView.rowCount
        for(let i = 0; i < msnLength; i++) {
            const row = filesTableView.get(i)
            if(row.state !== "√") {
                filesTableView.setProperty(i, "state", "")
            }
        }
        setMsnState("none") // 设置结束
    }

    // 文件表格中单击文档
    function onClickDoc(index) {
        if(msnState !== "none") return
        const info = filesTableView.get(index)
        previewDoc.show(info)
    }

    // 关闭页面
    function closePage() {
        if(msnState !== "none") {
            const argd = { yesText: qsTr("依然关闭") }
            const callback = (flag)=>{
                if(flag) {
                    docStop()
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

    // 准备开始处理一个文档
    function onDocStart(path) {
        // 刷新表格显示
        const d = filesTableView.get(path)
        let state = `0/${d.range_end - d.range_start + 1}`
        filesTableView.setProperty(path, "state", state)
    }

    // 获取一个文档的一页的结果
    function onDocGet(path, page, res) {
        // 刷新总体 耗时显示
        const date = new Date();
        const currentTime = date.getTime()
        missionInfo.costTime = currentTime - missionInfo.startTime
        missionInfo.nowNum = missionInfo.nowNum + 1
        const costTime = (missionInfo.costTime/1000).toFixed(1)
        const nowNum = missionInfo.nowNum
        const percent = Math.floor(((nowNum/missionInfo.allNum)*100))
        missionProgress.percent = nowNum/missionInfo.allNum // 进度条显示
        missionShow = `${costTime}s  ${nowNum}/${missionInfo.allNum}  ${percent}%` // 信息显示
        // 刷新单个文档的信息
        const d = filesTableView.get(path)
        let state = `${page - d.range_start}/${d.range_end - d.range_start + 1}`
        filesTableView.setProperty(path, "state", state)
        // 提取文字，添加到结果表格
        let title = path2name(path)
        res.title = `${title} - ${page}`
        resultsTableView.addOcrResult(res)
    }

    // 一个文档处理完毕
    function onDocEnd(path, msg) {
        filesTableView.setProperty(path, "state", "√")
        // 任务成功
        if(msg.startsWith("[Success]")) {
            // TODO
            // 所有文档处理完毕
            if(msg === "[Success] All completed.") {
                setMsnState("none") // 状态：不在运行
            }
        }
        // 任务失败
        else if(msg.startsWith("[Error]")) {
            qmlapp.popup.message(qsTr("批量识别任务异常"), msg, "error")
        }
    }

    // 路径转文件名
    function path2name(path) {
        const parts = path.split("/")
        return parts[parts.length - 1]
    }

    // ========================= 【布局】 =========================

    // 配置
    configsComp: BatchDOCConfigs {
    }
    // 主区域：左右双栏面板。
    DoubleRowLayout {
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
                height: size_.line * 2
                clip: true

                // 右边按钮
                Button_ {
                    id: runBtn
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.right: parent.right
                    width: size_.line * 6
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
                    height: size_.line * 1.3
                    clip: true

                    Text_ {
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        
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
            FilesTableView {
                id: filesTableView
                anchors.top: ctrlPanel.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.margins: size_.spacing
                anchors.topMargin: size_.smallSpacing
                headers: [
                    {key: "path", title: qsTr("文档"), left: true, display: path2name,
                        btn: true, onClicked:onClickDoc},
                    {key: "state", title: qsTr("状态"), btn: true, onClicked:onClickDoc},
                    {key: "pages", title: qsTr("范围"), btn: true, onClicked:onClickDoc},
                ]
                openBtnText: qsTr("选择文档")
                clearBtnText: qsTr("清空")
                defaultTips: qsTr("拖入或选择文档")
                fileDialogTitle: qsTr("请选择文档")
                fileDialogNameFilters: [qsTr("文档")+" (*.pdf *.xps *.epub *.mobi *.fb2 *.cbz)"]
                isLock: msnState !== "none"
                onAddPaths: {
                    tabPage.addDocs(paths)
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

    // 鼠标拖入文档
    DropArea_ {
        anchors.fill: parent
        callback: tabPage.addDocs
    }

    // 预览面板
    PreviewDoc {
        id: previewDoc
        anchors.fill: parent
        configsComp: tabPage.configsComp
        ignoreAreaKey: "tbpu.ignoreArea"
        updateInfo: (path, info) => {
            let infoA = filesTableView.get(path)
            Object.assign(infoA, info)
            filesTableView.set(path, infoA)
        }
    }
}