// =============== 批量OCR页面的文件表格面板 ===============

import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt.labs.qmlmodels 1.0 // 表格
import QtGraphicalEffects 1.15 // 子元素圆角
import QtQuick.Dialogs 1.3 // 文件对话框

import "../../Widgets"

Item{
    id: filesTablePanel

    // ========================= 【逻辑】 =========================

    // 表头模型
    ListModel {
        id: headerModel
        ListElement { display: qsTr("文件名称") }
        ListElement { display: qsTr("耗时") }
        ListElement { display: qsTr("置信度") }
    }
    // 表格模型
    TableModel {
        id: tableModel
        TableModelColumn { display: "fileName" }
        TableModelColumn { display: "timeCost" }
        TableModelColumn { display: "score" }
        rows: [] // 初始为空行
    }
    // 列宽。第一列随总体宽度自动变化（[0]表示最小值），剩余列为固定值。
    property var columnsWidth: [theme.textSize*6, theme.textSize*4,theme.textSize*4]

    property int othersWidth: 0 // 除第一列以外的列宽，初始时固定下来。
    Component.onCompleted: { // 计算剩余列的固定值。
        for(let i = 1;i < columnsWidth.length; i++)
            othersWidth += columnsWidth[i]

        let index = 1
        for(let i=0; i<33; i++){
            tableModel.appendRow({
                "fileName": `测试文件${index++}.png`,
                "timeCost": (Math.random()* 1.4 + 0.6).toFixed(2),
                "score": (Math.random()* 0.5 + 0.5).toFixed(2),
            })
        }
        tableModel.appendRow({
            "fileName": `测试文件${index++}.png`,
            "timeCost": "进行中",
            "score": "",
        })
        for(let i=0; i<27; i++){
            tableModel.appendRow({
                "fileName": `测试文件${index++}.png`,
                "timeCost": "排队中",
                "score": "",
            })
        }
        tableView.forceLayout()
    }

    // 文件选择对话框
    // QT-5.15.2 会报错：“Model size of -225 is less than 0”，不影响使用。
    // QT-5.15.5 修复了这个Bug，但是PySide2尚未更新到这个版本号。只能先忍忍了
    // https://bugreports.qt.io/browse/QTBUG-92444
    FileDialog {
        id: fileDialog
        title: qsTr("请选择图片")
        nameFilters: [qsTr("图片")+" (*.jpg *.jpe *.jpeg *.jfif *.png *.webp *.bmp *.tif *.tiff)"]
        folder: shortcuts.pictures
        selectMultiple: true // 多选
        onAccepted: { // TODO
            console.log("选择图片: " + fileDialog.fileUrls)
        }
    }

    // ========================= 【布局】 =========================

    // 表格区域
    Rectangle {
        anchors.fill: parent
        color: theme.bgColor

        Item {
            id: tableContainer
            anchors.fill: parent

            // 上方操控版
            Item {
                id: tableTopPanel
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: theme.textSize * 2

                // 左打开图片按钮
                IconTextButton {
                    visible: parent.width > width*1.6 // 容器宽度过小时隐藏
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.margins: theme.smallSpacing * 0.5
                    icon_: "folder"
                    text_: qsTr("选择图片")

                    onClicked: {
                        fileDialog.open()
                    }
                    
                }

                // 右清空按钮
                IconTextButton {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.margins: theme.smallSpacing * 0.5
                    icon_: "clear"
                    text_: qsTr("清空")

                    onClicked: {
                        console.log("清空！")
                    }
                }
            }

            // 表头
            HorizontalHeaderView {
                id: tableViewHeader
                syncView: tableView
                anchors.top: tableTopPanel.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: theme.textSize * 2
                model: headerModel // 模型

                // 元素
                delegate: Rectangle {
                    implicitWidth: 0
                    implicitHeight: tableViewHeader.height
                    border.width: 1
                    color: "#00000000"
                    border.color: theme.coverColor1
                    clip: true
                    Text_ {
                        text: display
                        anchors.centerIn: parent
                    }
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
                    contentWidth: parent.width // 内容宽度
                    model: tableModel // 模型

                    // 宽度设定函数
                    columnWidthProvider: (column)=>{
                        if(column == 0){ // 第一列宽度，变化值
                            let w = parent.width - filesTablePanel.othersWidth // 计算宽度
                            return Math.max(w, columnsWidth[0]) // 宽度不得小于最小值
                        }
                        else{ return columnsWidth[column] }
                    }
                    onWidthChanged: forceLayout()  // 组件宽度变化时重设列宽
                    
                    // 元素
                    delegate: Rectangle {
                        implicitWidth: 0
                        implicitHeight: theme.textSize * 1.5
                        border.width: 1
                        color: "#00000000"
                        border.color: theme.coverColor1
                        clip: true

                        Text_ {
                            text: display
                            color: theme.subTextColor
                            anchors.left: parent.left
                            anchors.leftMargin: theme.textSize * 0.5
                        }
                    }
                }
            }
        }

        // 内圆角裁切
        layer.enabled: true
        layer.effect: OpacityMask {
            maskSource: Rectangle {
                width: tableContainer.width
                height: tableContainer.height
                radius: theme.btnRadius
            }
        }
    }
}