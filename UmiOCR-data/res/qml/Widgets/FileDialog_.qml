// =========================================
// =============== 文件选择窗 ===============
// =========================================

import QtQuick.Dialogs 1.3
import "../js/utils.js" as Utils

FileDialog {
    property var fileUrls_: [] // 缓存处理好的 fileUrls

    onAccepted: {
        fileUrls_ = Utils.QUrl2String(fileUrls)
    }
}