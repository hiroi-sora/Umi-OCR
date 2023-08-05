// =====================================
// =============== 主窗口 ===============
// =====================================

import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15
import Qt.labs.settings 1.1
import MissionConnector 1.0 // Python任务连接器

import "Themes"
import "TabView_"
import "Configs"
import "Popup_"
import "TabPages/GlobalConfigsPage"

Window {
    id: rootWindow // 通过 qmlapp.rootWindow 访问
    visible: true
    property bool isOnTop: false // 标记是否置顶
    // 窗口 | 自定义标题栏 | 有标题 | 有系统菜单 | 有最小最大化按钮 | 有关闭按钮 | 根据条件是否置顶
    flags: Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint 
        | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint | (isOnTop?Qt.WindowStaysOnTopHint:0)

    width: 800
    height: 500
    minimumWidth: 400
    minimumHeight: 400
    color: "#00000000"
    
    // ========================= 【控制】 =========================

    // 全局样式，通过 theme 来访问
    property Theme theme: ThemeLight{}

    // 全局单例，通过 qmlapp. 来访问
    Item {
        id: qmlapp
        property alias rootWindow: rootWindow

        GlobalConfigs { id: globalConfigs }  // 全局设置 qmlapp.globalConfigs
        ThemeManager { id: themeManager } // 主题管理器 qmlapp.themeManager
        TabViewManager { id: tab }  // 标签页逻辑管理器 qmlapp.tab
        PopupManager { id: popup }  // 弹窗管理器 qmlapp.popup
        MissionConnector { id: msnConnector } // 任务连接器 qmlapp.globalConfigs.msnConnector

        property alias globalConfigs: globalConfigs
        property alias themeManager: themeManager
        property alias tab: tab
        property alias popup: popup
        property alias msnConnector: msnConnector
        // 记录当前窗口状态，可见时为true。包括正常窗口、最大化、全屏。
        property bool isVisible: rootWindow.visibility==2||rootWindow.visibility==4||rootWindow.visibility==5

        // 延时加载标签页
        Component.onCompleted: { // 全局初始化完毕，执行延迟加载的函数
            Qt.callLater(()=>{
                qmlapp.tab.init()
            })
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
            id: mainUI
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
                    width: mainUI.width
                    height: mainUI.height
                    radius: theme.windowRadius
                }
            }
        }
    }

    // ========================= 【主窗UI存储】 =========================
    
    // 持久化存储
    Settings_ { 
        id: rootSettings
        category: "MainWindow"

        property alias winIsOnTop: rootWindow.isOnTop
    }
}