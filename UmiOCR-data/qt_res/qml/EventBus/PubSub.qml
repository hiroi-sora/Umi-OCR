// ====================================================
// =============== 全局事件 发布/订阅机制 ===============
// ====================================================

import PubSubConnector 1.0

PubSubConnector{

    // 订阅事件。传入 标题，函数所在Item，函数名
    // subscribe(title, item, funcName)

    // 订阅事件，可额外传入组
    // subscribeGroup(title, item, funcName, groupName)

    // 取消订阅事件
    // unsubscribe(title, item, funcName)

    // 取消订阅整组事件
    // unsubscribeGroup(groupName)

    // 发布事件，传入任意参数
    function publish(title, ...args) {
        console.log("qml 发布事件", title, args)
        publish_(title, args)
    }
}