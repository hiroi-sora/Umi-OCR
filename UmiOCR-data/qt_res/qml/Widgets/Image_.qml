// ==============================================
// =============== 增强的Image组件 ===============
// ==============================================

import QtQuick 2.15

Image {

    // 组件ID
    readonly property string compID: this.toString()

    // 传入路径，展示图片
    function showPath(path) {
        path = encodeURIComponent(path) // URL编码
        source = `file:///${path}`
    }

    // 传入imgID，展示图片
    function showImgID(imgID) {
        source = `image://pixmapprovider/${compID}/${imgID}`
    }

    // 清空展示，并释放缓存
    function clear() {
        source = `image://pixmapprovider/${compID}`
    }

    Component.onDestruction: {
        clear()
    }
}