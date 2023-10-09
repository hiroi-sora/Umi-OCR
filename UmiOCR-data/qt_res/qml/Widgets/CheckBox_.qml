// ========================================================
// =============== 复选框样式，不提供点击事件 ===============
// ========================================================

import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    property bool checked: false // 选中/非选中
    property bool enabledAnime: false // true 启用动画

    height: size_.line
    width: size_.line*2
    clip: true
    color: theme.bgColor
    radius: size_.btnRadius
    border.width: 2
    border.color: theme.coverColor4

    // 关闭：-
    Icon_ {
        anchors.fill: parent
        anchors.margins: 3
        icon: "dash"
        color: theme.noColor
    }

    // 启用：√
    Rectangle {
        id: enableIcon
        x: checked ? 0 : width*-1.1
        height: parent.height
        width: parent.width
        color: theme.yesColor
        radius: size_.btnRadius
        Icon_ {
            anchors.fill: parent
            icon: "yes"
            color: theme.bgColor
        }
        Behavior on x { // 位移动画
            enabled: qmlapp.enabledEffect && enabledAnime
            NumberAnimation {
                duration: 200
                easing.type: Easing.OutCirc
            }
        }
    }
}