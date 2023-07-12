// ===========================================
// =============== 标签页的基类 ===============
// ===========================================

import QtQuick 2.15

Item {
    anchors.fill: parent

    property string ctrlKey // Python控制器的key
    property var controller // Python控制器的引用
    property var configsComp: undefined // 该页面的配置组件

    // 调用Python控制器的func方法名，传入任意个数的args作为参数
    function callPy(func, ...args) {
        return controller.callPy(ctrlKey, func, args)
    }
    // 获取配置项值字典
    function getConfigValueDict() {
        if (typeof configsComp === "object" && "valueDict" in configsComp) {
            console.log(`尝试：${configsComp.valueDict}`)
            return configsComp.valueDict
        }
        return {}
    }
    
}