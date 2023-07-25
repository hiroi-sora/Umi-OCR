// ===========================================
// =============== 结果面板布局 ===============
// ===========================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import "../"

Item {

    // ========================= 【对外接口】 =========================

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
        resultsModel.append({
            "resStatus_": resStatus,
            "path": res.path,
            "fileName": res.fileName,
            "datetime": dateTimeString,
            "resText": resText,
        })
    }
    
    // ========================= 【布局】 =========================

    ListModel { id: resultsModel }
    anchors.fill: parent
    clip: true // 溢出隐藏

    // 左边表格
    TableView {
        id: tableView
        anchors.fill: parent
        anchors.rightMargin: theme.smallSpacing
        rowSpacing: theme.spacing // 行间隔
        contentWidth: parent.width // 内容宽度
        model: resultsModel // 模型
        flickableDirection: Flickable.VerticalFlick // 只允许垂直滚动

        // 宽度设定函数
        columnWidthProvider: (column)=>{
            if(column == 0){ // 第一列宽度，变化值
                return tableView.width
            }
        }
        onWidthChanged: forceLayout()  // 组件宽度变化时重设列宽
        // 元素
        delegate: ResultTextContainer {
            resStatus: resStatus_
            textLeft: fileName
            textRight: datetime
            textMain: resText
        } 
        ScrollBar.vertical: ScrollBar { }
    }
}