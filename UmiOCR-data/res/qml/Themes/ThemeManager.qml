// ================================================
// =============== 主题切换的逻辑管理 ===============
// ================================================

import QtQuick 2.15

Item {
    // 容纳主题组件
    Item { 

        // =============== 所有主题列在下面 ===============
        ThemeLight{}
        ThemeDark{}
        // ===============================================

        id: themeComps
        Component.onCompleted: init() // 初始化
    }

    // ========================= 【对外接口】 =========================

    // 切换主题
    function switchTheme(key){
        if(themeDict.hasOwnProperty(key)) {
            theme = themeDict[key]
        }
    }
    // 切换动画特效 开true / 关false
    function switchEnabledEffect(flag){
        for(let k in themeDict)
            themeDict[k].enabledEffect = flag
    }

    // ========================= 【内部】 =========================

    // 主题字典和列表，自动加载
    property var themeDict: {}
    property var themeList: []
    // 初始化两表
    function init() {
        themeDict = {}
        themeList = []
        // 遍历所有主题子组件
        let tc = themeComps.children
        for (let i = 0; i < tc.length; i++) {
            let cname = tc[i].toString() // 取组件名称
            cname = cname.substring(0, cname.indexOf("_")) // 取第一个下划线之前的内容
            themeDict[cname] = tc[i]
            themeList.push([cname, tc[i].themeTitle])
        }
    }
}