// =============================================
// =============== 截图窗口管理器 ===============
// =============================================

import QtQuick 2.15
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
            const g = grabList[i]
            console.log("得到id：", g.imgID)
            const argd = {
                imgID: g.imgID,
                x: g.geometry.x,
                y: g.geometry.y,
                width: g.geometry.width,
                height: g.geometry.height,
            }
            console.log(`屏幕： ${argd.x} ${argd.y} ${argd.width} ${argd.height}`)
            const obj = ssWinComp.createObject(this, argd)
            winDict[g.imgID] = obj
        }
    }

    // 关闭一个覆盖窗口，传入图片ID
    function close(imgID) {
        if(winDict.hasOwnProperty(imgID)) {
            winDict[imgID].destroy()
        }
    }


    Component {
        id: ssWinComp

        Window {
            id: win

            property string imgID: "" // 图片id

            visible: true
            flags: Qt.FramelessWindowHint // 无边框
            // visibility: Window.FullScreen

            Image {
                anchors.fill: parent
                source: "image://pixmapprovider/"+imgID
            }
            Rectangle {
                anchors.fill: parent
                color: "#22000000"
                border.width: 50
                border.color: "red"
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    ssWinRoot.close(win.imgID)
                }
            }
        }
    }
}