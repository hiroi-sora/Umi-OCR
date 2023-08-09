// ===========================================
// =============== 主窗口管理器 ===============
// ===========================================

import QtQuick 2.15
import QtQuick.Window 2.15

Item {
    property var mainWin // 主窗口的引用
    property bool isTopping: false
    
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
        return mainWin.visible
        // return mainWin.visibility==2||mainWin.visibility==4||mainWin.visibility==5
    }

    // 设置主窗口可见性。 false 隐藏， true 恢复。
    function setVisible(flag) {
        if(flag) {
            mainWin.visibility = Window.Windowed // 状态为可见
            mainWin.raise() // 弹到最前层
            mainWin.requestActivate() // 激活窗口
        }
        else {
            mainWin.visibility = Window.Hidden
        }
    }

    // 设置置顶状态。 toConfig 为 true 表示需要同步到设置
    function setTopping(flag, toConfig) {
        isTopping = flag
        // 窗口 | 自定义标题栏 | 有标题 | 有系统菜单 | 有最小最大化按钮 | 有关闭按钮 | 根据条件是否置顶
        mainWin.flags = Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint 
            | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint | (flag?Qt.WindowStaysOnTopHint:0)
        if(toConfig) {
            qmlapp.globalConfigs.setValue("ui.topping", flag, true)
        }
    }

    // 点击主窗口关闭
    function winClose() {

    }
}