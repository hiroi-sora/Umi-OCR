// ===========================================
// =============== 主窗口管理器 ===============
// ===========================================

import QtQuick 2.15
import QtQuick.Window 2.15

Item {
    property var mainWin // 主窗口的引用
    property var screens: Qt.application.screens // 屏幕属性的引用
    
    property var mScreen: mainWin.screen
    property int mx: mainWin.x
    property int my: mainWin.y
    // ========================= 【保存量】 =========================
    
    // 主窗口属性初始化
    Component.onCompleted: {
        // 启动时可见
        const visi = !qmlapp.globalConfigs.getValue("window.startupInvisible")
        setVisibility(visi)
        if(!visi) {
            qmlapp.popup.simple(qsTr("欢迎使用 Umi-OCR"), qsTr("已启用后台模式，可通过快捷键使用功能。"))
        }
        // 检查屏幕位置，防止初始出界
        checkScreen()
    }

    // ========================= 【接口】 =========================

    // 返回主窗口是否可见
    function getVisibility() {
        return mainWin.visibility==2||mainWin.visibility==4||mainWin.visibility==5
    }

    // 设置主窗口可见性。 false 隐藏， true 恢复。
    function setVisibility(flag) {
        console.log("=== set!!!!!!")
        if(flag) {
            mainWin.visibility = Window.Windowed // 状态为可见
            mainWin.requestActivate() // 激活窗口
            mainWin.raise() // 弹到顶层
        }
        else {
            mainWin.visibility = Window.Hidden
        }
    }

    // 关闭主窗口
    function close() {
        // 隐藏
        if(qmlapp.globalConfigs.getValue("window.closeWin2Hide")) {
            setVisibility(false)
        }
        // 关闭
        else {
            Qt.quit()
        }
    }

    // 检查主窗口初始化屏幕位置，防止出界及过大
    function checkScreen() {
        if(mainWin.width > mScreen.desktopAvailableWidth)
            mainWin.width = mScreen.desktopAvailableWidth
        if(mainWin.height > mScreen.desktopAvailableHeight)
            mainWin.height = mScreen.desktopAvailableHeight
        if(mx < mScreen.virtualX) {
            mainWin.x = mScreen.virtualX
        }
        else if(mx > mScreen.virtualX+mScreen.desktopAvailableWidth-mainWin.width) {
            mainWin.x = mScreen.virtualX+mScreen.desktopAvailableWidth-mainWin.width
        }
        if(my < mScreen.virtualY+30) {
            mainWin.y = mScreen.virtualY+30
        }
        else if(my > mScreen.virtualY+mScreen.desktopAvailableHeight-mainWin.height) {
            mainWin.y = mScreen.virtualY+mScreen.desktopAvailableHeight-mainWin.height
        }
    }
}