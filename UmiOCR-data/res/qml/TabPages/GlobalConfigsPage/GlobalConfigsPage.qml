// ==============================================
// =============== 功能页：全局设置 ===============
// ==============================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import ".."
import "../../Widgets"

TabPage {
    id: tabPage
    Panel {
        anchors.fill: parent
        anchors.margins: theme.spacing
        
        Item {
            anchors.fill: parent
            anchors.margins: theme.spacing
            Component.onCompleted: { // 将全局设置UI的父级重定向过来
                // 就算本页面删除，全局UI也不会被删，只会丢失父级
                qmlapp.globalConfigs.panelComponent.parent = this
            }
        }
    }
}