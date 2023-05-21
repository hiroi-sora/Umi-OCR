// ==============================================
// =============== 功能页：批量OCR ===============
// ==============================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import ".."
import "../../Widgets"

TabPage {
    id: tabPage

    // ========================= 【逻辑】 =========================

    // 文件表格模型
    property alias tableModel: filesTableView.tableModel_
    property alias tableDict: filesTableView.tableDict

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
        // 初始化
        if(tableDict == undefined)
            tableDict = {}
        // 结果写入数据
        for(let i in res){
            // 检查重复
            if(tableDict.hasOwnProperty(res[i])){
                continue
            }
            // 添加到字典中
            tableDict[res[i]] = {
                index: tableModel.rowCount
            }
            // 添加到表格中
            tableModel.appendRow({
                "filePath": res[i],
                "timeCost": "",
                "score": "",
            })
        }
    }

    // ========================= 【布局】 =========================

    // 主区域：左右双栏面板。
    DoubleColumnLayout {
        anchors.fill: parent
        initSplitterX: 500
        hideWidth: 50

        // 左面板：控制板+文件表格
        leftItem: Panel{
            anchors.fill: parent

            // 上方控制板
            Item{
                id: ctrlPanel
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: theme.spacing
                height: theme.textSize * 3
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
                    text_: "开始任务" // TODO
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
                        
                        text: "25s  33/100  33%"
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
                    anchors.topMargin: theme.smallSpacing

                    HProgressBar {
                        anchors.fill: parent
                        color: theme.bgColor
                        percent: 0.3
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
        rightItem: Panel{
            anchors.fill: parent

            Rectangle {
                id: testContainer
                anchors.fill: parent
                anchors.margins: theme.spacing
                color: theme.bgColor

                property string testStr: ""
                
                Component.onCompleted: {
                    for(let i =0;i<100;i++) testStr += "测试文本"
                }
                
                    
                ScrollView {
                    id: textScroll
                    anchors.fill: parent
                    anchors.margins: theme.spacing
                    contentWidth: width // 内容宽度
                    clip: true // 溢出隐藏

                        TextEdit {
                        text: testContainer.testStr
                        width: textScroll.width // 与内容宽度相同
                        textFormat: TextEdit.MarkdownText // md格式
                        wrapMode: TextEdit.Wrap // 尽量在单词边界处换行
                        readOnly: true // 只读
                        selectByMouse: true // 允许鼠标选择文本
                        selectByKeyboard: true // 允许键盘选择文本
                        color: theme.textColor
                        font.pixelSize: theme.textSize
                        font.family: theme.fontFamily
                    }
                }
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