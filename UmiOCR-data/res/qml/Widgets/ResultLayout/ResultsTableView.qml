// ===========================================
// =============== 结果面板布局 ===============
// ===========================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import "../"

Item {
    ListModel { id: resultsModel } // OCR结果模型

    // ========================= 【对外接口】 =========================

    property alias ctrlBar: ctrlBar // 控制栏的引用

    // 添加一条OCR结果
    function addOcrResult(res) {
        // 提取并转换结果时间
        let date = new Date(res.timestamp * 1000)  // 时间戳转日期对象
        let year = date.getFullYear()
        let month = ('0' + (date.getMonth() + 1)).slice(-2)
        let day = ('0' + date.getDate()).slice(-2)
        let hours = ('0' + date.getHours()).slice(-2)
        let minutes = ('0' + date.getMinutes()).slice(-2)
        let seconds = ('0' + date.getSeconds()).slice(-2)
        let dateTimeString = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
        // 提取结果文本和状态
        let resStatus = ""
        let resText = ""
        switch(res.code){
            case 100: // 成功
                resStatus = "text"
                const textArray = res.data.map(item => item.text);
                resText = textArray.join('\n');
                break
            case 101: // 无文字
                resStatus = "noText"
                break
            default: // 失败
                resStatus = "error"
                resText = qsTr("异常状态码：%1\n异常信息：%2").arg(res.code).arg(res.data)
                break
        }
        // 添加到列表模型
        resultsModel.append({
            "resStatus_": resStatus,
            "path": res.path,
            "fileName": res.fileName,
            "datetime": dateTimeString,
            "resText": resText,
        })
        // 自动滚动
        if(autoToBottom) {
            tableView.toBottom()
        }
    }
    
    // ========================= 【布局】 =========================

    anchors.fill: parent
    clip: true // 溢出隐藏
    property bool autoToBottom: true // 自动滚动到底部

    // 内容滚动组件
    TableView {
        id: tableView
        anchors.fill: parent
        anchors.rightMargin: theme.smallSpacing
        rowSpacing: theme.spacing // 行间隔
        contentWidth: parent.width // 内容宽度
        model: resultsModel // 模型
        flickableDirection: Flickable.VerticalFlick // 只允许垂直滚动
        boundsBehavior: Flickable.StopAtBounds // 禁止flick过冲。不影响滚轮滚动的过冲

        // 滚动到底部
        function toBottom() {
            bottomTimer.running = true
        }
        Timer {
            id: bottomTimer
            interval: 100
            running: false
            repeat: true // 重复执行
            onTriggered: {
                // 已滚动到底部
                if(scrollBar.position  >= (1 - scrollBar.size)) {
                    bottomTimer.running = false
                    tableView.returnToBounds() // 确保未越界
                }
                // 未滚动到底部，重复将滚动条拉到底
                else {
                    scrollBar.position = (1 - scrollBar.size)
                }
            }
        }
        // 宽度设定函数
        columnWidthProvider: (column)=>{
            if(column == 0){ // 第一列宽度，变化值
                return tableView.width
            }
        }
        onWidthChanged: tableView.forceLayout()  // 组件宽度变化时重设列宽
        // 元素
        delegate: ResultTextContainer {
            resStatus: resStatus_
            textLeft: fileName
            textRight: datetime
            textMain: resText
            onTextHeightChanged: tableView.forceLayout // 文字高度改变时重设列宽
            onTextMainChanged: {
                resultsModel.setProperty(index, "resText", textMain) // 文字改变时写入列表
            }
        } 
        // 滚动条
        ScrollBar.vertical: ScrollBar { id:scrollBar }
    }

    // 外置控制栏
    Item {
        id: ctrlBar
        height: theme.textSize*1.5
        anchors.left: parent.left
        anchors.right: parent.right

        Button_ {
            id: ctrlBtn1
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            text_: qsTr("清空")
            textColor_: theme.noColor
            onClicked: {
                resultsModel.clear()
            }
        }
        CheckButton {
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.right: ctrlBtn1.left
            text_: qsTr("滚动")
            toolTip: qsTr("自动滚动到底部")
            textColor_: autoToBottom ? theme.textColor : theme.subTextColor
            checked: autoToBottom
            enabledAnime: true
            onCheckedChanged: {
                autoToBottom = checked
                if(checked) {
                    tableView.toBottom()
                }
                else {
                    bottomTimer.running = false
                }
            }
        }
    }
}