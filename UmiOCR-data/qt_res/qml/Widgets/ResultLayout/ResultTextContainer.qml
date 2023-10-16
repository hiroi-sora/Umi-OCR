// =======================================
// =============== 结果文本 ===============
// =======================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../"

Item {
    id: resultRoot

    property string status_: "" // 状态， text / noText / error
    property alias textLeft: textLeft_.text
    property alias textRight: textRight_.text
    property alias textMain: textMain_.text
    // 选取文字
    property int selectL: -1
    property int selectR: -1
    property int selectUpdate: 0 // 只要有变化，就刷新选中

    // 传入一个相对于item的坐标，返回该坐标位于this组件的什么位置。
    // undefined:不在组件中 | -1:顶部信息栏 | 0~N:所在字符的下标
    function where(item, mx, my) {
        const localPoint = this.mapFromItem(item, mx, my)
        if(!this.contains(localPoint)) {
            return undefined
        }
        if(resultTop.contains(localPoint)) {
            return -1
        }
        else {
            const textPoint = textMain_.mapFromItem(item, mx, my)
            const textPos = textMain_.positionAt(textPoint.x, textPoint.y)
            return textPos
        }

    }
    // 将光标移到指定位置并激活焦点。
    function focus(pos) {
        if(pos > 0)
            textMain_.cursorPosition = pos
        textMain_.forceActiveFocus() // 获取焦点
    }
    function toUpdateSelect() {
        if(selectL<0 || selectR<0)
            textMain_.deselect()
        else
            textMain_.select(selectL, selectR)
    }
    onSelectUpdateChanged: toUpdateSelect()
    TableView.onReused: toUpdateSelect()
    Component.onCompleted: toUpdateSelect()
    

    // 高度适应子组件
    implicitHeight: resultTop.height+resultBottom.height+size_.smallSpacing
    height: resultTop.height+resultBottom.height+size_.smallSpacing
    property var onTextHeightChanged // 当文字输入导致高度改变时，调用的函数

    onHeightChanged: { // 高度改变时，通知父级
        // 必须文本框获得焦点时才触发
        if(textMain_.activeFocus && (typeof onTextHeightChanged === "function"))
            onTextHeightChanged()
    }

    // 顶部信息
    Item {
        id: resultTop
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: size_.smallSpacing
        anchors.rightMargin: size_.smallSpacing
        height: size_.smallLine

        // 图片名称
        Text_ {
            id: textLeft_
            anchors.left: parent.left
            anchors.right: textRight_.left
            anchors.rightMargin: size_.spacing
            color: theme.subTextColor
            font.pixelSize: size_.smallText
            font.family: theme.dataFontFamily
            clip: true
            elide: Text.ElideLeft
        }
        // 日期时间
        Text_ {
            id: textRight_
            anchors.right: parent.right
            color: theme.subTextColor
            font.pixelSize: size_.smallText
        }
    }

    // 下方主要文字内容
    Rectangle {
        id: resultBottom
        color: theme.bgColor
        anchors.top: resultTop.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.topMargin: size_.smallSpacing
        radius: size_.baseRadius
        height: textMain_.height

        TextEdit {
            id: textMain_
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: size_.smallSpacing
            anchors.rightMargin: size_.smallSpacing
            wrapMode: TextEdit.Wrap // 尽量在单词边界处换行
            readOnly: false // 可编辑
            selectByMouse: true // 允许鼠标选择文本
            selectByKeyboard: true // 允许键盘选择文本
            color: status_==="error"? theme.noColor:theme.textColor
            font.pixelSize: size_.text
            font.family: theme.dataFontFamily
        }
    }
}