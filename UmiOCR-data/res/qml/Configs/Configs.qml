// ============================================
// =============== 参数配置 逻辑 ===============
// ============================================

import QtQuick 2.15


Item {
    property string key: "" // 键
    property var dict: {} // 配置字典

    Settings_ {
        id:sets
        category: key // 自定义类别名称
    }
    
    Component.onCompleted: {
        
        console.log("配置初始化")

        function initItem(config, groups=[]) {
            if(config instanceof ConfigItem) { // 配置项
                if(!config.key) {
                    console.error(`【Error】配置项${groups} - key为空`)
                    return
                }
                // TODO: 赋初始值
                let s = ""
                for(let i in groups) {
                    s += groups[i] + "."
                }
                s += config.key
                console.log("配置：", s)
                sets.setValue(s, config.defaultValue)
            }
            if(config instanceof ConfigGroup) { // 配置项组
                if(!config.key) {
                    console.error(`【Error】配置项组${groups} - key为空`)
                    return
                }
                let g = [...groups]
                g.push(config.key)
                for(let i in config.children) {
                    initItem(config.children[i], g)
                }
            }
        }

        for(let i in this.children) {
            initItem(this.children[i])
        }
    }
    
}