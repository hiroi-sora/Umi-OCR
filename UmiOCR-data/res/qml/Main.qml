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
import "Configs"
import "TabPages/GlobalConfigsPage"

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

    // 全局单例，通过 app. 来访问
    Item {
        id: app
        // 构建顺序由上到下，onCompleted的顺序相反（从下到上）
        GlobalConfigs { id: globalConfigs }  // 全局设置 app.globalConfigs
        ThemeManager { id: themeManager } // 主题管理器 app.themeManager
        TabViewManager { id: tab }  // 标签页逻辑管理器 app.tab

        property alias themeManager: themeManager
        property alias globalConfigs: globalConfigs
        property alias tab: tab
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