// =====================================
// =============== 主窗口 ===============
// =====================================

import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15
import Qt.labs.settings 1.1
import MissionConnector 1.0 // Python任务连接器
import KeyMouseConnector 1.0 // 键盘/鼠标连接器
import UtilsConnector 1.0 // 通用连接器

import "Themes"
import "TabView_"
import "Configs"
import "EventBus"
import "Popup_"
import "MainWindow"
import "ImageManager"

Window {
    id: mainWindowRoot
    visibility: Window.Hidden // 在 MainWindowManager 中启用可见性
    // 窗口 | 自定义标题栏 | 有标题 | 有系统菜单 | 有最小最大化按钮 | 有关闭按钮 | 根据条件是否置顶
    property bool isMainWindowTop: false
    flags: Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint 
        | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint | (isMainWindowTop?Qt.WindowStaysOnTopHint:0)

    width: 800
    height: 500
    minimumWidth: 400
    minimumHeight: 400
    color: "#00000000"
    title: UmiAbout.fullname
    
    // ========================= 【控制】 =========================

    // 全局样式，通过 theme 来访问
    property Theme theme: Theme{}
    // 全局尺寸，通过 size_ 来访问
    property Size_ size_: Size_{}

    // 全局单例，通过 qmlapp. 来访问
    Item {
        id: qmlapp

        // 普通全局单例
        TabViewManager { id: tab }  // 标签页逻辑管理器
        ImageManager { id: imageManager }  // 图片管理器
        MissionConnector { id: msnConnector } // 任务连接器
        PubSub { id: pubSub } // 全局事件发布/订阅
        KeyMouseConnector { id:keyMouse } // 鼠标/键盘
        UtilsConnector { id:utilsConnector } // 通用连接器

        // 必须先初始化的单例，onCompleted顺序从下往上
        MainWindowManager { id:mainWin; mainWin:mainWindowRoot } // 主窗管理
        SystemTray { id:systemTray } // 系统托盘
        PopupManager { id: popup }  // 弹窗管理器
        GlobalConfigs { id: globalConfigs }  // 全局设置

        property alias imageManager: imageManager
        property alias globalConfigs: globalConfigs
        property alias tab: tab
        property alias popup: popup
        property alias msnConnector: msnConnector
        property alias pubSub: pubSub
        property alias keyMouse: keyMouse
        property alias utilsConnector: utilsConnector
        property alias systemTray: systemTray
        property alias mainWin: mainWin
        property bool enabledEffect: false // 全局是否启用动画

        Component.onCompleted: {
            // 延时加载标签页
            Qt.callLater(()=>{
                qmlapp.tab.init()
            })
        }
    }

    onClosing: { // 窗口关闭事件
        close.accepted = false // 阻止原生事件
        mainWin.close() // 调用主窗管理器的关闭
    }

    // ========================= 【布局】 =========================

    // 主窗口的容器，兼做边框
    Rectangle {
        id: mainContainer
        anchors.fill: parent
        color: "#00000000"
        radius: size_.windowRadius // 窗口圆角

        // 为了防止主窗启动不显示时，内容的宽度初始值为0，先让内容挂到固定宽度的Item下
        Item {
            width: 800
            height: 500
            property alias mainWidth: mainContainer.width
            onMainWidthChanged: { // 主窗恢复显示时，再让内容挂回主窗
                if(mainUI.parent !== mainContainer)
                    mainUI.parent = mainContainer
            }

            // 主窗口的内容
            Rectangle {
                id: mainUI
                anchors.fill: parent
                anchors.margins: 0 // 透明边框宽度

                color: theme.bgColor // 整个窗口的背景颜色
                radius: size_.windowRadius // 窗口圆角

                // 标签视图
                TabView_ { }

                // 裁切子元素，并应用圆角
                layer.enabled: true
                layer.effect: OpacityMask {
                    maskSource: Rectangle {
                        width: mainUI.width
                        height: mainUI.height
                        radius: size_.windowRadius
                    }
                }
            }
        }
    }
}