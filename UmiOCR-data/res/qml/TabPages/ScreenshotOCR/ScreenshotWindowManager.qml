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

    // 关闭一个覆盖窗口，传入图片ID
    function close(imgID) {
        for (let key in winDict) {
            winDict[key].destroy()
        }
    }


    Component {
        id: ssWinComp

        Window {
            id: win

            property string imgID: "" // 图片id

            visible: true
            flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint // 无边框+置顶

            // 底层，图片
            Image {
                anchors.fill: parent
                source: "image://pixmapprovider/"+imgID
            }
            // 叠加层，暗
            Rectangle {
                anchors.fill: parent
                color: "#22000000"
                border.width: 50
                border.color: "red"
            }
            // 鼠标触控层
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    ssWinRoot.close(win.imgID)
                }
            }
        }
    }
}