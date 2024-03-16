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
    property bool advanced: false // true时是高级选项

    anchors.left: parent.left
    anchors.right: parent.right
    clip: true
    // 这个选项是高级选项，且设置页未开启高级模式，则高度为0隐藏
    height: (advanced&&!configs.advanced) ? 0 : (size_.line + size_.spacing)
    visible: !(advanced&&!configs.advanced)

    // 初始化
    Component.onCompleted: {
        origin = configs.originDict[key]
        title = origin.title
        updateUI()
        // 如果设定了提示，则加载提示组件
        if(origin.toolTip) {
            toolTipLoader.sourceComponent = toolTip
        }
        if(origin.advanced) {
            advanced = origin.advanced
            title = "* "+title
        }
        Qt.callLater(() => { // 延迟一个事件循环，再激活背景鼠标响应
            mouseAreaBackgroud.hoverEnabled = true
        })
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
        anchors.leftMargin: size_.smallSpacing
        anchors.verticalCenter: parent.verticalCenter
    }
    // 背景
    MouseAreaBackgroud {
        id: mouseAreaBackgroud
        cursorShape: cursorShape_
        hoverEnabled: false
    }
    // 提示
    Component {
        id: toolTip
        ToolTip_ {
            visible: mouseAreaBackgroud.hovered
            text: origin.toolTip
        }
    }
    Loader { id: toolTipLoader } // 默认不加载
}