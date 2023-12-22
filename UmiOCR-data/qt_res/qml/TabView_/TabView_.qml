// =============================================================
// =============== 水平标签组件（即标签按钮位于顶部） =============
// =============================================================

import QtQuick 2.15
import QtQuick.Layouts 1.15
import "../TabBar_"

Rectangle {
    
    anchors.fill: parent

    // 标签页容器
    Rectangle {
        anchors.top: topBar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        color: theme.bgColor

        Component.onCompleted: {
            qmlapp.tab.page.pagesNest.parent = this
        }
    }

    // 标签栏容器
    Rectangle {
        id: topBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: size_.hTabBarHeight
        color: theme.tabBarColor
        clip: true

        HTabBar { }
    }
}