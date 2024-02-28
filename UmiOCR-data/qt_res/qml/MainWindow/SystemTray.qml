// =======================================
// =============== 系统托盘 ===============
// =======================================

import QtQuick 2.15
import QtQml.Models 2.15
import Qt.labs.platform 1.1

SystemTrayIcon {

    // ========================= 【接口】 =========================

    // 添加一项菜单。如果只传入 eventTitle ，则发送事件。如果传入回调函数 func ，则调用函数，不发送事件。
    function addMenuItem(eventTitle, text, func=undefined) {
        // 检查重复
        const index = findMenuEvent(eventTitle)
        if(index >= 0) {
            console.log(`[Warning] 注册系统托盘菜单重复！ ${eventTitle} - ${text}`)
            return
        }
        const argv = {eventTitle: eventTitle, text_:text, isFunc:func?true:false}
        if(func) funcDict[eventTitle] = func // 不能将函数塞进ListModel，故放进单独的函数字典
        menuModel.append(argv)

    }

    // 移除一项菜单
    function delMenuItem(eventTitle) {
        console.log(`删除系统托盘菜单 ${eventTitle}`)
        const index = findMenuEvent(eventTitle)
        if(index < 0) {
            console.log(`[Warning] 删除系统托盘菜单，找不到对应项！ ${eventTitle} - ${text}`)
            return
        }
        const argd = menuModel.get(index)
        if(argd.isFunc) { // 删除回调函数
            delete funcDict[argd.eventTitle]
        }
        // 删除菜单项
        menuModel.remove(index)

    }

    // ========================= 【控制】 =========================

    // 在 menuModel 中寻找 eventTitle 对应的项，返回下标，找不到返回-1
    function findMenuEvent(eventTitle) {
        const len = menuModel.count
        let index = len-1
        for(; index >= 0; index--) {
            const d = menuModel.get(index)
            if(d.eventTitle === eventTitle)
                break
        }
        return index
    }

    // 点击菜单项
    function menuCall(index) {
        const argd = menuModel.get(index)
        if(argd.isFunc) { // 执行函数
            funcDict[argd.eventTitle]()
        }
        else { // 发布事件
            qmlapp.pubSub.publish(argd.eventTitle)
        }
    }

    // ========================= 【布局】 =========================

    id: systemTrayRoot
    visible: false
    icon.source: "../../images/icons/umiocr.ico"
    tooltip: "Umi-OCR"
    property var funcDict: {} // 存放函数的字典
    Component.onCompleted: funcDict = {}
    
    onVisibleChanged: {
        // 隐藏/显示托盘图标时，重新挂载菜单
        systemTrayRoot.menu = visible ? trayMenu : null
    }

    // 右键菜单
    menu: Menu {
        id: trayMenu
        ListModel{ id:menuModel } // 自定义菜单的模型
        property alias menuModel: menuModel

        // Menu { title: qsTr("所有功能") }

        Instantiator {
            model: trayMenu.menuModel
            delegate: MenuItem {
                text: text_
                onTriggered: systemTrayRoot.menuCall(index)
            }

            onObjectAdded: trayMenu.insertItem(index, object)
            onObjectRemoved: trayMenu.removeItem(object)
        }

        MenuItem {
            text: qsTr("退出 Umi-OCR")
            onTriggered: qmlapp.mainWin.quit()
        }
    }

    onActivated: {
        if(reason == SystemTrayIcon.DoubleClick)
            qmlapp.mainWin.setVisibility(true) // 主窗可见
    }
}