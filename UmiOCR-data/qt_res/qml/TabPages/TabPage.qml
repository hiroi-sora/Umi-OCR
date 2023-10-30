// ===========================================
// =============== 标签页的基类 ===============
// ===========================================

import QtQuick 2.15

Item {
    anchors.fill: parent

    property string ctrlKey // Python连接器的key
    property var connector // Python连接器的引用
    property var configsComp: undefined // 该页面的配置组件
    signal showPage // 页面展示时的信号，用 onShowPage 监听

    // ========================= 【页面控制】 =========================

    // 关闭页面。子类重载后可先向用户弹窗询问，再调用 delPage()
    function closePage() {
        delPage()
    }
    // 销毁页面
    function delPage() {
        const index = qmlapp.tab.getTabPageIndex(this) // 获取当前页下标
        qmlapp.tab.delTabPage(index) // 销毁页面
    }
    // 调用Python连接器的func方法名，传入任意个数的args作为参数
    function callPy(funcName, ...args) {
        return connector.callPy(ctrlKey, funcName, args)
    }
    // 获取配置项值字典
    function getValueDict() {
        // 控制组件存在，且有方法getValueDict
        if (typeof configsComp === "object" && typeof configsComp.getValueDict === "function") {
            return configsComp.getValueDict()
        }
        console.log("[Error] 返回空配置项字典")
        return {}
    }
    // 获取原始值字典
    function getOriginDict() {
        // 控制组件存在，且有方法getValueDict
        if (typeof configsComp === "object" && typeof configsComp.getValueDict === "function") {
            return configsComp.getOriginDict()
        }
        console.log("[Error] 返回空原始值字典")
        return {}
    }
    // 设置配置项值
    function setValue(key, val) {
        // 控制组件存在，且有方法getValueDict
        if (typeof configsComp === "object" && typeof configsComp.setValue === "function") {
            configsComp.setValue(key, val, true)
            return
        }
        console.log("[Error] 设置配置项失败", key, val)
    }
    
}