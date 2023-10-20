// ===========================================
// =============== 快速截图组件 ===============
// ===========================================

import QtQuick 2.15

Item {
    id: tabPage

    // 开始截图
    function screenshot() {
        let wait = 0
        // if(screenshotOcrConfigs.getValue("action.hideWindow")){
        //     if(qmlapp.mainWin.getVisibility()){
        //         qmlapp.mainWin.setVisibility(false) // 隐藏主窗
        //         wait = screenshotOcrConfigs.getValue("action.hideWindowTime")
        //     }
        // }
        const grabList = tabPage.callPy("screenshot", wait)
        ssWindowManager.create(grabList)
    }
}