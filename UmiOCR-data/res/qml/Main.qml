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

        Item { // 全局延迟加载 初始化函数列表
            // qml中，组件初始化顺序是从上到下，而onCompleted调用顺序相反。
            // 故这个组件的onCompleted将是全局最后一个调用的。
            // 将各个组件的初始化函数放在这里，可以保证其他组件都已经构建完毕。
            id: initFuncs
            property var list: []
            property var list2: []
            property bool isComplete: false
            function push(f) { // 添加一个要延迟加载的函数。若当前全局已初始化，则直接执行
                if(isComplete) f()
                else list.push(f)
            }
            function push2(f) { // 添加一个要延迟加载的函数，比push()更晚执行
                if(isComplete) f()
                else list2.push(f)
            }
            Component.onCompleted: { // 全局初始化完毕，执行延迟加载的函数
                isComplete = true
                console.log("% 开始执行 延迟加载初始化函数！")
                for(let i in list) list[i]()
                for(let i in list2) list2[i]()
            }
        }
        
        GlobalConfigs { id: globalConfigs }  // 全局设置 qmlapp.globalConfigs
        ThemeManager { id: themeManager } // 主题管理器 qmlapp.themeManager
        TabViewManager { id: tab }  // 标签页逻辑管理器 qmlapp.tab
        PopupManager { id: popup }  // 弹窗管理器 qmlapp.popup
        MissionConnector { id: msnConnector } // 任务连接器 qmlapp.globalConfigs.msnConnector

        property alias initFuncs: initFuncs
        property alias globalConfigs: globalConfigs
        property alias themeManager: themeManager
        property alias tab: tab
        property alias popup: popup
        property alias msnConnector: msnConnector
        // 记录当前窗口状态，可见时为true。包括正常窗口、最大化、全屏。
        property bool isVisible: rootWindow.visibility==2||rootWindow.visibility==4||rootWindow.visibility==5
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