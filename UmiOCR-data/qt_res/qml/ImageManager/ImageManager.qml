// =========================================
// =============== 图片管理器 ===============
// =========================================

import QtQuick 2.15
import ImageConnector 1.0 // 图片连接器

Item {
    // ========================= 【接口】 =========================

    // 截图，向回调函数传入裁切后的 clipImgID
    property var screenshot: screenshotManager.screenshot
    // 复制图片
    property var copyImage: imageConnector.copyImage

    // ===========================================================

    // 图片连接器
    property QtObject imageConnector: ImageConnector {}
    // 截图管理器
    property QtObject screenshotManager: ScreenshotManager {}
}