

class KeyList:
    '''
    用来维护图片表格列表的数据结构。
    可通过键key和下标index来访问。
    每一项data为字典。
    '''

    def __init__(self):
        self.__dataList = []
        self.__dataDict = {}

    # =============== 增 ==============================
    def append(self, key, data):
        '''在最末尾插入一项元素，指定key和内容'''
        self.__dataDict[key] = data
        self.__dataList.append(key)

    # =============== 删 ==============================
    def delete(self, key=None, index=-1):
        '''删除指定元素。传入key或index。'''
        if self.isKey(key):
            del self.__dataDict[key]
            self.__dataList.remove(key)
        elif self.isIndex(index):
            k = self.indexToKey(index)
            del self.__dataDict[k]
            del self.__dataList[index]
        else:
            raise Exception(
                f'List delete : 请传入合法的key或index！当前为 {key} , {index}')

    def clear(self):
        '''清空全部元素'''
        self.__dataList.clear()
        self.__dataDict.clear()

    # =============== 查 ==============================
    def len(self):
        '''返回长度'''
        return len(self.__dataList)

    def isEmpty(self):
        '''空返回True'''
        return len(self.__dataList) <= 0

    def isKey(self, key):
        '''若存在键为key的项，返回True'''
        return key in self.__dataDict

    def isIndex(self, index):
        '''若index合法，返回True'''
        return index >= 0 and index < len(self.__dataList)

    def indexToKey(self, index):
        '''传入index，返回该项的key'''
        return self.__dataList[index]

    def get(self, key=None, index=-1):
        '''查询指定元素。传入key或index，返回data。'''
        if self.isKey(key):
            return self.__dataDict[key]
        elif self.isIndex(index):
            return self.__dataDict[self.__dataList[index]]
        else:
            raise Exception(f'List get : 请传入合法的key或index！当前为 {key} , {index}')

    def getKeys(self):
        '''返回key列表'''
        return self.__dataDict.keys()

    def getItemValueList(self, dKey):
        '''将所有data中dKey对应的值提取成列表'''
        return [d[dKey] for d in self.__dataDict.values()]

    def isDataItem(self, dKey, dValue):
        '''查找所有data中是否存在键为dKey、值为dValue的元素，是返回True'''
        for d in self.__dataDict.values():
            if dKey in d and d[dKey] == dValue:
                return True
        return False
