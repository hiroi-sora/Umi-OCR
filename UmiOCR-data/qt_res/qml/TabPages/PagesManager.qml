// ===============================================
// =============== 页面的逻辑管理器 ===============
// ===============================================


import QtQuick 2.15
import TagPageConnector 1.0 // Python页面连接器

Item {

    // ========================= 【列表】 =========================

    property var infoList: [
        {
            key: "Navigation",         // 页面的唯一标识符。同时也是对应Python模块的名称。
            url: "",                   // 页面的qml文件路径。留空时，初始化为  key/key.qml
            needController: false,      // 为true时才需要加载对应Python模块，不需要可留空
            title: qsTr("新标签页"),    // 页面的显示名称。
            intro: ""                  // 页面的简介。
        },
        {
            key: "ScreenshotOCR",
            needController: true,
            title: qsTr("截图OCR"),
            intro: qsTr("# 截图OCR\n\n　  \n\n屏幕截图，快捷转文字。也支持粘贴图片。")
        },
        {
            key: "BatchOCR",
            needController: true,
            title: qsTr("批量OCR"),
            intro: qsTr("# 批量OCR\n\n　  \n\n导入本地图片或文件夹，批量转换文字。")
        },
        {
            key: "GlobalConfigsPage",
            needController: false,
            title: qsTr("全局设置"),
            intro: qsTr("# 全局设置\n\n　  \n\n调节全局设置项，对所有页面生效。")
        },
    ]

    /* 存放当前已打开的页面
            obj:        页面组件对象
            info:       页面信息（infoList中对应项的引用）
            infoIndex:  页面信息下标（infoList中对应项的引用）
    */
    property var pageList: []

    // Python的页面连接器，手动维护单例状态
    TagPageConnector { id: connector }
    
    // ========================= 【增删改查】 =========================

    // 初始化： 将 infoList 的 url 转换为可实例化的组件类 comp
    function initListUrl() {
        for(let i=infoList.length-1; i>=0; i--){
            const info = infoList[i]
            if(!info.url) {
                info.url = `${info.key}/${info.key}.qml`
            }
            const comp = Qt.createComponent(info.url)
            if (comp.status === Component.Ready) { // 加载成功
                info.comp = comp
            } else{ // 加载失败
                info.comp = undefined
                if (comp.status === Component.Error) {  // 加载失败，提取错误信息
                    let str = comp.errorString()
                    const last = str.lastIndexOf(":")
                    if(last < 0) last = -1
                    str = str.substring(last+1).replace("\n","")
                    console.error(`【Error】加载页面文件失败：【${info.url}】${str}`)
                }
                else{
                    console.error(`【Error】加载页面文件异常：【${info.url}】`)
                }
            }
        }
    }

    // 创建并返回一个 infoList[infoIndex] 页面。
    function newPage(infoIndex){
        const info = infoList[infoIndex]
        // 实例化逻辑控制器
        let ctrlKey = ""
        if(info.needController){
            ctrlKey = connector.addPage(info.key)
            if(!ctrlKey){
                console.error("【Error】添加页面失败：组件["+info.key+"]创建控制器失败！")
                return undefined
            }
        }
        else { // 新增一个不带控制器的简单页
            ctrlKey = connector.addSimplePage(info.key)
        }
        // 检查组件
        const comp = info.comp
        if(!comp){
            console.error("【Error】添加页面失败：组件["+info.key+"]的comp不存在！")
            return undefined
        }
        // 实例化页面，挂到巢下，写入自身参数
        const obj = comp.createObject(pagesNest, {
            z: -1, visible: false,
            ctrlKey: ctrlKey, // Python控制器key
            connector: connector, // Python控制器对象
        })
        // 收集并返回页面对象信息
        const dic = {
            obj: obj,
            info: info,
            infoIndex: infoIndex,
            ctrlKey: ctrlKey
        }
        // 向控制器传入页面对象
        connector.setPageQmlObj(ctrlKey, obj)
        return dic
    }

    // 增： 在 pageList 的 index 处，插入一个 infoList[infoIndex] 页面。
    function addPage(index, infoIndex){ // index=-1 代表尾部插入
        // 列表添加
        const dic = newPage(infoIndex)
        if(dic == undefined){
            return false
        }
        pageList.splice(index, 0, dic) // 列表添加
        return true
    }

    // 增改： 在 pageList 的 index 处，删除该页面，改为 infoIndex 页。
    function changePage(index, infoIndex){
        const page = pageList[index]
        // 删除旧页的python逻辑控制器
        const flag = connector.delPage(page.ctrlKey)
        if(!flag){
            console.error("【Warning】删除页面失败：控制器["+page.ctrlKey+"]删除失败！")
            // return false // 暂时不管控制器删除失败
        }
        const dic = newPage(infoIndex)
        if(dic == undefined){
            return false
        }
        page.obj.destroy()  // 旧页对象删除
        pageList[index] = dic  // 替换新页
        return true
    }

    // 删： 在 pageList 的 index 处，发送关闭指令。
    function closePage(index){
        pageList[index].obj.closePage()
    }

    // 删： 在 pageList 的 index 处，删除该页面。
    function delPage(index){
        const page = pageList[index]
        // 删除python逻辑控制器
        const flag = connector.delPage(page.ctrlKey)
        if(!flag){
            console.error("【Warning】删除页面失败：控制器["+page.ctrlKey+"]删除失败！")
            // return false // 暂时不管控制器删除失败
        }
        page.obj.destroy()  // 页对象删除
        pageList.splice(index, 1)  // 列表删除
        return true
    }

    // 改： 展示 index 页。
    function showPage(index){
        // 遍历，将展示的页面设为可视状态，其他页面设为非可视状态
        for(let i in pageList){
            if(i==index){
                pageList[i].obj.z = 0
                pageList[i].obj.visible = true
            }else{
                pageList[i].obj.z = -1
                pageList[i].obj.visible = false
            }
        }
    }

    // 改： 将一个原本在 index 的页移到 go 处。
    function movePage(index, go){
        var x = pageList.splice(index, 1)[0] // 删除
        pageList.splice(go, 0, x) // 添加
    }

    // 查： 传入下标 index 列表 list 报错内容前缀 msg ，返回下标是否合法。
    function isIndex(index, list, msg=""){
        if(index<0 || index>=list.length){
            if(msg)
                console.error(msg+"下标"+index+"超出范围"+(pageList.length-1)+"！")
            return false
        }
        return true
    }

    // ========================= 【辅助元素】 =========================
    
    // 页巢，作为已生成的页组件对象的父级。可挂载到可视节点下来展示。
    Item {
        id: pagesNest
        anchors.fill: parent
    }
    property var pagesNest: pagesNest
}