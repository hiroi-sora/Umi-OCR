// =============================================
// =============== 截图窗口管理器 ===============
// =============================================

import QtQuick 2.15
// import QtQml 2.15
import QtQuick.Window 2.15

Item {
    id: ssWinRoot
    property var winDict: {}

    // 传入py获取的截图列表，生成覆盖窗口
    function create(grabList) {
        // 初始化字典
        if(winDict===undefined) winDict={}
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
                screen: screen,
                x: screen.virtualX,
                y: screen.virtualY,
                width: screen.width,
                height: screen.height,
            }
            const obj = ssWinComp.createObject(this, argd)
            winDict[g.imgID] = obj
        }
    }

    // 关闭所有覆盖窗口
    function close() {
        for (let key in winDict) {
            winDict[key].destroy()
        }
        winDict = {}
    }


    Component {
        id: ssWinComp

        ScreenshotWindowComp {
            onClosed: ssWinRoot.close // 关闭函数
        }
    }
}