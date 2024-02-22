// =========================================
// =============== 截图管理器 ===============
// =========================================

import QtQuick 2.15
import QtQuick.Window 2.15

Item {
    id: ssWinRoot

    // ==================== 【接口】 ====================

    // 开始一次截图。传入回调函数。
    function screenshot(callback) {
        // 获取所有屏幕的截图图像
        const grabList = getGrabList()
        if(!grabList) return
        // 记录回调
        lastCallback = callback 
        if(winDict === undefined) winDict = {}
        // 遍历截图列表，生成数量一致的覆盖窗口
        for(let i in grabList) {
            const g = grabList[i]  // 截图属性
            const screen = Qt.application.screens[i]  // 获取对应编号的屏幕
            if(screen.name !== g.screenName) {
                qmlapp.popup.message(errorTitle, 
                    qsTr("屏幕设备名称不相同：\n%1\n%2").arg(screen.name).arg(g.screenName), "error")
                running = false
                return
            }
            const argd = {
                imgID: g.imgID,
                screenName: screen.name,
                screen: screen, // 为Window设定所属屏幕属性
                screenRatio: screen.devicePixelRatio, // 屏幕缩放比
                x: screen.virtualX,
                y: screen.virtualY,
                width: screen.width,
                height: screen.height,
                screenshotEnd: ssWinRoot.ssEnd // 关闭函数
            }
            const obj = ssWinComp.createObject(this, argd)
            winDict[g.imgID] = obj
        }
        // 注册esc事件监听
        qmlapp.pubSub.subscribeGroup("<<esc>>", ssWinRoot, "ssEsc", "ssEsc")
    }

    // 重复上一次截图区域
    function reScreenshot(callback) {
        // 获取所有屏幕的截图图像
        const grabList = getGrabList()
        if(!grabList) return
        if(!lastClipArgd) {
            qmlapp.popup.simple(qsTr("尚未记录截图区域"), "")
            running = false
            return
        }
        // 在截图列表中，寻找上一次截图所在的屏幕
        for(let i in grabList) {
            const g = grabList[i]  // 截图属性
            if(lastClipArgd.screenName === g.screenName) {
                // 向py汇报，获取裁剪后的imgID
                const clipImgID = imageConn.getClipImgID(g.imgID,
                    lastClipArgd.clipX, lastClipArgd.clipY, lastClipArgd.clipW, lastClipArgd.clipH)
                // 成功 调用回调
                runLastCallback(clipImgID)
                running = false
                return
            }
        }
        // 失败，未找到相同屏幕
        lastClipArgd = undefined
        running = false
        qmlapp.popup.simple(qsTr("重复截图失败"), qsTr("未找到匹配的屏幕"))
        runLastCallback()
    }

    // =================================================

    // 获取所有屏幕的截图图像
    function getGrabList() {
        // 重复调用验证
        if(running) {
            qmlapp.popup.message(errorTitle,
                qsTr("上次截图操作未结束，不能进行新的截图！"), "error")
            return undefined
        }
        running = true
        // 截图前等待时间
        let wait = 0
        if(qmlapp.globalConfigs.getValue("screenshot.hideWindow")) {
            qmlapp.mainWin.setVisibility(false)
            wait = qmlapp.globalConfigs.getValue("screenshot.hideWindowTime")
        }
        // 获取所有屏幕的截图并验证
        const grabList = imageConn.getScreenshot(wait)
        if(!grabList || grabList.length<1 || !grabList[0]) {
            qmlapp.popup.message(errorTitle,
                qsTr("未知异常！"), "error")
            running = false
            return undefined
        }
        if(typeof grabList[0] === "string") {
            qmlapp.popup.message(errorTitle, grabList[0], "error")
            running = false
            return undefined
        }
        return grabList
    }

    // Esc退出截图
    function ssEsc() {
        const argd = {clipX: -1, clipY: -1, clipW: -1, clipH: -1}
        ssEnd(argd)
    }

    // 截图窗口操作完毕的回调
    function ssEnd(argd) {
        // 注销esc事件监听
        qmlapp.pubSub.unsubscribeGroup("ssEsc")
        // 关闭所有覆盖窗口
        for (let key in winDict) {
            winDict[key].destroy()
        }
        winDict = {}
        running = false
        // 检测是否有效
        if(argd.clipX<0 || argd.clipY<0 || argd.clipW<1 || argd.clipH<1 || !argd.imgID) {
            runLastCallback()
            lastClipArgd = undefined
            return
        }
        // 记录当前截图信息
        lastClipArgd = argd
        // 向py汇报，获取裁剪后的imgID
        const clipImgID = imageConn.getClipImgID(argd.imgID, argd.clipX, argd.clipY, argd.clipW, argd.clipH)
        // 调用回调
        runLastCallback(clipImgID)
    }

    // 调用上级回调
    function runLastCallback(clipImgID) {
        if (lastCallback && typeof lastCallback === "function") {
            lastCallback(clipImgID)
        }
    }

    property string errorTitle: qsTr("截图失败")
    property bool running: false // 当前是否正在截图
    property var lastClipArgd: undefined // 最后一次截图的信息
    property var lastCallback: undefined // 截图完毕的回调，得到 clipImgID
    property var winDict: {} // 存放当前已打开的窗口
    property QtObject imageConn: qmlapp.imageManager.imageConnector

    Component {
        id: ssWinComp
        ScreenshotWindowComp { }
    }
}