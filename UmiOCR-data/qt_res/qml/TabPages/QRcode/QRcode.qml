// ==============================================
// =============== 功能页：二维码 ===============
// ==============================================

import QtQuick 2.15

import ".."
import "../../Widgets"
import "../../Widgets/ResultLayout"
import "../../Widgets/ImageViewer"

TabPage {
    id: tabPage
    // 配置
    configsComp: QRcodeConfigs {} 
}