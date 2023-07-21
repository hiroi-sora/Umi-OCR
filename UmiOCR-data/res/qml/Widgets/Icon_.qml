import QtQuick 2.0
import QtGraphicalEffects 1.15 // 改颜色

Image {

    // ========================= 【设定值】 =========================

    property string icon: ""
    property color color: theme.subTextColor


    // =============================================================
    id: image
    source: icon ? `../../images/icons/${icon}.svg` : ""
    fillMode: Image.PreserveAspectFit // 均匀缩放

    // 填充颜色
    ColorOverlay{
        id: overlay
        anchors.fill: parent
        source: parent
        color: parent.color
        cached: true
    }
}