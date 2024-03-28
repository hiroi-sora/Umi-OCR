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
        // let dateTimeString = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
        let dateTimeString = `${hours}:${minutes}`
        // 提取结果文本和状态
        let status_ = ""
        let resText = ""
        switch(res.code){
            case 100: // 成功
                status_ = "text"
                const l = res.data.length
                for(let i=0; i<l; i++) {
                    resText += res.data[i].text
                    if(i<l-1)
                        resText += res.data[i].end || "" // 行尾分隔符
                }
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
                res.title += " | "+qsTr("置信度 %1").arg(t2)
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
            "source": JSON.stringify(res), // 保存原始数据
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
    property real scrollBarWidth: size_.spacing * 1.5 // 滚动条区域宽度

    // 内容滚动组件
    TableView {
        id: tableView
        anchors.fill: parent
        anchors.rightMargin: scrollBarWidth
        rowSpacing: size_.smallSpacing // 行间隔
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
            index_: index
            onTextHeightChanged: tableView.forceLayout // 文字高度改变时重设列宽
            onTextMainChanged: {
                resultsModel.setProperty(index, "resText", textMain) // 文字改变时写入列表
            }
            copy: tableMouseArea.selectCopy
            copyAll: tableMouseArea.selectAllCopy
            selectAll: tableMouseArea.selectAll
            selectSingle: tableMouseArea.selectSingle
            selectDel: tableMouseArea.selectDel
            selectAllDel: tableMouseArea.selectAllDel
        } 
        // 滚动条
        ScrollBar.vertical: scrollBar
    }
    // ==================== 【跨文本框选取】 ====================
    MouseArea {
        id: tableMouseArea
        z: 10
        anchors.fill: parent
        anchors.rightMargin: scrollBarWidth
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        property var tableChi: tableView.children[0].children
        hoverEnabled: true
        property int startIndex: -1 // 拖拽开始时，文本框序号
        property int startTextIndex: -1 // 拖拽开始时，字符序号
        property int endIndex: -1 // 拖拽结束时，文本框序号
        property int endTextIndex: -1 // 拖拽结束时，字符序号
        property int selectUpdate: 0
        // 查询鼠标坐标位于哪个表格组件内 ，位于什么地方
        // 若 outside==true：则允许鼠标跑到组件以外，会计算鼠标离组件内最近的点。
        function getWhere(outside = false) {
            let mx=mouseX, my=mouseY
            if(outside) { // 允许出界时，将出界的x回归到界内
                if(mx < 0) mx = 0
                if(mx > tableMouseArea.width) mx = tableMouseArea.width
            }
            for(let i in tableChi) {
                const c = tableChi[i]
                let f = c.where(this, mx, my)
                if(outside && f===-1) f = 0 // 允许出界时，将标题栏视为首字符区域
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
                else { // 单击，未选中
                    li = ri = startIndex
                    lt = rt = -1
                }
            }
            return [li, lt, ri, rt]
        }
        // 根据 Index 的参数，选择对应文本。
        function selectIndex() {
            const [li, lt, ri, rt] = getIndexes()
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
        // 选中单个文本框
        function selectSingle() {
            if(endIndex < 0) return
            let item = resultsModel.get(endIndex)
            startTextIndex = 0
            endTextIndex = item.resText.length
            startIndex = endIndex
            selectIndex()
        }
        // 全选
        function selectAll() {
            if(resultsModel.count === 0) return
            startIndex = startTextIndex = 0
            endIndex = resultsModel.count-1
            endTextIndex = resultsModel.get(endIndex).resText.length
            selectIndex()
        }
        // 复制已选中的内容，或当前块的所有文本
        function selectCopy() {
            // 若当前没有选中的内容，但指针放在一个块上，则选择该块
            if(startIndex>=0 && startIndex===endIndex && startTextIndex===endTextIndex) {
                selectSingle()
            }
            let [li, lt, ri, rt] = getIndexes()
            if(li >= 0 && ri >= 0) {
                let copyText = ""
                for(let i = li; i <= ri; i++) {
                    const item = resultsModel.get(i)
                    if(item.resText) {
                        // 范围检查
                        const text = item.resText
                        const len = text.length
                        if (lt < 0) lt = 0
                        if (lt > len) lt = len
                        if (rt < lt) rt = lt
                        if (rt > len) rt = len
                        // 获取文本
                        if(i === li && i === ri) // 单个块
                            copyText = text.substring(lt, rt)
                        else if(i === li) // 多个块的起始
                            copyText = text.substring(lt)+"\n"
                        else if(i === ri) // 多个块的结束
                            copyText += text.substring(0, rt)
                        else // 多个块的中间
                            copyText += text+"\n"
                    }
                }
                if(copyText && copyText.length>0) {
                    qmlapp.utilsConnector.copyText(copyText)
                    qmlapp.popup.simple(qsTr("记录：复制%1字").arg(copyText.length), "")
                    return copyText
                }
            }
            qmlapp.popup.simple(qsTr("记录：无选中文字"), "")
            return ""
        }
        // 复制所有
        function selectAllCopy() {
            let copyText = ""
            for (let i = 0, l=resultsModel.count; i < l; i++) {
                let item = resultsModel.get(i)
                if(item.resText) {
                    copyText += item.resText
                    if(i < l-1) copyText += "\n"
                }
            }
            qmlapp.utilsConnector.copyText(copyText)
            qmlapp.popup.simple(qsTr("记录：复制全部%1字").arg(copyText.length), "")
            selectAll()
        }
        // 删除选中的文本框
        function selectDel() {
            const [li, lt, ri, rt] = getIndexes()
            if(li < 0 || ri < 0) return
            const l = ri-li+1
            resultsModel.remove(li, l)
            qmlapp.popup.simple(qsTr("删除%1条记录").arg(l), "")
        }
        // 删除全部
        function selectAllDel() {
            resultsModel.clear()
            qmlapp.popup.simple(qsTr("清空记录"), "")
        }
        // 按下
        onPressed: {
            if (mouse.button === Qt.RightButton) {
                selectMenu.popup()
                return
            }
            const info = getWhere()
            if(info === undefined) { // 无效区域
                startIndex=startTextIndex=endIndex=endTextIndex=-1
            }
            else if(info.where === -1) { // 标题栏区域
                endIndex = startIndex = info.index
                startTextIndex = endTextIndex = -1
                selectCopy()
                startIndex = startTextIndex = -1 // 复制完后，将start归为-1
            }
            else if(info.where >= 0) { // 文本区域
                endIndex = startIndex = info.index
                endTextIndex = startTextIndex = info.where
                info.obj.focus(info.where) // 放置光标 & 赋予焦点
            }
        }
        // 移动
        onPositionChanged: {
            const info = getWhere(pressed)
            // 根据所在区域，调整光标
            if(info===undefined) {
                tableMouseArea.cursorShape = Qt.ArrowCursor
                return
            }
            if(info.where >= 0) tableMouseArea.cursorShape = Qt.IBeamCursor
            else if(info.where >= -1) tableMouseArea.cursorShape = Qt.PointingHandCursor
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
            if (mouse.button === Qt.RightButton) {
                return
            }
            const info = getWhere()
            if(info===undefined || info.where<0) {
                if(startIndex >= 0)
                    selectIndex()
                return
            }
            endIndex = info.index
            endTextIndex = info.where
            selectIndex() // 选中
            if(startIndex===endIndex && startTextIndex===endTextIndex) {
                info.obj.focus(info.where) // 单击移动光标
            }
            else {
                info.obj.focus(-1) // 激活焦点
            }
        }
        // 菜单
        Menu_ {
            id: selectMenu
            menuList: [
                [tableMouseArea.selectCopy, qsTr("复制　　　　（Ctrl+C）")],
                [tableMouseArea.selectAllCopy, qsTr("复制全部　　（Ctrl+C 双击）")],
                [tableMouseArea.selectSingle, qsTr("选中单个　　（Ctrl+A）")],
                [tableMouseArea.selectAll, qsTr("选中全部记录（Ctrl+A 双击）")],
                [tableMouseArea.selectDel, qsTr("删除选中记录"), "noColor"],
                [tableMouseArea.selectAllDel, qsTr("清空全部记录（Ctrl+D 双击）"), "noColor"],
            ]
        }
    }
    // ==================== 【滚动条】 ====================
    ScrollBar {
        id:scrollBar
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        width: scrollBarWidth 
    }

    // ==================== 【外置控制栏】 ====================
    Item {
        id: ctrlBar
        height: size_.line*1.5
        anchors.left: parent.left
        anchors.right: parent.right

        Row {
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.right: parent.right

            CheckButton {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
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
            // 菜单
            IconButton {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: height
                icon_: "menu"
                color: theme.textColor
                onClicked: selectMenu.popup()
                toolTip: qsTr("右键菜单")
            }
        }
    }
}