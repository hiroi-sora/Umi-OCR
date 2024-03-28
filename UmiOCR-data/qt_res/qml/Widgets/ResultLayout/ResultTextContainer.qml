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
    property string textRight: ""
    property alias textMain: textMain_.text
    property int index_
    // 选取文字
    property int selectL: -1
    property int selectR: -1
    property int selectUpdate: 0 // 只要有变化，就刷新选中
    // 外部函数
    property var copy: undefined // 复制选中
    property var copyAll: undefined // 复制全部
    property var selectSingle: undefined // 选中单个文本框
    property var selectAll: undefined // 所有文本框全选
    property var selectDel: undefined // 删除单个
    property var selectAllDel: undefined // 清空

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
    function focus(pos=-1) {
        if(pos >= 0 && textMain_.cursorPosition !== pos) {
            textMain_.cursorPosition = pos
        }
        if(!textMain_.activeFocus) {
            textMain_.forceActiveFocus() // 获取焦点
        }
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
        height: size_.smallLine + size_.spacing*2

        // 图片名称
        Text_ {
            id: textLeft_
            anchors.left: parent.left
            anchors.right: textRight_.left
            anchors.bottom: parent.bottom
            anchors.rightMargin: size_.spacing
            anchors.bottomMargin: size_.smallSpacing
            color: theme.subTextColor
            font.pixelSize: size_.smallText
            font.family: theme.dataFontFamily
            clip: true
            elide: Text.ElideLeft
        }
        // 日期时间
        Text_ {
            id: textRight_
            anchors.right: btnRight.left
            anchors.bottom: parent.bottom
            anchors.bottomMargin: size_.smallSpacing
            color: theme.subTextColor
            font.pixelSize: size_.smallText
            text: textRight + " | "
        }
        // 复制按钮
        Text_ {
            id: btnRight
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.bottomMargin: size_.smallSpacing
            color: theme.specialTextColor
            font.pixelSize: size_.smallText
            text: qsTr("复制")
        }
    }

    // 下方主要文字内容
    Rectangle {
        id: resultBottom
        color: theme.bgColor
        anchors.top: resultTop.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        // anchors.topMargin: size_.smallSpacing
        radius: size_.baseRadius
        height: textMain_.height

        TextEdit_ {
            id: textMain_
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: size_.smallSpacing
            anchors.rightMargin: size_.smallSpacing
            readOnly: false // 可编辑
            persistentSelection: true // 丢失焦点时，保留选区
            color: status_==="error"? theme.noColor:theme.textColor

            // 按键事件。响应并拦截：单双击 Ctrl+C ，双击 Ctrl+A
            property int keyDoubleTime: 300 // 双击毫秒
            property int lastUpTime: -1 // 上次按键抬起的时间戳。需要截取后8位以免int放不下
            property int lastKey: -1 // 上次按键的键值
            property var listeningKeys: [Qt.Key_A, Qt.Key_C, Qt.Key_D]
            Keys.onPressed: {
                if (event.modifiers & Qt.ControlModifier) {
                    if (listeningKeys.includes(event.key)) {
                        event.accepted = true // 拦截按键
                        const t = Date.now() & 0xFFFFFFFF
                        // 双击
                        if(t - lastUpTime <= keyDoubleTime && lastKey==event.key) {
                            event.key===Qt.Key_A && resultRoot.selectAll && resultRoot.selectAll()
                            event.key===Qt.Key_C && resultRoot.copyAll && resultRoot.copyAll()
                            event.key===Qt.Key_D && resultRoot.selectAllDel && resultRoot.selectAllDel()
                        }
                        else { // 单击
                            event.key===Qt.Key_A && resultRoot.selectSingle && resultRoot.selectSingle()
                            event.key===Qt.Key_C && resultRoot.copy && resultRoot.copy()
                        }
                    }
                }
            }
            Keys.onReleased: {
                if (listeningKeys.includes(event.key)) {
                    lastUpTime = Date.now() & 0xFFFFFFFF
                    lastKey = event.key
                }
            }
        }
    }
}