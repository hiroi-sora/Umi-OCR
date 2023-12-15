// =============== 文件表格面板 ===============

import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt.labs.qmlmodels 1.0 // 表格
import QtGraphicalEffects 1.15 // 子元素圆角
import QtQuick.Dialogs 1.3 // 文件对话框

Item {
    id: fTableRoot

    // ========================= 【定义】 =========================

    // 表头。定义每一列。
    property var headers: [
        // 第一列也作为总key（tk），不允许重复。
        {"key": "path", "title": "文件", },
        {"key": "time", "title": "耗时", },
        {"key": "state", "title": "状态", },
    ]
    property string openBtnText: qsTr("选择文件")
    property string clearBtnText: qsTr("清空")
    property string defaultTips: qsTr("拖入或选择文件")
    property string fileDialogTitle: qsTr("请选择文件")
    property var fileDialogNameFilters: [qsTr("文件")+" (*.jpg *.jpe *.jpeg *.jfif *.png *.webp *.bmp *.tif *.tiff)"]
    property int spacing: size_.spacing * 2 // 表项水平间隔
    property int minWidth0: size_.smallLine * 5 // 第0列最小宽度


    // ========================= 【调用接口】 =========================

    property int columnCount: 0 // 列数量， onCompleted 中初始化
    property int rowCount: dataModel.count // 行数量

    // 增：添加一项
    // ik：可以是表格行index（int），也可以是总key（string）
    function add(row, ik=-1) {
        if(isLock) {
            console.log("[Warning] 表格已锁定， add 操作无效")
            return
        }
        // TODO
    }
    // 增：添加一个 tableKey
    function addKey(tableKey, ik=-1) {
        if(isLock) {
            console.log("[Warning] 表格已锁定， addKey 操作无效")
            return
        }
        var row = preAddKey(tableKey)
        add(row, ik)
    }
    // 增：添加多个 tableKey
    function addKeys(tableKeys, ik=-1) {
        if(isLock) {
            console.log("[Warning] 表格已锁定， addKeys 操作无效")
            return
        }
        for(let i in tableKeys)
            addKey(row, tableKeys[i])
    }
    // 添加 tableKey 之前的预处理函数
    property var preAddKey: (tableKey) => {
        var row = Array(columnCount).fill("")
        row[0] = tableKey
        return row
    }
    // 删：删除一项
    function del(ik) {
        if(isLock) {
            console.log("[Warning] 表格已锁定， del 操作无效")
            return
        }
        // TODO
    }
    // 删：清空
    function clear() {
        if(isLock) {
            console.log("[Warning] 表格已锁定， clear 操作无效")
            return
        }
        // TODO
    }
    // 改
    function set(ik, columnIK, value) {
        // TODO
    }
    // 查：ik转index
    function ik2i(ik) {
        // TODO
    }

    // 表格锁定时，禁止增、删，允许改。
    function lock() { isLock = true }  // 锁定表格，禁止操作
    function unlock() { isLock = false }  // 解锁表格
    // 定义信号
    // signal click(var info) // 点击条目的信号

    Component.onCompleted: {
        columnCount = headers.length
        for(let i=0; i<columnCount; i++){
            headerModel.append({
                "key": headers[i].key,
                "title": headers[i].title,
                "width": 1,
            })
        }
        // TODO 测试
        dataModel.append({
            "path": "111",
            "time": "222",
            "state": "333333",
        })
        for(let i = 0;i < 50; i++)
            dataModel.append({
                "path": "44444",
                "time": "55555555555555",
                "state": "666",
            })
        updateWidth(true)
    }

    // ========================= 【逻辑】 =========================

    property bool isLock: false
    // 表头， key title width
    ListModel { id: headerModel }
    // 数据， 项为headers的key
    ListModel { id: dataModel }

    // 宽度更新
    Timer {
        id: updateWidthTimer
        interval: 100
        repeat: false
        onTriggered: {
            updateWidth(true)
        }
    }
    // 更新全部宽度
    function updateWidth(timer=false) {
        if(!timer) { // 启动计时器，减少调用频率
            updateWidthTimer.restart()
            return
        }
        console.log("#")
        let ws = Array(columnCount).fill(1)
        // 表头
        for(let i = 1; i < columnCount; i++) {
            let maxWidth = headerRepeater.itemAt(i).maxWidth + fTableRoot.spacing
            if(maxWidth > ws[i]) ws[i] = maxWidth
        }
        // 表体
        for(let y in tableView.items) {
            const repeater = tableView.items[y].repeater
            for(let x = 1; x < columnCount; x++) {
                let maxWidth = repeater.itemAt(x).maxWidth + fTableRoot.spacing
                if(maxWidth > ws[x]) ws[x] = maxWidth
            }
        }
        // 赋值 / 计算第0列宽度
        let w0 = tableArea.width
        for(let i = 1; i < columnCount; i++) {
            headerModel.setProperty(i, "width", ws[i])
            w0 -= ws[i]
        }
        // 更新第0列宽度
        updateWidth0(w0)
    }
    // 更新第0列宽度
    function updateWidth0(w0 = -1) {
        if(headerModel.count <= 0) return
        if(w0 < 0) {
            w0 = tableArea.width
            for(let i = 1; i < columnCount; i++)
                w0 -= headerModel.get(i).width
        }
        if(w0 < minWidth0) w0 = minWidth0
        headerModel.setProperty(0, "width", w0)
    }

    // ========================= 【布局】 =========================

    // 表格区域
    Rectangle {
        id: tableArea
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
                height: size_.line * 2

                // 左打开图片按钮
                IconTextButton {
                    id: openBtn
                    visible: parent.width > openBtn.width + clearBtn.width // 容器宽度过小时隐藏
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.margins: size_.smallSpacing * 0.5
                    icon_: "folder"
                    text_: openBtnText

                    onClicked: {
                        if(isLock) return
                        fileDialog.open()
                    }
                }

                // 右清空按钮
                IconTextButton {
                    id: clearBtn
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.margins: size_.smallSpacing * 0.5
                    icon_: "clear"
                    text_: clearBtnText

                    onClicked: {
                        if(isLock) return
                        fTableRoot.clear()
                    }
                }
            }

            // 提示
            DefaultTips {
                visibleFlag: fTableRoot.rowCount
                anchors.top: tableTopPanel.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                tips: defaultTips
            }

            // 表头
            Item {
                id: tableHeaderContainer
                anchors.top: tableTopPanel.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: size_.line * 1.5
                onWidthChanged: updateWidth0()

                Row {
                    anchors.fill: parent
                    Repeater {
                        model: headerModel
                        id: headerRepeater
                        Rectangle {
                            width: model.width
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            color: theme.bgColor
                            border.width: 1
                            border.color: theme.coverColor2
                            property alias maxWidth: hText.width
                            Text_ {
                                id: hText
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                anchors.horizontalCenter: parent.horizontalCenter
                                verticalAlignment: Text.AlignVCenter // 垂直居中
                                font.pixelSize: size_.smallText
                                text: model.title
                            }
                        }
                    }
                }
            }
            // 表体
            TableView {
                id: tableView
                anchors.top: tableHeaderContainer.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                flickableDirection: Flickable.VerticalFlick // 只允许垂直滚动
                boundsBehavior: Flickable.StopAtBounds // 禁止flick过冲。不影响滚轮滚动的过冲
                model: dataModel
                clip: true
                property var items: tableView.children[0].children
                delegate: Item {
                    Component.onCompleted: updateWidth()
                    TableView.onReused: updateWidth()
                    implicitHeight: size_.smallLine * 1.5
                    implicitWidth: 1
                    property int rowIndex: index
                    property var rowModel: model
                    property alias repeater: repeater
                    Row {
                        anchors.fill: parent
                        Repeater {
                            id: repeater
                            model: headerModel
                            Rectangle {
                                width: model.width
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                color: theme.bgColor
                                border.width: 1
                                border.color: theme.coverColor2
                                property alias maxWidth: hText.width
                                property int columnIndex: index
                                property string columnKey: model.key
                                Text_ {
                                    id: hText
                                    anchors.top: parent.top
                                    anchors.bottom: parent.bottom
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    verticalAlignment: Text.AlignVCenter // 垂直居中
                                    font.pixelSize: size_.smallText
                                    color: theme.subTextColor
                                    text: rowModel[columnKey]
                                }
                            }
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
                radius: size_.btnRadius
            }
        }
    }

    // 文件选择对话框
    // QT-5.15.2 会报错：“Model size of -225 is less than 0”，不影响使用。
    // QT-5.15.5 修复了这个Bug，但是PySide2尚未更新到这个版本号。只能先忍忍了
    // https://bugreports.qt.io/browse/QTBUG-92444
    FileDialog_ {
        id: fileDialog
        title: fileDialogTitle
        nameFilters: fileDialogNameFilters
        folder: shortcuts.pictures
        selectMultiple: true // 多选
        onAccepted: {
            addKeys(fileDialog.fileUrls_)
        }
    }
}