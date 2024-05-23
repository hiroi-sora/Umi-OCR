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
        {key: "path", title: "文件", },
        {key: "time", title: "耗时", },
        {key: "state", title: "状态", },
        // 可选项：
        // btn:  true 启用按钮
        // onClicked: 单击函数
        // left: true 左对齐
        // display: 显示函数，输入value，返回显示文本
    ]
    property string openBtnText: "选择文件"
    property string clearBtnText: "清空"
    property string defaultTips: "拖入或选择文件"
    property string fileDialogTitle: "请选择文件"
    property var fileDialogNameFilters: ["文件 (*.jpg *.jpe *.jpeg *.jfif *.png *.webp *.bmp *.tif *.tiff)"]
    property int spacing: size_.smallLine // 表项水平间隔
    property int minWidth0: size_.smallLine * 5 // 第0列最小宽度
    property bool isLock: false // 是否锁定UI操作


    // ========================= 【调用接口】 =========================

    // 增：添加一项。 row：字典，key在headers中，如 { "path" "time" "state" }
    // ik：可以是表格行index（int），也可以是总key（string）
    function add(row, ik=-1) {
        const key = row[headerKey]
        if(key in dataDict) {
            console.log(`[Warning] add: ${key} 已在dataDict中！`)
            return false
        }
        if(ik === -1 || ik === rowCount) {
            dataDict[key] = rowCount
            dataModel.append(row)
        }
        else {
            const i = ik2i(ik)
            if(i < 0) {
                console.log(`[Warning] add: ik ${ik} ${i} < 0 ！`)
                return false
            }
            dataDict[key] = i
            dataModel.insert(i, row)
        }
        updateWidth()
        return true
    }
    // 删：删除一项
    function del(ik) {
        const i = ik2i(ik)
        if(i < 0) {
            console.log(`[Warning] del: ik ${ik} ${i} < 0 ！`)
            return false
        }
        const key = dataModel.get(i)[headerKey]
        delete dataDict[key]
        dataModel.remove(i)
        return true
    }
    // 删：清空
    function clear() {
        dataModel.clear()
        dataDict = {}
    }
    // 改：属性字典
    function set(ik, columnDict) {
        const i = ik2i(ik)
        if(i < 0) {
            console.log(`[Warning] set: ik ${ik} ${i} < 0 ！`)
            return false
        }
        dataModel.set(i, columnDict)
        updateWidth()
        return true
    }
    // 改：单个属性
    function setProperty(ik, columnKey, value) {
        const i = ik2i(ik)
        if(i < 0) {
            console.log(`[Warning] setProperty: ik ${ik} ${i} < 0 ！`)
            return false
        }
        dataModel.setProperty(i, columnKey, value)
        updateWidth()
        return true
    }
    // 查：ik转index。返回-1表示失败。
    function ik2i(ik) {
        if (typeof ik === "number") {
            if(ik >= 0 && ik < rowCount)
                return ik
        } else if (typeof ik === "string") {
            if(ik in dataDict)
                return dataDict[ik]
        }
        return -1
    }
    // 查：获取单个行的字典
    function get(ik) {
        const i = ik2i(ik)
        if(i < 0) {
            console.log(`[Warning] get: ik ${ik} ${i} < 0 ！`)
            return {}
        }
        return dataModel.get(i)
    }
    // 查：获取key列的所有数据，返回每项为value
    function getColumnsValue(key) {
        let list = []
        for(let y = 0; y < rowCount; y++) {
            list.push( dataModel.get(y)[key] )
        }
        return list
    }
    // 查：获取多个列的数据，返回每项为字典
    function getColumnsValues(keys=[]) {
        let list = []
        if(keys.length > 0) {
            for(let y = 0; y < rowCount; y++) {
                const data = dataModel.get(y)
                const d = {}
                for(let i in keys)
                    d[keys[i]] = data[keys[i]]
                list.push(d)
            }
        }
        else {
            for(let y = 0; y < rowCount; y++)
                list.push(dataModel.get(y))
        }
        return list
    }

    // 定义信号
    signal addPaths(var paths) // 添加文件的信号
    signal click(var info) // 点击条目的信号

    Component.onCompleted: {
        dataDict = {}
        columnCount = headers.length
        for(let i=0; i<columnCount; i++){
            headerModel.append({
                "key": headers[i].key,
                "title": headers[i].title,
                "width": 1,
            })
        }
        headerKey = headers[0].key
        updateWidth(true)
    }

    // ========================= 【逻辑】 =========================

    property int columnCount: 0 // 列数量， onCompleted 中初始化
    property int rowCount: dataModel.count // 行数量
    property string headerKey: "" // 自动
    // 表头， key title width
    ListModel { id: headerModel }
    // 数据， 项为headers的key
    ListModel { id: dataModel }
    property var dataDict: {} // 指向 dataModel 的 index
    onRowCountChanged: {
        headerModel.setProperty(0, "title", headers[0].title + ` (${rowCount})`)
    }

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
        let ws = Array(columnCount).fill(1)
        // 表头
        for(let i = 1; i < columnCount; i++) {
            let maxWidth = headerRepeater.itemAt(i).maxWidth + fTableRoot.spacing*2
            if(maxWidth > ws[i]) ws[i] = maxWidth
        }
        // 表体
        for(let y in tableView.items) {
            const repeater = tableView.items[y].repeater
            for(let x = 1; x < columnCount; x++) {
                let maxWidth = repeater.itemAt(x).maxWidth + fTableRoot.spacing*2
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
        w0 += columnCount-10 // 避让右侧滚动条空间
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
                visible: fTableRoot.rowCount > 0
                anchors.top: tableTopPanel.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: size_.line * 1.5
                onWidthChanged: updateWidth0()

                Row {
                    anchors.fill: parent
                    spacing: -1
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
                rowSpacing: -1
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
                        spacing: -1
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
                                property var header: headers[columnIndex]
                                clip: true
                                Button_ {
                                    visible: header.btn?true:false
                                    anchors.fill: parent
                                    radius: 0
                                    onClicked: {
                                        if(header.onClicked) {
                                            header.onClicked(rowIndex)
                                        }
                                    }
                                }
                                Text_ {
                                    id: hText
                                    property bool isLeft: headers[columnIndex].left?true:false
                                    anchors.top: parent.top
                                    anchors.bottom: parent.bottom
                                    anchors.left: isLeft? parent.left : undefined
                                    anchors.leftMargin: fTableRoot.spacing * 0.5
                                    anchors.horizontalCenter: isLeft? undefined : parent.horizontalCenter
                                    verticalAlignment: Text.AlignVCenter // 垂直居中
                                    font.pixelSize: size_.smallText
                                    color: (columnKey != "state"|| typeof rowModel.state != "string" || rowModel.state.length == 0) ? theme.subTextColor : 
                                        (rowModel.state.startsWith("×") ? theme.noColor : (rowModel.state.startsWith("√") ? theme.yesColor : theme.subTextColor))
                                    text: header.display ? header.display(rowModel[columnKey]) : rowModel[columnKey]
                                }
                            }
                        }
                    }
                }
                // 滚动条
                ScrollBar.vertical: ScrollBar { }
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
            addPaths(fileDialog.fileUrls_)
        }
    }
}