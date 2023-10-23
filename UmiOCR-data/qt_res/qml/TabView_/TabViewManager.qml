// ====================================================
// =============== 标签页整体的逻辑管理器 ===============
// ====================================================


import QtQuick 2.15
import "../TabPages"
import "../Configs"

Item {
    id: tabViewManager
    // ========================= 【子管理器】 =========================

    PagesManager{ id: page } // 页管理器
    property alias page: page
    property var bar: undefined // 栏管理器
    // 连接别名
    property alias infoList: page.infoList
    property alias pageList: page.pageList
    // 控制属性
    property bool barIsLock: false // 栏是否已锁定
    property int showPageIndex: -1 // 当前展示的标签页序号
    property var openPageList: [] // 当前已打开的的标签页列表，存放URL，用于记录历史操作

    // 持久化存储
    Settings_ { 
        id: settings
        category: "TabPageManager" // 自定义类别名称
        property alias openPageList: tabViewManager.openPageList
        property alias showPageIndex: tabViewManager.showPageIndex
        property bool refresh: false // 用于刷新
        function save(){ // 手动刷新
            refresh=!refresh
        }
    }

    // ========================= 【初始化】 =========================

    function init() { // 需要延迟加载，全局初始化完毕后执行
        page.initListUrl() // 页管理器初始化文件
        // 提取所有info的url
        const urlList = [] 
        for(let i in infoList){
            urlList.push(infoList[i].url)
        }
        // 从历史记录中搜索仍存在的项
        const newPage = []
        const newIndex = []
        for(let i in openPageList){
            const urlIndex = urlList.indexOf(openPageList[i])
            if(urlIndex == -1){
                console.error("【Error】上次url历史中的 "+openPageList[i]+" 已经丢失！")
            }
            else if(!page.getComp(urlIndex)){
                console.error("【Error】上次url历史中的 "+openPageList[i]+" 页面组件类未初始化！")
            } else {
                newPage.push(openPageList[i])
                newIndex.push(urlIndex)
            }
        }
        openPageList = [] // 清空当前页面记录，重新添加
        // 初始为空，默认添加导航页
        if(newPage.length == 0){
            addNavi()
        }
        else { 
            let showPageI = showPageIndex // 另起一变量记录showPageIndex，以免受addTabPage的影响。
            // 初始不为空，添加初始页
            for(let i in newIndex){
                addTabPage(i, newIndex[i])
            }
            // 初始选中
            if(!isIndex(showPageI, pageList, "【Warning】初始选中页面失败："))
                showPageI = 0
            showTabPage(showPageI)
        }
        settings.save()
        console.log("% TabViewManager 初始化页面完毕！")
    }

    // ========================= 【增删改查】 =========================

    // 增： 在 index 处，插入一个 infoList[infoIndex] 标签页。
    function addTabPage(index, infoIndex){ // index=-1 代表尾部插入
        if(index<0) index = pageList.length // 尾部添加
        else if(index>pageList.length){
            console.error("【Error】添加标签页失败：页面下标"+index+"超出范围"+pageList.length+"！")
            return
        }
        if(!isIndex(infoIndex, infoList, "【Error】添加标签页失败：信息"))
            return
        if(!page.addPage(index, infoIndex)) return
        bar.addTab(index, infoList[infoIndex].title)
        openPageList.splice(index, 0, infoList[infoIndex].url)
        if(showPageIndex >= index) { // 若选中页在被添加页之前
            showPageIndex++ // 选中页序号后移
        }
    }

    // 增： 在最后，添加一个导航页，并选中该页
    function addNavi(){
        addTabPage(-1, 0) // 添加页
        showTabPage(-1) // 选中页
    }

    // 删：关闭页面（点击关闭按钮），不立刻删除
    function closeTabPage(index){
        page.closePage(index)
    }

    // 删： 在 index 处，删除该标签页。
    function delTabPage(index){
        if(!isIndex(index, pageList, "【Error】删除标签页失败：页面"))
            return
        page.delPage(index)
        bar.delTab(index)
        openPageList.splice(index, 1)
        if(showPageIndex > index) { // 若选中页在被删除页之后
            showPageIndex-- // 选中页序号前移
        }
        else if(showPageIndex == index){ // 若选中页就是被删除页
            if(pageList.length == 0){ // 已经没页了，就补充一个导航页
                addNavi()
            } else if (index == pageList.length){ // 原本在队尾，则展示当前队尾页
                showTabPage(-1)
            } else { // 原本不在队尾，则展示原本的后一个页
                showTabPage(index)
            }
        }
        else { // 删除不影响选中页，则手动刷新存储
            settings.save()
        }
    }

    // 改： 将 index 处的标签页，改为 infoIndex 页。
    function changeTabPage(index, infoIndex){
        if(!isIndex(index, pageList, "【Error】更改标签页失败：页面"))
            return
        if(!isIndex(infoIndex, infoList, "【Error】更改标签页失败：信息"))
            return
        // 检查pageList中是否已有目标页面，有则展示该页
        for(let i in pageList) {
            if(pageList[i].infoIndex===infoIndex) {
                showTabPage(i)
                return
            }
        }
        // 尚无目标页，则删除原页，新增目标页
        if(!page.changePage(index, infoIndex)) return
        bar.changeTab(index, infoList[infoIndex].title)
        openPageList[index] = infoList[infoIndex].url
        settings.save() // 改动列表项，需要手动触发保存
        if(showPageIndex == index) // 若原本是选中的，则改页后要再选中一次
            showTabPage(index)
    }

    // 改： 展示 index 页。index=-1 代表尾部
    function showTabPage(index){
        if(index<0) index = pageList.length-1
        if(!isIndex(index, pageList, "【Error】展示页面失败：页面"))
            return
        showPageIndex = index
        page.showPage(index)
        bar.showTab(index)
    }

    // 改： 展示 obj 页。
    function showTabPageObj(obj){
        const index = getTabPageIndex(obj)
        if(index < 0) {
            return // 未找到对应页下标
        }
        showTabPage(index)
    }

    // 改： 将一个原本在 index 的页移到 go 处。
    function moveTabPage(index, go){
        if(!isIndex(index, pageList, "【Error】移动页面失败：起点"))
            return
        if(!isIndex(go, pageList, "【Error】移动页面失败：终点"))
            return
        page.movePage(index, go)
        bar.moveTab(index, go)
        if(showPageIndex == index) // 若原本是选中的，则改页后要同步选中位置
            showPageIndex = go
        for(let i in pageList){ // 记录新URL顺序
            openPageList[i] = pageList[i].info.url
        }
    }

    // 查： 传入页面对象 obj ，返回该对象的下标。
    function getTabPageIndex(obj){
        for(let i in pageList){
            if(pageList[i].obj===obj)
                return i
        }
        return -1
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

    // 查： 返回 infoList
    function getInfoList() {
        return infoList
    }
    // 查： 返回 pageList
    function getPageList() {
        return pageList
    }
}
