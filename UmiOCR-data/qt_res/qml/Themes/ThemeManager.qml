// ================================================
// =============== 主题切换的逻辑管理 ===============
// ================================================

import QtQuick 2.15
import ThemeConnector 1.0

Item {
    // ==================== 【接口】 ====================

    // 初始化
    function init() {
        loadAll() // 加载主题
        console.log("% 主题管理器初始化完毕！", this)
    }

    // 从配置文件中加载 theme.all
    function loadAll() {
        const tstr = tConn.loadThemeStr() // 文件读字符串
        let f = strToAll(tstr) // 字符串写入all
        if(!f) { // 写入失败，则初始化配置文件
            console.log("% 初始化主题配置文件")
            saveAll()
        }
    }

    // 将 theme.all写入配置文件
    function saveAll() {
        const tstr = allToStr()
        tConn.saveThemeStr(tstr)
    }

    // 切换主题
    function switchTheme(th) {
        if(!theme.all.hasOwnProperty(th)) {
            console.log("[Warning] 切换主题失败，theme.all 不存在主题", k)
            return
        }
        const target = theme.all[th]
        for(const k of theme.keys) {
            theme[k] = target[k]
        }
    }

    // 获取主题列表
    function getOptionsList() {
        let optList = []
        for(let k in theme.all) {
            optList.push([k, theme.all[k].themeTitle])
        }
        return optList
    }

    // =========================================================

    // 连接器
    ThemeConnector{id: tConn}

    // 从json字符串加载主题配置，写入 theme.all 。返回是否成功
    function strToAll(tstr) {
        if(!tstr)
            return false
        try {
            // 加载并检查主题字典
            let all = JSON.parse(tstr)
            for(let k in all) {
                if(!checkThemeDict(all[k])) {
                    console.log("[Warning] 加载单个主题失败：", k)
                    delete all[k]
                    continue
                }
                // 覆盖加载名称
                if(theme.all.hasOwnProperty(k)) {
                    all[k].themeTitle = theme.all[k].themeTitle
                }
            }
            if(Object.keys(all).length === 0) {
                return false
            }
            theme.all = all
            return true
        } catch (error) {
            console.log("[Warning] 解析主题JSON字符串时出现异常:", error)
        }
        return false
    }

    // 将 theme.all 转为json字符串
    function allToStr() {
        return JSON.stringify(theme.all, null, "    ")
    }

    // 检测单个主题字典的合法性
    function checkThemeDict(td) {
        const tdKeys = Object.keys(td);
        if (tdKeys.length !== theme.keys.length) {
            return false // 长度不符
        }
        for (let k of theme.keys) {
            if (!tdKeys.includes(k))
                return false // 缺键
        }
        return true
    }

}