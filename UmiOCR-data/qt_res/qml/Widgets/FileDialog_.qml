// =========================================
// =============== 文件选择窗 ===============
// =========================================

import QtQuick.Dialogs 1.3

FileDialog {
    property var fileUrls_: [] // 缓存处理好的 fileUrls

    onAccepted: {
        fileUrls_ = qmlapp.utilsConnector.QUrl2String(fileUrls)
    }
}