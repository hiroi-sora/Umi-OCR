// ==================================================
// =============== 功能页：批量文档处理 ===============
// ==================================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import ".."
import "../../Widgets"
import "../../Widgets/ResultLayout"
import "../../Widgets/IgnoreArea"

TabPage {
    id: tabPage

    // ========================= 【逻辑】 =========================

    property string msnState: "" // 任务状态， none init run stop
    property var missionInfo: {} // 当前任务信息，耗时等
    property string missionShow: "" // 当前任务信息展示字符串

    property string msnID: "" // 当前任务ID

    Component.onCompleted: {
        missionInfo = {}
        setMsnState("none")
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
        for(let i in res) {
            const info = res[i]
            filesTableView.add({
                // 显示：路径，状态，页范围
                path: info.path, state: "", pages: `1-${info.page_count}`,
                // 数据
                page_count: info.page_count,
                page_range:[1, info.page_count],
            })
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
        console.log("docStart")
    }

    // 停止文档任务
    function docStop() {
        _docStop()
        // tabPage.callPy("msnStop")
    }
    function _docStop() {
        console.log("_docStop")
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
                    {key: "path", title: qsTr("文档"), left: true, display: path2name },
                    {key: "state", title: qsTr("状态"), },
                    {key: "pages", title: qsTr("页数"), },
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
}