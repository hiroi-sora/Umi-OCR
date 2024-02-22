// =========================================
// =============== 图片管理器 ===============
// =========================================

import QtQuick 2.15
import ImageConnector 1.0 // 图片连接器

Item {
    // ========================= 【接口】 =========================

    // 截图，向回调函数传入裁切后的 clipImgID
    readonly property var screenshot: screenshotManager.screenshot
    // 重复截图
    readonly property var reScreenshot: screenshotManager.reScreenshot
    // 复制图片
    readonly property var copyImage: imageConnector.copyImage
    // 用系统默认应用打开图片
    readonly property var openImage: imageConnector.openImage
    // 保存图片
    readonly property var saveImage: imageConnector.saveImage
    // 获取剪贴板
    readonly property var getPaste: imageConnector.getPaste

    // ===========================================================

    // 图片连接器
    property QtObject imageConnector: ImageConnector {}
    // 截图管理器
    property QtObject screenshotManager: ScreenshotManager {}
}