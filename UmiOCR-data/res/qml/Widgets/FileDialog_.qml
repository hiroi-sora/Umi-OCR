// =========================================
// =============== 文件选择窗 ===============
// =========================================

import QtQuick.Dialogs 1.3

FileDialog {
    property var fileUrls_: [] // 缓存处理好的 fileUrls

    onAccepted: {
        fileUrls_ = []
        for(let i in fileUrls){
            let s = fileUrls[i]
            if(s.startsWith("file:///"))
                fileUrls_.push(s.substring(8))
        }
        console.log(`关闭对话框，路径为${fileUrls_}`)
    }
}