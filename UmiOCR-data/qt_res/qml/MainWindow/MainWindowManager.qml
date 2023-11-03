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
    property int mw: mainWin.width
    property int mh: mainWin.height
    // 最小宽高
    property int minW: 400
    property int minH: 400

    // ========================= 【保存量】 =========================
    
    // 主窗口属性初始化
    Component.onCompleted: {
        loadGeometry() // 恢复上次大小位置
        // 启动时可见
        const visi = !qmlapp.globalConfigs.getValue("window.startupInvisible")
        setVisibility(visi)
        if(!visi) {
            qmlapp.popup.simple(qsTr("欢迎使用 Umi-OCR"), qsTr("已启用后台模式，可通过快捷键使用功能。"))
        }
    }

    // ========================= 【记录窗口位置大小】 =========================


    Connections {
        target: mainWin
        function onClosing() {
            saveGeometry()
        }
    }
    // 保存
    function saveGeometry() {
        let xywh = checkGeometry(mx, my, mw, mh)
        xywh = xywh.join(",")
        qmlapp.globalConfigs.setValue("window.geometry", xywh, false, true)
        console.log("% 保存窗口位置", xywh)
    }
    // 读取
    function loadGeometry() {
        let xywh = qmlapp.globalConfigs.getValue("window.geometry")
        xywh = xywh.split(",")
        if(xywh.length < 4) {
            console.log("% 未能读取窗口位置", xywh)
            return
        }
        for(let i=0; i<4; i++)
            xywh[i] = parseInt(xywh[i])
        let [x, y, w, h] = checkGeometry(xywh[0], xywh[1], xywh[2], xywh[3])
        mainWin.x = x
        mainWin.y = y
        mainWin.width = w
        mainWin.height = h
        let screenIndex = 0
        for(let i=0, l=Qt.application.screens.length; i<l; i++) {
            let s = Qt.application.screens[i]
            if(x >= s.virtualX && x <= s.virtualX+s.width
                && y >= s.virtualY && y <= s.virtualY+s.height) {
                    screenIndex = i
                    break
                }
        }
        mainWin.screen = Qt.application.screens[screenIndex]
        console.log("% 读取窗口位置", x, y, w, h, screenIndex)
    }
    // 检查窗口位置，返回检查后的值
    function checkGeometry(x, y, w, h) {
        // 检查宽高
        if(w > mScreen.desktopAvailableWidth)
            w = mScreen.desktopAvailableWidth
        else if(w < minW)
            w = minW
        if(h > mScreen.desktopAvailableHeight)
            h = mScreen.desktopAvailableHeight
        else if(h < minH)
            h = minH
        // 检查位置
        if(x < mScreen.virtualX)
            x = mScreen.virtualX
        else if(x > mScreen.virtualX+mScreen.desktopAvailableWidth-w)
            x = mScreen.virtualX+mScreen.desktopAvailableWidth-w
        if(y < mScreen.virtualY+30) // +30防止标题栏出界
            y = mScreen.virtualY+30
        else if(y > mScreen.virtualY+mScreen.desktopAvailableHeight-h)
            y = mScreen.virtualY+mScreen.desktopAvailableHeight-h
        return [x, y, w, h]
    }


    // ========================= 【接口】 =========================

    // 返回主窗口是否可见
    function getVisibility() {
        return mainWin.visibility==2||mainWin.visibility==4||mainWin.visibility==5
    }

    // 设置主窗口可见性。 false 隐藏， true 恢复。
    function setVisibility(flag) {
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
            quit()
        }
    }

    // 退出主窗口
    function quit() {
        saveGeometry()
        Qt.quit()
    }

    // 检查主窗口初始化屏幕位置，防止出界及过大
    function checkScreen() {
        if(mw > mScreen.desktopAvailableWidth)
            mw = mScreen.desktopAvailableWidth
        if(mh > mScreen.desktopAvailableHeight)
            mh = mScreen.desktopAvailableHeight
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