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
        // 重复调用验证
        if(running) {
            qmlapp.popup.simple(errorTitle, errorRepeat)
            return
        }
        running = true
        // 获取所有屏幕的截图图像
        const grabList = getGrabList()
        // 遍历截图列表，收集覆盖窗口属性 argds
        let argds = []
        for(let i in grabList) {
            const g = grabList[i]  // 截图属性
            // 合法性检查
            if(g.imgID.startsWith("[")) {
                qmlapp.popup.message(errorTitle,
                    qsTr("显示器： %1\n错误信息： %2").arg(g.screenName).arg(g.imgID), "error")
                callback()
                running = false
                return
            }
            const screen = Qt.application.screens[i]  // 获取对应编号的屏幕
            if(screen.name !== g.screenName) {
                qmlapp.popup.message(errorTitle,
                    qsTr("屏幕设备名称不相同：\n%1\n%2").arg(screen.name).arg(g.screenName), "error")
                callback()
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
            argds.push(argd)
        }
        // 记录回调
        lastCallback = callback
        if(winDict === undefined) winDict = {}
        // 生成覆盖窗口
        for(let a in argds) {
            const obj = ssWinComp.createObject(this, argds[a])
            winDict[argds[a].imgID] = obj
        }
        // 注册esc事件监听
        qmlapp.pubSub.subscribeGroup("<<esc>>", ssWinRoot, "ssEsc", "ssEsc")
    }

    // 重复上一次截图区域
    function reScreenshot(callback) {
        // 重复调用验证
        if(running) {
            qmlapp.popup.simple(errorTitle, errorRepeat)
            return
        }
        running = true
        if(!lastClipArgd) {
            qmlapp.popup.simple(qsTr("尚未记录截图区域"), "")
            callback()
            running = false
            return
        }
        // 获取所有屏幕的截图图像
        const grabList = getGrabList()
        let errorMsg = "" // 缓存报错信息
        // 在截图列表中，寻找上一次截图所在的屏幕
        for(let i in grabList) {
            const g = grabList[i]  // 截图属性
            // 合法性检查
            if(g.imgID.startsWith("[")) {
                errorMsg = g.imgID // 记录失败，跳过本轮
                continue
            }
            // 找到对应屏幕
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
        if(!errorMsg) errorMsg = qsTr("未找到匹配的屏幕")
        qmlapp.popup.simple(qsTr("重复截图失败"), errorMsg)
        runLastCallback()
        running = false
    }

    // 【同步】获取指定区域的截图ID，失败返回 "[Error]..."
    function getScreenshot(rect, screen=0) { // screen 屏幕编号
        // 无需验证 running
        // 获取所有屏幕的截图图像
        const grabList = getGrabList()
        // 参数检查
        if(!Number.isInteger(screen) || screen < 0 || screen >= grabList.length)
            return `[Error] Invalid screen=${screen}: must be an integer (0~${grabList.length-1})`
        if(rect.length != 4) // 不检查内部是否合法，getClipImgID会检查
            return `[Error] Invalid rect=${rect}: must be integers [x,y,w,h]`
        const grab = grabList[screen]
        const imgID = grab.imgID
        if(imgID.startsWith("[")) // 获取截图数据失败
            return imgID
        let [x, y, w, h] = rect
        // 补充缺省宽高
        if(w <= 0) w = grab.width - x
        if(h <= 0) h = grab.height - y
        // 返回裁剪后的imgID
        return imageConn.getClipImgID(imgID, x, y, w, h)
    }

    // =================================================

    // 获取所有屏幕的截图图像
    function getGrabList() {
        /*
        返回列表(不为空)，每项为：\n
        {
            "imgID": 图片ID 或 报错信息 "[Error]开头" ,
            "screenName": 显示器名称 ,
            "width": 截图宽度 ,
            "height": 截图高度 ,
        }
        */

        // 截图前等待时间
        let wait = 0
        if(qmlapp.globalConfigs.getValue("screenshot.hideWindow")) {
            qmlapp.mainWin.setVisibility(false)
            wait = qmlapp.globalConfigs.getValue("screenshot.hideWindowTime")
        }
        // 获取所有屏幕的截图
        const grabList = imageConn.getScreenshot(wait)
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
        // 检测是否有效。如果无效，可能是按Esc退出了截图流程
        if(argd.clipX<0 || argd.clipY<0 || argd.clipW<1 || argd.clipH<1 || !argd.imgID) {
            runLastCallback()
            lastClipArgd = undefined
            running = false
            return
        }
        // 记录当前截图信息
        lastClipArgd = argd
        // 向py汇报，获取裁剪后的imgID
        const clipImgID = imageConn.getClipImgID(argd.imgID, argd.clipX, argd.clipY, argd.clipW, argd.clipH)
        // 调用回调
        runLastCallback(clipImgID)
        running = false
    }

    // 调用上级回调
    function runLastCallback(clipImgID) {
        if (lastCallback && typeof lastCallback === "function") {
            lastCallback(clipImgID)
        }
    }

    property string errorTitle: qsTr("截图失败")
    property string errorRepeat: qsTr("上次截图操作未结束，不能进行新的截图！")
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