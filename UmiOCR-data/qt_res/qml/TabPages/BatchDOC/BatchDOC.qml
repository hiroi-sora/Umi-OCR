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

    property string msnID: "" // 当前任务ID

    // TODO: 测试用
    // Timer {
    //     interval: 200
    //     running: true
    //     onTriggered: {
    //         addDocs(
    //             [
    //                 // "D:/Pictures/Screenshots/test",
    //                 // "../../PDF测试",
    //                 "D:/MyCode/PythonCode/Umi-OCR 计划/PDF测试/多样本",
    //             ]
    //         )
    //         console.log("自动添加！！！！！！！！！！！！！")
    //         // docStart()
    //     }
    // }

    // 添加一批文档。传入值是没有 file:/// 开头的纯字符串的列表。
    function addDocs(paths) {
        addDocsDropArea.enable = false // 禁用继续拖入
        qmlapp.popup.showMask(qsTr("文件读取中…"), "addDocs")
        const isRecurrence = configsComp.getValue("mission.recurrence")
        // 等待python调用 onAddDocs 回调
        tabPage.callPy("addDocs", paths, isRecurrence)
    }

    // 运行文档任务
    function docStart() {
        const fileCount = filesTableView.rowCount
        if(fileCount <= 0) {
            ctrlPanel.stopFinished()
            return
        }
        // 获取信息
        const docs = filesTableView.getColumnsValues([
            "path","range_start", "range_end", "page_count", "is_encrypted", "is_authenticate", "password"])
        // 第1次遍历：检查密码填写
        for(let i = 0; i < fileCount; i++) {
            const d = docs[i]
            if(d.is_encrypted && !d.is_authenticate) {
                qmlapp.popup.message(qsTr("文档已加密"), qsTr("【%1】\n请点击文档名，设置密码").arg(d.path), "warning")
                ctrlPanel.stopFinished()
                return
            }
        }
        // 第2次遍历：刷新信息
        let allPages = 0 // 页总数
        for(let i = 0; i < fileCount; i++) {
            const d = docs[i]
            allPages += d.range_end - d.range_start + 1
            filesTableView.setProperty(d.path, "state", qsTr("排队"))
        }
        // 若tabPanel面板的下标没有变化过，则切换到记录页
        if(tabPanel.indexChangeNum < 2)
            tabPanel.currentIndex = 1
        // 任务进度 开始计时
        ctrlPanel.runFinished(allPages)
        // 提交任务
        const argd = configsComp.getValueDict()
        tabPage.callPy("msnDocs", docs, argd)
    }

    // 停止文档任务
    function docStop() {
        tabPage.callPy("msnStop")
        // 刷新表格，清空未执行的任务的状态
        let msnLength = filesTableView.rowCount
        for(let i = 0; i < msnLength; i++) {
            const row = filesTableView.get(i)
            const s = row.state
            if(s.length > 0 && s[0] !== "√" && s[0] !== "×") {
                filesTableView.setProperty(i, "state", "")
            }
        }
        ctrlPanel.stopFinished()
    }

    // 文件表格中单击文档
    function onClickDoc(index) {
        if(ctrlPanel.state_ !== "stop") return
        const info = filesTableView.get(index)
        if(Object.keys(info).length > 0)
            previewDoc.show(info)
    }

    // 关闭页面
    function closePage() {
        if(ctrlPanel.state_ !== "stop") {
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

    // 添加一批文档
    function onAddDocs(docs) {
        qmlapp.popup.hideMask("addDocs")
        addDocsDropArea.enable = true
        if(docs.length <= 0){
            return
        }
        // 加入表格
        let encryptedCount = 0
        for(let i in docs) {
            const info = docs[i]
            filesTableView.add({
                // 显示：路径，状态，页范围
                path: info.path,
                pages: `${info.page_count}`, // 如果范围为整本，只显示总页数。否则显示 起始-结束
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

    // 准备开始处理一个文档
    function onDocStart(path) {
        // 刷新表格显示
        const d = filesTableView.get(path)
        let state = `0/${d.range_end - d.range_start + 1}`
        filesTableView.setProperty(path, "state", state)
    }

    // 获取一个文档的一页的结果
    function onDocGet(path, page, res) {
        // 刷新单个文档的信息
        const d = filesTableView.get(path)
        const state = `${page - d.range_start + 1}/${d.range_end - d.range_start + 1}`
        filesTableView.setProperty(path, "state", state)
        // 提取文字，添加到结果表格
        const title = path2name(path)
        res.title = `${title} - ${page}`
        resultsTableView.addOcrResult(res)
        ctrlPanel.msnStep(1)
    }

    // 一个文档处理完毕。 isAll==true 时所有文档处理完毕。
    function onDocEnd(path, msg, isAll) {
        const errTitle = qsTr("文档识别异常")
        // 成功结束
        if(msg.startsWith("[Success]")) {
            filesTableView.setProperty(path, "state", "√")
            msg = ""
        }
        // 单个文档任务失败，总体未结束
        else if(!isAll) {
            filesTableView.setProperty(path, "state", "× "+ qsTr("失败"))
            qmlapp.popup.simple(errTitle, msg)
        }
        // 所有文档处理完毕
        if(isAll) {
            const simpleType = configsComp.getValue("other.simpleNotificationType")
            qmlapp.popup.simple(qsTr("批量识别完成"), "", simpleType)
            if(msg) // 如果有异常，则弹窗
                qmlapp.popup.message(errTitle, msg, "error")
            ctrlPanel.stopFinished()
            // 任务完成后续操作
            qmlapp.globalConfigs.utilsDicts.postTaskHardwareCtrl(
                configsComp.getValue("postTaskActions.system")
            )
        }
    }

    // 路径转文件名
    function path2name(path) {
        const parts = path.split("/")
        return parts[parts.length - 1]
    }

    // ========================= 【布局】 =========================

    // 配置
    configsComp: BatchDOCConfigs {}

    // 主区域：左右双栏面板。
    DoubleRowLayout {
        saveKey: "BatchDOC_1"
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

                onRunClicked: tabPage.docStart()
                onPauseClicked: {
                    tabPage.callPy("msnPause")
                    pauseFinished()
                }
                onResumeClicked: {
                    tabPage.callPy("msnResume")
                    resumeFinished()
                }
                onStopClicked: tabPage.docStop()
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
                    {key: "pages", title: qsTr("页数"), btn: true, onClicked:onClickDoc},
                ]
                openBtnText: qsTr("打开文档")
                clearBtnText: qsTr("清空")
                defaultTips: qsTr("拖入文档或文件夹")
                fileDialogTitle: qsTr("请选择文档")
                fileDialogNameFilters: [qsTr("文档")+" (*.pdf *.xps *.epub *.mobi *.fb2 *.cbz)"]
                isLock: ctrlPanel.state_ !== "stop"
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
        id: "addDocsDropArea"
        anchors.fill: parent
        callback: tabPage.addDocs
    }

    // 预览面板
    PreviewDoc {
        id: previewDoc
        anchors.fill: parent
        configsComp: tabPage.configsComp
        updateInfo: (path, info) => {
            let infoA = filesTableView.get(path)
            Object.assign(infoA, info)
            filesTableView.set(path, infoA)
        }
    }
}