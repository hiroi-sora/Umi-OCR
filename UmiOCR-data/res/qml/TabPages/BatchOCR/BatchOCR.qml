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

    // ========================= 【逻辑】 =========================

    // 配置
    BatchOCRConfigs { id: batchOCRConfigs } 
    configsComp: batchOCRConfigs

    // 文件表格模型
    property alias filesModel: filesTableView.filesModel
    property alias filesDict: filesTableView.filesDict
    property string msnState: "" // OCR任务状态
    property var missionInfo: {} // 当前任务信息，耗时等
    property string missionShow: "" // 当前任务信息展示字符串

    // 输出表格模型
    property alias resultsModel: resultsTableView.resultsModel

    Component.onCompleted: {
        setMsnState("none")
    }
    // TODO: 测试用
    Timer {
        interval: 200
        running: true
        onTriggered: {
            addImages(
                [
                    "D:/Pictures/Screenshots/屏幕截图 2023-06-03 120958.png",
                    "D:/Pictures/Screenshots/屏幕截图 2021-04-27 171637.png",
                    "D:/Pictures/Screenshots/屏幕截图 2021-04-27 171639.png",
                    "D:/Pictures/Screenshots/屏幕截图 2023-04-24 235542.png",
                    "D:/Pictures/Screenshots/屏幕截图 2023-04-22 212147.png",
                    "D:/Pictures/Screenshots/屏幕截图 2023-04-22 212204.png",
                    "D:/Pictures/Screenshots/屏幕截图 2023-04-22 212207.png",
                    "D:/Pictures/Screenshots/屏幕截图 2023-04-22 212310.png",
                    "D:/Pictures/Screenshots/屏幕截图 2023-04-22 212813.png",
                    "D:/Pictures/Screenshots/屏幕截图 2023-04-22 212854.png",
                    "D:/Pictures/Screenshots/屏幕截图 2023-04-23 140303.png",
                    "D:/Pictures/Screenshots/屏幕截图 2023-04-23 140829.png",
                    "D:/Pictures/Screenshots/屏幕截图 2023-04-23 191053.png",
                ]
            )
            console.log("自动添加！！！！！！！！！！！！！")
            ocrStart()
        }
    }

    // 将需要查询的图片路径列表paths发送给python。传入值是没有 file:/// 开头的纯字符串的列表。
    function addImages(paths) {
        if(paths.length == 0){
            return
        }
        // 调用Python方法
        const res = tabPage.callPy("findImages", paths)
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
        for(let path in filesDict){
            filesModel.setRow(filesDict[path].index, {
                    "filePath": path,
                    "time": "",
                    "state": qsTr("排队"),
                })
        }
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
        tabPage.callPy("msnPaths", Object.keys(filesDict))
    }

    // 停止OCR（同步）
    function ocrStop() {
        setMsnState("stop")
        const leftover = tabPage.callPy("msnStop")
        // console.log("剩余：", leftover)
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
        setMsnState("none")
    }

    // 添加一个结果
    function addResult(path, date, text) {
        resultsModel.append({
            "textLeft_": path,
            "textRight_": date,
            "textMain_": text
        })
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
            console.error("【Error】qml队列不存在路径！", path)
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
        const filename = path.split('/').pop()
        const formattedDate = `${date.getMonth()+1}/${date.getDate()} ${date.getHours()}:${date.getMinutes()}`
        let state = ""
        let ocrText = ""
        switch(res.code){
            case 100:
                state = "√ "+res.score.toFixed(2)
                // 合并文字
                const textArray = res.data.map(item => item.text);
                ocrText = textArray.join('\n');
                break
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
        addResult(filename, formattedDate, ocrText)
    }

    // 任务队列完毕
    function onOcrFinish() {
        setMsnState("none")
    }

    // ========================= 【布局】 =========================

    // 主区域：左右双栏面板。
    DoubleColumnLayout {
        anchors.fill: parent
        initSplitterX: 0.5
        hideWidth: 50

        // 左面板：控制板+文件表格
        leftItem: Panel {
            anchors.fill: parent

            // 上方控制板
            Item {
                id: ctrlPanel
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: theme.spacing
                height: theme.textSize * 2
                clip: true

                // 右边按钮
                Button_ {
                    id: runBtn
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.right: parent.right
                    width: theme.textSize * 6
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
                    anchors.rightMargin: theme.smallSpacing
                    height: theme.textSize * 1.3
                    clip: true

                    Text_ {
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        // anchors.rightMargin: theme.smallSpacing
                        
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
                    anchors.rightMargin: theme.smallSpacing
                    anchors.topMargin: theme.smallSpacing * 0.5

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
                anchors.margins: theme.spacing
                anchors.topMargin: theme.smallSpacing
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
                anchors.fill: parent
                anchors.margins: theme.spacing

                tabsModel: [
                    {
                        "key": "configs",
                        "title": qsTr("设置"),
                        "component": batchOCRConfigs.panelComponent,
                    },
                    {
                        "key": "ocrResult",
                        "title": qsTr("信息"),
                        "component": resultsTableView,
                    },
                ]
            }
        }
    }

    // 鼠标拖入图片
    DropArea {
        id: imgDropArea
        anchors.fill: parent;
        onDropped: {
            if(drop.hasUrls){
                var urls = Utils.QUrl2String(drop.urls)
                addImages(urls)
            }
        }

        // 背景
        Rectangle {
            id: dropAreaBg
            visible: imgDropArea.containsDrag 
            anchors.fill: parent
            color: theme.coverColor4

            Panel {
                color: theme.bgColor
                anchors.centerIn: parent
                implicitWidth: dragText.width*2
                implicitHeight: dragText.height*2
                
                Text_ {
                    id: dragText
                    anchors.centerIn: parent
                    text: qsTr("松手放入图片")
                }
            }
        }
    }
}