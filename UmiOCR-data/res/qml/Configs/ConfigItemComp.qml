// =============================================
// =============== 参数项组件基类 ===============
// =============================================

import QtQuick 2.15
import "../Widgets"

Item {
    property string key: "" // valueDict的键
    property var configs: undefined // 保存对Configs组件的引用
    property var updateUI: ()=>{console.log(`${key} 更新设置UI为${value()}`)} // 更新UI函数，子类重写，通过value()获取最新值
    property int cursorShape_: Qt.ArrowCursor // 鼠标指针

    property string title: "" // 标题，可不填
    property var origin: undefined // 起源参数（静态）

    anchors.left: parent.left
    anchors.right: parent.right
    height: theme.textSize + theme.spacing
    clip: true
    // 初始化
    Component.onCompleted: {
        origin = configs.originDict[key]
        title = origin.title
        updateUI()
    }
    // 获取或设置值
    function value(v=undefined) {
        if(v===undefined) { // 获取
            return configs.getValue(key)
        }
        else { // 设置
            configs.setValue(key, v)
        }
    }
    
    // 左边 标题
    Text_ {
        text: title
        anchors.left: parent.left
        anchors.leftMargin: theme.smallSpacing
        anchors.verticalCenter: parent.verticalCenter
    }
    // 背景
    MouseAreaBackgroud {
        cursorShape: cursorShape_
    }
}