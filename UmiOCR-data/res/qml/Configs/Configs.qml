// ============================================
// =============== 参数配置 逻辑 ===============
// ============================================

/*
定义规则：

configDict: {

    "配置项组": {
        "title": 显示名称，可选，填写时自动生成控件,
        "group": true,
        "配置项或配置项组": ……
    },

    "常规配置项": {
        "title": 显示名称，可选，填写时自动生成控件,
        "default": 默认值，支持string，number，bool,
    },

}

configDict为嵌套形式，而keyDict与valueDict为展开形式的单层字典。

*/

import QtQuick 2.15

Item {
    property string category_: "" // 配置名
    property var configDict: { } // 定义字典，静态参数

    property var keyDict: { } // 键字典，键为展开形式，值指向configDict的项
    property var valueDict: { } // 值字典，动态变化

    // 初始化数值
    function initConfigDict() {
        function handleConfigItem(config, key) { // 处理一个配置项
            console.log(`配置项[${key}]=${config}`)
            keyDict[key] = config // configDict项的引用绑定到keyDict
            // 从配置文件中取值
            let val = settings.value(key, undefined)
            if(val === undefined) {
                val = config.default // 取默认值
                settings.setValue(key, val) // 存储
            }
            valueDict[key] = val // 设当前值
        }
        function handleConfigGroup(group, prefix="") { // 处理一个配置组
            for(let key in group) {
                const config = group[key]
                if(typeof config !== "object"){
                    continue
                }
                if(!config.hasOwnProperty("title")) { // 补充空白标题
                    config.title = ""
                }
                if(config.hasOwnProperty("group")) { // 若是配置项组，递归遍历
                    handleConfigGroup(config, prefix+key+".") // 前缀加深一层
                }
                else { // 若是配置项
                    config.group = false
                    handleConfigItem(config, prefix+key)
                }
            }
        }
        keyDict = {}
        valueDict = {}
        handleConfigGroup(configDict)
        // console.log(`配置${category_}: `,JSON.stringify(keyDict, null, 4))
        // console.log(`配置${category_}: `,JSON.stringify(valueDict, null, 4))
    }

    // 生成控件
    // function get

    // 存储
    Settings_ {
        id: settings
        category: category_ // 自定义类别名称
    }
    Component.onCompleted: { initConfigDict() }
}