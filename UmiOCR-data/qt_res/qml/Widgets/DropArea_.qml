// =============================================
// =============== 拖入图片的区域 ===============
// =============================================

import QtQuick 2.15

// 鼠标拖入图片
DropArea {
    property var callback: undefined
    property bool enable: true // 是否启用
    property string tips: qsTr("松手放入文件")
    onEntered: {
        if(!enable) return
        qmlapp.popup.showMask(tips, "DropImage")
    }
    onExited: {
        if(!enable) return
        qmlapp.popup.hideMask("DropImage")
    }
    onDropped: {
        if(!enable) return
        qmlapp.popup.hideMask("DropImage")
        if(drop.hasUrls){
            var urls = qmlapp.utilsConnector.QUrl2String(drop.urls)
            if(urls.length > 0 && callback)
                callback(urls)
        }
    }
}