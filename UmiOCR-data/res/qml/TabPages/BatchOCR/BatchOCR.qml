// ==============================================
// =============== 功能页：批量OCR ===============
// ==============================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import ".."
import "../../Widgets"
import "../../Widgets/ResultLayout"

TabPage {
    id: tabPage

    // ========================= 【逻辑】 =========================

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
                    "file:///D:/Pictures/Screenshots/屏幕截图 2023-06-03 120958.png",
                    "file:///D:/Pictures/Screenshots/屏幕截图 2021-04-27 171637.png",
                    "file:///D:/Pictures/Screenshots/屏幕截图 2021-04-27 171639.png",
                    "file:///D:/Pictures/Screenshots/屏幕截图 2023-04-24 235542.png",
                    "file:///D:/Pictures/Screenshots/屏幕截图 2023-04-22 212147.png",
                    "file:///D:/Pictures/Screenshots/屏幕截图 2023-04-22 212204.png",
                    "file:///D:/Pictures/Screenshots/屏幕截图 2023-04-22 212207.png",
                    "file:///D:/Pictures/Screenshots/屏幕截图 2023-04-22 212310.png",
                    "file:///D:/Pictures/Screenshots/屏幕截图 2023-04-22 212813.png",
                    "file:///D:/Pictures/Screenshots/屏幕截图 2023-04-22 212854.png",
                    "file:///D:/Pictures/Screenshots/屏幕截图 2023-04-23 140303.png",
                    "file:///D:/Pictures/Screenshots/屏幕截图 2023-04-23 140829.png",
                    "file:///D:/Pictures/Screenshots/屏幕截图 2023-04-23 191053.png",
                ]
            )
            ocrImages()
        }
    }

    // 将需要查询的图片路径列表paths发送给python。传入值是qt url，file:/// 开头。
    function addImages(paths) {
        // qt url 转为字符串
        let fileList = []
        for(let i in paths){
            let s = paths[i]
            if(s.startsWith("file:///"))
                fileList.push(s.substring(8))
        }
        if(fileList.length == 0){
            return
        }
        // 调用Python方法
        const res = tabPage.callPy("findImages", fileList)
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
                ocrImages()
                break
            case "run":  // 工作中
                tabPage.callPy("msnStop")
                break
        }
    }

    // 运行OCR
    function ocrImages() {
        let msnLength = Object.keys(filesDict).length
        if(msnLength <= 0)
            return
        // 刷新表格
        for(let path in filesDict){
            filesModel.setRow(filesDict[path].index, {
                    "filePath": path,
                    "time": "",
                    "state": "",
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
                runBtn.text_ = qsTr("暂停任务")
                runBtn.enabled = true
                break;
            case "stop": // 停止中
                runBtn.text_ = qsTr("停止中…")
                runBtn.enabled = false
                break;
        }
        console.log("set mission state:  ", flag)
    }

    // 设置一个OCR的返回值
    function setOcrRes(path, res) {
        if(!filesDict.hasOwnProperty(path)){
            console.error("【Error】OCR结果不存在qml队列！", path)
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
                height: theme.textSize * 2.6
                clip: true

                // 右边按钮
                Button_ {
                    id: runBtn
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.right: parent.right
                    width: theme.textSize * 6

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

                onAddImages: {
                    tabPage.addImages(paths)
                }
            }
        }
        // 右面板：文字输出 & 设置
        rightItem: Panel {
            anchors.fill: parent

            ResultsTableView {
                id: resultsTableView
                anchors.fill: parent
                anchors.margins: theme.spacing
            }
        }
    }

    // 鼠标拖入图片
    DropArea {
        id: imgDropArea
        anchors.fill: parent;
        onDropped: {
            if(drop.hasUrls){
                addImages(drop.urls)
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