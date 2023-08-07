// ===========================================
// =============== 标签页的基类 ===============
// ===========================================

import QtQuick 2.15

Item {
    anchors.fill: parent

    property string ctrlKey // Python连接器的key
    property var connector // Python连接器的引用
    property var configsComp: undefined // 该页面的配置组件

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
    function getConfigValueDict() {
        // 控制组件存在，且有方法getConfigValueDict
        if (typeof configsComp === "object" && typeof configsComp.getConfigValueDict === "function") {
            return configsComp.getConfigValueDict()
        }
        console.log("【Error】返回空配置项字典")
        return {}
    }
    
}