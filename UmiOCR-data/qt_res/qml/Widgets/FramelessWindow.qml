// ==================================================
// =============== 无边框窗口，支持拖拽 ===============
// ==================================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15

Window {
    id: win
    flags: Qt.FramelessWindowHint // 无边框

    // 鼠标拖拽移动窗口
    MouseArea {
        anchors.fill: parent
        property int ox: 0
        property int oy: 0
        onPressed: {
            ox = mouse.x
            oy = mouse.y
        }
        onPositionChanged: {
            win.setX(win.x+mouse.x-ox)
            win.setY(win.y+mouse.y-oy)
        }
    }
}