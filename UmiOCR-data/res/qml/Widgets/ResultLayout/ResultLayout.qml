// ===========================================
// =============== 结果面板布局 ===============
// ===========================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../"

Rectangle {
    color: "#00000000"

    
    ListModel { // 所有页面的标题
        id: resultModel
    }
    
    Component.onCompleted: {
        
        resultModel.clear()
        for(let i=1,c=40; i<c; i++){
            resultModel.append({
                "textLeft_": "textLeft.text",
                "textRight_": "textRight.text",
                "textMain_": "textMain.text"
            })
        }
    }
    
    Item {
        anchors.fill: parent
        clip: true // 溢出隐藏

        // 左边表格
        TableView {
            id: tableView
            anchors.fill: parent
            anchors.rightMargin: theme.smallSpacing
            contentWidth: parent.width // 内容宽度
            model: resultModel // 模型
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
                textLeft: textLeft_
                textRight: textRight_
                textMain: textMain_
            } 
        }
        // 右边滚动条
        Rectangle {
            id: scrollbar
            visible: tableView.visibleArea.heightRatio < 1
            anchors.right: parent.right
            y: tableView.visibleArea.yPosition * parent.height
            height: tableView.visibleArea.heightRatio * parent.height
            width: theme.smallSpacing * 0.5
            color: theme.coverColor2
        }

    }

}