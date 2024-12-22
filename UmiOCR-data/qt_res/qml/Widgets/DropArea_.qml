// =============================================
// =============== 拖入图片的区域 ===============
// =============================================

import QtQuick 2.15

// 鼠标拖入文件
DropArea {
    // 只填 callback ：直接返回所有地址
    // 填 asyn_import ：异步扫描地址合法性，再调用 callback 返回合法地址

    property var callback: undefined // 返回拖入的地址
    property var asyn_scan: undefined // 异步检查函数

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
        if(drop.hasUrls) {
            var urls = qmlapp.utilsConnector.QUrl2String(drop.urls)
            if(urls.length > 0 && callback) {
                if(asyn_scan) { // 异步

                }
                else // 同步
                    callback(urls)
            }
        }
    }

    // 异步回调，适合加载大批文件
}