// ======================================
// =============== 工具类 ===============
// ======================================

function QUrl2String(fileUrls) { // QUrl列表 转 String列表
    var fileUrls_ = []
    for (let i in fileUrls) {
        let s = fileUrls[i]
        if (s.startsWith("file:///"))
            fileUrls_.push(s.substring(8))
    }
    return fileUrls_
}