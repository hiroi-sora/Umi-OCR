// =============================================
// =============== 截图窗口管理器 ===============
// =============================================

import QtQuick 2.15
// import QtQml 2.15
import QtQuick.Window 2.15

Item {
    id: ssWinRoot
    property var screenshotEnd // 截图完毕的回调
    property var winDict: {} // 存放当前已打开的窗口

    // 传入py获取的截图列表，生成覆盖窗口
    function create(grabList) {
        // 初始化字典
        if(winDict===undefined) winDict={}
        // 如果当前字典非空，则上次截图还未结束，不允许新截图
        if(Object.keys(winDict).length > 0) {
            console.log("【Error】上次截图还未结束！")
            return
        }
        // 遍历截图列表，生成数量一致的覆盖窗口
        for(let i in grabList) {
            // if(i==0) continue
            const g = grabList[i]  // 截图属性
            const screen = Qt.application.screens[i]  // 获取对应编号的
            if(screen.name !== g.screenName) {
                qmlapp.popup.message(qsTr("截图窗口展开异常"), 
                qsTr("屏幕设备名称不相同：\n%1\n%2").arg(screen.name).arg(g.screenName), "error")
                return
            }
            const argd = {
                imgID: g.imgID,
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
    }

    // 截图完毕的回调
    function ssEnd(argd) {
        // 关闭所有覆盖窗口
        for (let key in winDict) {
            winDict[key].destroy()
        }
        winDict = {}
        // 向父级回报
        ssWinRoot.screenshotEnd(argd)
    }

    Component {
        id: ssWinComp
        ScreenshotWindowComp { }
    }
}