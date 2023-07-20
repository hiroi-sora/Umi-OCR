// ======================================================
// =============== 标签栏的复制器的逻辑管理 ===============
// ======================================================

/* 页面表现（布局、动画）应该在继承的子类中编写


    delegate:              // 子类中填入按钮组件，属性必须包含：
        title: title_      // 标题
        checked: checked_  // 是否选中
        width: 宽
        height: 高
*/
    
import QtQuick 2.15
import QtQuick.Controls 2.15

Repeater {

    // ========================= 【属性与变量】 =========================

    model: ListModel{} // 标签元素列表，初始为空
    property bool isLock: false


    Component.onCompleted: {
        qmlapp.tab.bar = this // 逆向连接引用
    }
    // ========================= 【增删改查】 =========================

    // 增： 在 index 处，插入一个标题为 title 的标签。
    function addTab(index, title){ // index=-1 代表尾部插入
        if(index<0) index=model.count // 尾部添加
        else if(index>model.count){
            console.error("【Error】添加标签失败：下标"+index+"超出范围"+model.count+"！")
            return
        }

        model.insert(index, {
            "title_": title,
            "checked_": false
        })
    }

    // 删： 在 index 处，删除该标签。
    function delTab(index){
        if(!isIndex(index, "【Error】删除标签失败："))
            return
        model.remove(index) // 删除按钮
    }

    // 改： 在 index 处，重设标签的 title 。
    function changeTab(index, title){
        if(!isIndex(index, "【Error】重命名标签失败："))
            return
        model.set(index, {"title_": title})
    }

    // 改： 选中 index 标签。
    function showTab(index){
        if(!isIndex(index, "【Error】选中标签失败："))
            return
        for(let i=0; i<model.count; i++){
            itemAt(i).checked = (i==index)
            // model.set(index, {"checked_": (i==index)})
        }
    }

    // 改： 将一个原本在 index 的标签移到 go 处。
    function moveTab(index, go){
        if(!isIndex(index, "【Error】移动标签失败：起点"))
            return
        if(!isIndex(go, "【Error】移动标签失败：终点"))
            return
        model.move(index, go, 1)
    }

    // 改： 重置所有标签的序号
    function resetIndex() {
        for(let i=0, c=model.count; i<c; i++){
            itemAt(i).index = i
        }
    }

    // 查： 返回下标 index 是否合法。
    function isIndex(index, msg=""){
        if(index<0 || index>=model.count){
            if(msg)
                console.error(msg+"下标"+index+"超出范围"+(model.count-1)+"！")
            return false
        }
        return true
    }

    // ========================= 【创建和删除事件】 =========================

    // 创建新标签时
    onItemAdded: { 
        resetIndex() // 重设序号
    }

    onItemRemoved: {
        resetIndex() // 重设序号
    }
}