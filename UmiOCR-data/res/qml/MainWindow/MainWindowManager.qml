// ===========================================
// =============== 主窗口管理器 ===============
// ===========================================

import QtQuick 2.15
import QtQuick.Window 2.15

Item {
    property var mainWin // 主窗口的引用
    
    // ========================= 【保存量】 =========================
    
    // 主窗口属性初始化
    Component.onCompleted: {
        // 启动时可见
        const visi = !qmlapp.globalConfigs.getValue("ui.startupInvisible")
        setVisible(visi)
        if(!visi) {
            qmlapp.popup.simple(qsTr("欢迎使用 Umi-OCR"), qsTr("已启用后台模式，可通过快捷键使用功能。"))
        }
    }

    // ========================= 【接口】 =========================

    // 返回主窗口是否可见
    function getVisible() {
        return mainWin.visibility==2||mainWin.visibility==4||mainWin.visibility==5
    }

    // 设置主窗口可见性。 false 隐藏， true 恢复。
    function setVisible(flag) {
        if(flag) {
            mainWin.visibility = Window.Windowed // 状态为可见
            mainWin.requestActivate() // 激活窗口
            mainWin.raise() // 弹到顶层
        }
        else {
            mainWin.visibility = Window.Hidden
        }
    }

    // 设置置顶状态。 toConfig 为 true 表示需要同步到设置
    function setTopping(flag, toConfig=false) {
        mainWin.isMainWindowTop = flag
        if(toConfig) {
            qmlapp.globalConfigs.setValue("ui.topping", flag, true)
        }
    }
    // 获取置顶状态
    function getTopping() {
        return mainWin.isMainWindowTop
    }

    // 关闭主窗口
    function close() {
        // 隐藏
        if(qmlapp.globalConfigs.getValue("ui.closeWin2Hide")) {
            setVisible(false)
        }
        // 关闭
        else {
            Qt.quit()
        }
    }
}