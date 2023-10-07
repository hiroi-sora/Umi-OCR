import QtQuick 2.0
import QtGraphicalEffects 1.15 // 改颜色


Item {
    // ========================= 【设定值】 =========================

    property string icon: ""
    property color color: theme.subTextColor
    property bool mirror: false // 水平翻转

    // =============================================================
    id: iconRoot
    Image {
        id: image
        anchors.fill: parent
        source: icon ? `../../images/icons/${icon}.svg` : ""
        fillMode: Image.PreserveAspectFit // 均匀缩放
        visible: false // 关闭原图显示，只显示填充颜色
        mirror: iconRoot.mirror
    }
    // 填充颜色
    ColorOverlay{
        id: overlay
        anchors.fill: parent
        source: image
        color: parent.color
        cached: true
    }
}