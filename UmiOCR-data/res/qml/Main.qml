// =====================================
// =============== 主窗口 ===============
// =====================================

import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15
import Qt.labs.settings 1.1

import "Themes"
import "TabView_"

Window {
// ApplicationWindow {
    id: root
    visible: true
    // flags: Qt.Window | Qt.FramelessWindowHint // 无边框窗口，保留任务栏图标

    width: 800
    height: 500
    minimumWidth: 600
    minimumHeight: 400

    color: "#00000000"

    // ========================= 【控制】 =========================

    // 全局样式，通过 theme 来访问
    property Theme theme: ThemeLight{}
    // property Theme theme: ThemeDark{}

    // 全局逻辑，通过 app 来访问
    Item {
        id: app

        // 标签页逻辑管理器
        TabViewManager { id: tab_ }
        property var tab: tab_ // 通过 app.tab 来访问

        // 持久化存储
        Settings { 
            id: settings
            category: "TabPage" // 自定义类别名称
            fileName: "./.settings_ui.ini" // 配置文件名


            property alias openPageList: tab_.openPageList
            property alias showPageIndex: tab_.showPageIndex
            property alias barIsLock: tab_.barIsLock

            property bool refresh: false // 用于刷新
            function save(){ // 手动刷新
                refresh=!refresh
            }
        }
    }

    // ========================= 【布局】 =========================

    // 主窗口的容器，兼做边框
    Rectangle {
        id: mainContainer
        anchors.fill: parent
        color: "#00000000"
        radius: theme.windowRadius // 窗口圆角

        // 主窗口的内容
        Rectangle {
            id: main
            anchors.fill: parent
            anchors.margins: 0 // 透明边框宽度

            color: theme.bgColor // 整个窗口的背景颜色
            radius: theme.windowRadius // 窗口圆角

            // 标签视图
            TabView_ { }

            // 裁切子元素，并应用圆角
            layer.enabled: true
            layer.effect: OpacityMask {
                maskSource: Rectangle {
                    width: main.width
                    height: main.height
                    radius: theme.windowRadius
                }
            }
        }
    }
}