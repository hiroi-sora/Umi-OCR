// =====================================================
// =============== 可切换左右/上下双栏布局 ===============
// =====================================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {

    // ========================= 【可调参数】 =========================

    property QtObject itemA // 第一子组件，左或上
    property QtObject itemB // 第二子组件，右或下
    property bool isRow: true // t为左右布局，f为上下
    property string saveKey: "" // 如果非空，则缓存 isRow 和布局的 hide 参数。
    // 只读：0为不隐藏，1为隐藏第一子组件，2为隐藏第二子组件
    property int hideAB: 0

    id: doubleLayout

    Component.onCompleted: {
        // 取 isRow 缓存
        Qt.callLater(() => {
            if(doubleLayout.saveKey) {
                const layoutDict = qmlapp.globalConfigs.getValue("window.doubleLayout")
                const f = layoutDict[doubleLayout.saveKey]
                if(f === true || f === false) isRow = f // bool类型合法性检查
            }
        })
    }

    // 切换布局
    function toSwitchView(toRow) { // isRow 要变为的值
        isRow = toRow
        hideAB = doubleLayout.isRow ? rowLayout.hideLR : columnLayout.hideTB
        // 缓存 isRow
        if(doubleLayout.saveKey) {
            let layoutDict = qmlapp.globalConfigs.getValue("window.doubleLayout")
            layoutDict[doubleLayout.saveKey] = toRow
            qmlapp.globalConfigs.setValue("window.doubleLayout", layoutDict)
        }
    }

    // 左右布局
    DoubleRowLayout {
        id: rowLayout
        anchors.fill: parent
        visible: doubleLayout.isRow
        leftItem: doubleLayout.isRow ? itemA : placeholderA
        rightItem: doubleLayout.isRow ? itemB : placeholderB
        isShowSplitView: true
        saveKey: doubleLayout.saveKey==="" ? "" : doubleLayout.saveKey+"row"
        onSwitchView: toSwitchView(false)
        onHideLRChanged: {
            if(doubleLayout.isRow) doubleLayout.hideAB = hideLR
        }
    }
    // 上下布局
    DoubleColumnLayout {
        id: columnLayout
        anchors.fill: parent
        visible: !doubleLayout.isRow
        topItem: doubleLayout.isRow ? placeholderA : itemA
        bottomItem: doubleLayout.isRow ? placeholderB : itemB
        isShowSplitView: true
        saveKey: doubleLayout.saveKey==="" ? "" : doubleLayout.saveKey+"col"
        onSwitchView: toSwitchView(true)
        onHideTBChanged: {
            if(!doubleLayout.isRow) doubleLayout.hideAB = hideTB
        }
    }

    // 临时占位用子组件
    Item {
        id: placeholderA
        visible: false
    }
    Item {
        id: placeholderB
        visible: false
    }
}