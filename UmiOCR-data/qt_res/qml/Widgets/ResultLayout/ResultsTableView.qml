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

    // 添加一条OCR结果。元素：
    // timestamp 时间戳，秒为单位
    // title 左边显示标题，可选
    // code 结果代码， data 结果内容
    // 返回结果字符串
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
        let status_ = ""
        let resText = ""
        switch(res.code){
            case 100: // 成功
                status_ = "text"
                const textArray = res.data.map(item => item.text);
                resText = textArray.join('\n');
                break
            case 101: // 无文字
                status_ = "noText"
                break
            default: // 失败
                status_ = "error"
                resText = qsTr("异常状态码：%1\n异常信息：%2").arg(res.code).arg(res.data)
                break
        }
        // 补充空白标题
        if(res.title === undefined) {
            const t1 = res.time.toFixed(2)
            res.title = qsTr("耗时 %1").arg(t1)
            if(res.score > 0) {
                const t2 = res.score.toFixed(2)
                res.title += " | "+qsTr("置信 %1").arg(t2)
            }
        }
        // 添加到列表模型
        resultsModel.append({
            "status__": status_,
            "title": res.title,
            "datetime": dateTimeString,
            "resText": resText,
            "timestamp": res.timestamp,
            "selectL_": -1,
            "selectR_": -1,
            "selectUpdate_": 0,
        })
        // 自动滚动
        if(autoToBottom) {
            tableView.toBottom()
        }
        return resText
    }

    // 搜索一个结果。可传入 title 或 timestamp
    function getResult(title="", timestamp=-1) {
        for (let i = 0, l=resultsModel.count; i < l; i++) {
            let item = resultsModel.get(i);
            if (item.title === title || item.timestamp === timestamp) {
                return item
            }
        }
        return undefined
    }
    
    // ========================= 【布局】 =========================

    anchors.fill: parent
    clip: true // 溢出隐藏
    property bool autoToBottom: true // 自动滚动到底部

    // 内容滚动组件
    TableView {
        id: tableView
        anchors.fill: parent
        anchors.rightMargin: size_.smallSpacing
        rowSpacing: size_.spacing // 行间隔
        contentWidth: parent.width // 内容宽度
        model: resultsModel // 模型
        flickableDirection: Flickable.VerticalFlick // 只允许垂直滚动
        boundsBehavior: Flickable.StopAtBounds // 禁止flick过冲。不影响滚轮滚动的过冲

        // ==================== 【滚动和视觉相关】 ====================
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
        onWidthChanged: {  // 组件宽度变化时重设列宽
            Qt.callLater(()=>{ // 延迟调用
                tableView.forceLayout() 
            })
        }
        // ==================== 【元素】 ====================
        delegate: ResultTextContainer {
            status_: status__
            textLeft: title
            textRight: datetime
            textMain: resText
            selectL: selectL_
            selectR: selectR_
            selectUpdate: selectUpdate_
            property int index_: index
            onTextHeightChanged: tableView.forceLayout // 文字高度改变时重设列宽
            onTextMainChanged: {
                resultsModel.setProperty(index, "resText", textMain) // 文字改变时写入列表
            }
        } 
        // 滚动条
        ScrollBar.vertical: ScrollBar { id:scrollBar }
    }
    // ==================== 【跨文本框选取】 ====================
    MouseArea {
        id: tableMouseArea
        z: 10
        anchors.fill: parent
        anchors.rightMargin: size_.smallSpacing
        property var tableChi: tableView.children[0].children
        hoverEnabled: true
        property int startIndex: -1 // 拖拽开始时，文本框序号
        property int startTextIndex: -1 // 拖拽开始时，字符序号
        property int endIndex: -1 // 拖拽结束时，文本框序号
        property int endTextIndex: -1 // 拖拽结束时，字符序号
        property int selectUpdate: 0
        // 查询鼠标坐标位于哪个表格组件内 ，位于什么地方
        function getWhere() {
            const mx=mouseX, my=mouseY
            for(let i in tableChi) {
                const c = tableChi[i]
                const f = c.where(this, mx, my)
                if(f !== undefined) {
                    return {
                        "obj": c,
                        "index": c.index_, // 文本框序号
                        "where": f, // undefined:不在组件中 | -1:顶部信息栏 | 0~N:所在字符的下标
                    }
                }
            }
            return undefined
        }
        // 获取Index正确顺序
        function getIndexes() {
            let li, lt, ri, rt
            if(startIndex < endIndex) {
                li=startIndex; lt=startTextIndex; ri=endIndex; rt=endTextIndex;
            }
            else if(startIndex > endIndex) {
                li=endIndex; lt=endTextIndex; ri=startIndex; rt=startTextIndex;
            }
            else {
                li=ri=startIndex
                if(startTextIndex < endTextIndex) {
                    lt=startTextIndex; rt=endTextIndex;
                }
                else if(startTextIndex > endTextIndex) {
                    lt=endTextIndex; rt=startTextIndex;
                }
                else {
                    li=-1; lt=-1; ri=-1; rt=-1; // 单击，未选中
                }
            }
            return [li, lt, ri, rt]
        }
        // 根据 Index 的参数，选择对应文本。返回选取类型：
        function selectIndex() {
            const lr = getIndexes()
            const li=lr[0], lt=lr[1], ri=lr[2], rt=lr[3]
            // 遍历每个文本框数据
            for (let i = 0, l=resultsModel.count; i < l; i++) {
                if( li<0 || ri<0 || i<li || i>ri ) { // 未被选中
                    resultsModel.setProperty(i, "selectL_", -1)
                    resultsModel.setProperty(i, "selectR_", -1)
                }
                else if(i === li && i === ri) { // 单个块
                    resultsModel.setProperty(i, "selectL_", lt)
                    resultsModel.setProperty(i, "selectR_", rt)
                }
                else if(i === li) { // 多个块的起始
                    resultsModel.setProperty(i, "selectL_", lt)
                    let item = resultsModel.get(i)
                    resultsModel.setProperty(i, "selectR_", item.resText.length)
                }
                else if(i === ri) { // 多个块的结束
                    resultsModel.setProperty(i, "selectL_", 0)
                    resultsModel.setProperty(i, "selectR_", rt)
                }
                else { // 多个块的中间
                    resultsModel.setProperty(i, "selectL_", 0)
                    let item = resultsModel.get(i)
                    resultsModel.setProperty(i, "selectR_", item.resText.length)
                }
                resultsModel.setProperty(i, "selectUpdate_", selectUpdate) // 开始刷新
            }
            selectUpdate++
        }
        // 按下
        onPressed: {
            const info = getWhere()
            if(info===undefined || info.where<0) {
                startIndex=startTextIndex=endIndex=endTextIndex=-1
                return
            }
            if(info.where >= 0) {
                endIndex = startIndex = info.index
                endTextIndex = startTextIndex = info.where
            }
        }
        // 移动
        onPositionChanged: {
            const info = getWhere()
            // 根据所在区域，调整光标
            if(info===undefined) {
                tableMouseArea.cursorShape = Qt.ArrowCursor
                return
            }
            if(info.where >= 0) tableMouseArea.cursorShape = Qt.IBeamCursor
            else tableMouseArea.cursorShape = Qt.ArrowCursor
            // 拖拽中
            if(pressed) {
                if(startIndex===startTextIndex && startIndex===-1)
                    return
                endIndex = info.index
                endTextIndex = info.where
                selectIndex()
            }
        }
        // 抬起
        onReleased: {
            const info = getWhere()
            if(info===undefined || info.where<0) {
                startIndex=startTextIndex=endIndex=endTextIndex-1
                return
            }
            endIndex = info.index
            endTextIndex = info.where
            if(startIndex!==endIndex) { // 多块选中，预先激活本元素焦点，准备接收键盘事件
                tableMouseArea.forceActiveFocus()
            }
            selectIndex() // 选中
            if(startIndex===endIndex && startTextIndex===endTextIndex) {
                info.obj.focus(info.where) // 单击移动光标
            }
            else if(startIndex===endIndex) {
                info.obj.focus(-1) // 单块选中，激活焦点
            }
        }
        // 按键事件
        Keys.onPressed: {
            if (event.modifiers & Qt.ControlModifier) {
                // 复制
                if (event.key === Qt.Key_C) {
                    console.log("== copy: ")
                    const lr = getIndexes()
                    const li=lr[0], lt=lr[1], ri=lr[2], rt=lr[3]
                    if(li < 0 || ri < 0) return
                    let copyText = ""
                    for(let i = li; i <= ri; i++) {
                        let item = resultsModel.get(i)
                        if(i === li && i === ri) // 单个块
                            copyText = item.resText.substring(lt, rt)
                        else if(i === li) // 多个块的起始
                            copyText = item.resText.substring(lt)+"\n"
                        else if(i === ri) // 多个块的结束
                            copyText += item.resText.substring(0, rt)
                        else // 多个块的中间
                            copyText += item.resText+"\n"
                    }
                    if(copyText && copyText.length>0) {
                        console.log("== copy", copyText)
                        qmlapp.utilsConnector.copyText(copyText)
                    }
                }
            }
        }
    }

    // ==================== 【外置控制栏】 ====================
    Item {
        id: ctrlBar
        height: size_.line*1.5
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

/*
跨文本块选取

状态记忆：
    开始的块序号
        起始字符序号
    结束的块序号
        结束字符序号
块的判断：
    若为开始/结束块：
        选取指定字符范围
    若为中间块：
        选取所有字符

状态1：未选取
    点击：插入光标
    按住拖拽：选取
    松开：提取选取
    离开：进入多选状态

状态2：已选取（按住）
    进入：
*/