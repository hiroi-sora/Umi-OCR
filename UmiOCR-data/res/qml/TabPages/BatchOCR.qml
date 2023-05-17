// ==============================================
// =============== 功能页：批量OCR ===============
// ==============================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import Qt.labs.qmlmodels 1.0 // 表格

import "../Widgets"

Item {
    anchors.fill: parent

    DoubleColumnLayout {
        anchors.fill: parent
        initSplitterX: 0.5
        hideWidth: 50

        // 左面板：控制板+文件表格
        leftItem: Item{
            anchors.fill: parent

            // 上方控制板
            Panel{
                id: ctrlPanel
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: theme.textSize * 4
                clip: true

                // 右边按钮
                Button_ {
                    id: runBtn
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.right: parent.right
                    anchors.margins: theme.spacing * 0.5
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
                    height: ctrlPanel.height * 0.5
                    clip: true

                    Text_ {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.rightMargin: theme.spacing * 0.5
                        
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

                    HProgressBar {
                        anchors.fill: parent
                        anchors.margins: theme.spacing * 0.5
                        percent: 0.3
                    }
                }
            }

            // 下方文件表格
            Panel{
                anchors.top: ctrlPanel.bottom
                anchors.topMargin: theme.spacing
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom

                // 表格区域
                Rectangle {
                    anchors.fill: parent
                    anchors.margins: theme.spacing
                    color: theme.bgColor
                    clip: true

                    // 表头
                    HorizontalHeaderView {
                        id: tableViewHeader
                        syncView: tableView
                        anchors.top: parent.top
                        anchors.left: parent.left
                        anchors.right: parent.right
                        height: theme.textSize*2
                        model: ListModel {
                            ListElement { display: qsTr("文件名称") }
                            ListElement { display: qsTr("状态") }
                            ListElement { display: qsTr("耗时") }
                            ListElement { display: qsTr("置信") }
                        }
                    }

                    // 表格本体
                    Item {
                        anchors.top: tableViewHeader.bottom
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        clip: true

                        TableView {
                            id: tableView
                            anchors.fill: parent
                            // 列宽，-1表示填充
                            property var columnsWidth: [-1, theme.textSize*4,theme.textSize*3,theme.textSize*3]
                            
                            // 表格模型
                            model: TableModel {
                                TableModelColumn { display: "fileName" }
                                TableModelColumn { display: "status" }
                                TableModelColumn { display: "timeCost" }
                                TableModelColumn { display: "score" }
                                rows: [] // 初始为空行
                            }

                            // 宽度设定
                            columnWidthProvider: function (column) {
                                if(columnsWidth[column] < 0){ // 填充宽度
                                    let w = parent.width
                                    for(let i in columnsWidth){
                                        if(i != column)
                                            w -= columnsWidth[i]
                                    }
                                    return w
                                }
                                else{
                                    return columnsWidth[column]
                                }
                            }

                            onWidthChanged: {
                                forceLayout()
                            }
                            
                            // 元素
                            delegate: Rectangle {
                                implicitWidth: 140
                                implicitHeight: 30
                                border.width: 1
                                color: "#00000000"
                                border.color: theme.coverColor1

                                Text {
                                    text: display
                                    anchors.centerIn: parent
                                }
                            }
                            contentWidth: parent.width 
                            
                            Component.onCompleted: {
                                let index = 1
                                for(let i=0; i<33; i++){
                                    model.appendRow({
                                        "fileName": `测试文件${index++}.png`,
                                        "status": "已完成",
                                        "timeCost": (Math.random()* 1.4 + 0.6).toFixed(2),
                                        "score": (Math.random()* 0.5 + 0.5).toFixed(2),
                                    })
                                }
                                model.appendRow({
                                    "fileName": `测试文件${index++}.png`,
                                    "status": "进行中",
                                    "timeCost": "",
                                    "score": "",
                                })
                                for(let i=0; i<27; i++){
                                    model.appendRow({
                                        "fileName": `测试文件${index++}.png`,
                                        "status": "排队中",
                                        "timeCost": "",
                                        "score": "",
                                    })
                                }
                            }
                            
                            
                        }
                    }
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

                property string testStr: `
 
测试文本测试文本测试文本  
-  
reuseltems : bool  
This property holds whether or not items instantiated from the delegate should be reused. If set to  
false, any currently pooled items are destroyed.  
此属性保存是否应重用从delegate实例化的项。如果设置为false，则会销毁任何当前合并的项  
目。  
See also Reusing items, TableView:pooled, and TableView:reused.  
另请参阅 Reusing items、TableView:pooled 和 TableView:reused 。 
rowHeightProvider : var  
This property can hold a function that returns the row height for each row in the model. It is called  
whenever TableView needs to know the height of a specific row. The function takes one argument, row,  
for which the TableView needs to know the height.  
此属性可以保存一个函数，该函数返回模型中每一行的行高。每当TableView需要知道特定行的高度  
时，就会调用它。该函数接受一个参数row，TableView需要知道该参数的高度。  
Since Qt 5.13, if you want to hide a specific row, you can return O height for that row. If you return a  
negative number, TableView calculates the height based on the delegate items.  
从Qt5.13开始，如果要隐藏特定行，可以返回该行的0高度。如果返回负数，TableView将根据委托  
项计算高度。  
See also columnWidthProvider and Row heights and column widths  
                `
                    
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
}