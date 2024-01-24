# 【间隙·树·排序算法】 GapTree_Sort_Algorithm
# 对OCR结果或PDF提取的文本进行版面分析，按人类阅读顺序进行排序。
# https://github.com/hiroi-sora/GapTree_Sort_Algorithm

from typing import Callable


class GapTree:
    def __init__(self, get_bbox: Callable):
        """
        :param get_bbox: 函数，传入单个文本块，
                        返回该文本块左上角、右下角的坐标元组 (x0, y0, x1, y1)
        """
        self.get_bbox = get_bbox

    # ======================= 调用接口 =====================
    # 对文本块列表排序
    def sort(self, text_blocks: list):
        """
        对文本块列表，按人类阅读顺序进行排序。

        :param text_blocks: 文本块对象列表
        :return: 排序后的文本块列表
        """

        # 封装块单元，并求页面左右边缘
        units, page_l, page_r = self._get_units(text_blocks, self.get_bbox)
        # 求行和竖切线
        cuts, rows = self._get_cuts_rows(units, page_l, page_r)
        # 求布局树
        root = self._get_layout_tree(cuts, rows)
        # 求树节点序列
        nodes = self._preorder_traversal(root)
        # 求排序后的 原始文本块序列
        new_text_blocks = self._get_text_blocks(nodes)

        # 测试：缓存中间变量，以便调试输出
        self.current_rows = rows
        self.current_cuts = cuts
        self.current_nodes = nodes

        return new_text_blocks

    # 获取以区块为单位的文本块二层列表
    def get_nodes_text_blocks(self):
        """
        获取以区块为单位的文本块二层列表。需要在 sort 后调用。

        :return: [ [区块1的text_blocks], [区块2的text_blocks]... ]
        """
        result = []
        for node in self.current_nodes:
            tbs = []
            if node["units"]:
                for unit in node["units"]:
                    tbs.append(unit[1])
                result.append(tbs)
        return result

    # ======================= 封装块单元列表 =====================
    # 将原始文本块，封装为 ( (x0,y0,x2,y2), 原始 ) 。并检查页边界。
    def _get_units(self, text_blocks, get_bbox):
        # 封装单元列表 units [ ( (x0,y0,x2,y2), 原始文本块 ), ... ]
        units = []
        page_l, page_r = float("inf"), -1  # 记录文本块的左右最值，作为页边界
        for tb in text_blocks:
            x0, y0, x2, y2 = get_bbox(tb)
            units.append(((x0, y0, x2, y2), tb))
            if x0 < page_l:
                page_l = x0
            if x2 > page_r:
                page_r = x2
        units.sort(key=lambda a: a[0][1])  # 按顶部从上到下排序
        return units, page_l, page_r

    # ======================= 求行和竖切线 =====================
    """
    扫描所有文本块，获取所有行和竖切线。
    一个行，由一组垂直位置接近的文本块所组成。
    一条竖切线，由多个连续行中，同一位置的间隙所组成。间隙划分同一行中不同列的文本块。
    输入：一个页面上的文本块单元列表 units=[ ( (x0,y0,x2,y2), _ ) ] 。必须按上到下排序。
    返回：
      竖切线列表 cuts=[ ( 左边缘x, 右边缘x, 起始行号, 结束行号 ) ] 。从左到右排序
      页面上的行 rows=[ [unit...] ] 。从上到下，从左到右排序
    """

    def _get_cuts_rows(self, units, page_l, page_r):
        # 使用间隙组 gaps2 更新 gaps1 。返回： 更新后的gaps1 , gaps1中被移除的间隙
        def update_gaps(gaps1, gaps2):
            flags1 = [True for _ in gaps1]  # gaps1[i] 是否彻底移除
            flags2 = [True for _ in gaps2]  # gaps2[i] 是否新加入
            new_gaps1 = []
            for i1, g1 in enumerate(gaps1):
                l1, r1, _ = g1
                for i2, g2 in enumerate(gaps2):  # 对每一个gap1，考察所有gap2
                    l2, r2, _ = g2
                    # 计算交集的起点和终点
                    inter_l = max(l1, l2)
                    inter_r = min(r1, r2)
                    # 如果交集有效
                    if inter_l <= inter_r:
                        new_gaps1.append((inter_l, inter_r, g1[2]))  # 更新 gap1 左右边缘
                        flags1[i1] = False  # 旧的 gap1 不应移除
                        flags2[i2] = False  # 新的 gap2 不应添加
            # gap2 新加入
            for i2, f2 in enumerate(flags2):
                if f2:
                    new_gaps1.append(gaps2[i2])
            # 记录 gaps1 彻底移除的项
            del_gaps1 = []
            for i1, f1 in enumerate(flags1):
                if f1:
                    del_gaps1.append(gaps1[i1])

            return new_gaps1, del_gaps1

        # ========================================

        page_l -= 1  # 保证页面左右边缘不与文本块重叠
        page_r += 1
        # 存放所有行。“row”指同一水平线上的单元块（可能属于多列）。 [ [unit...] ]
        rows = []
        # 已生成完毕的竖切线。[ ( 左边缘x, 右边缘x , 起始行号, 结束行号 ) ]
        completed_cuts = []
        # 考察中的间隙。 [ (左边缘x, 右边缘x , 开始行号) ]
        gaps = []
        row_index = 0  #  当前行号
        unit_index = 0  # 当前块号
        # 从上到下遍历所有文本行
        l_units = len(units)
        while unit_index < l_units:
            # ========== 查找当前行 row ==========
            unit = units[unit_index]  # 当前行最顶部的块
            u_bottom = unit[0][3]
            row = [unit]  # 当前行
            # 查找当前行的剩余块
            for i in range(unit_index + 1, len(units)):
                next_u = units[i]
                next_top = next_u[0][1]
                if next_top > u_bottom:
                    break  # 下一块的顶部超过当前底部，结束本行
                row.append(next_u)  # 当前行添加块
                unit_index = i  # 步进 已遍历的块序号
            # ========== 查找当前行的间隙 row_gaps ==========
            row.sort(key=lambda x: (x[0][0], x[0][2]))  # 当前行中的块 从左到右排序
            row_gaps = []  # 当前行的间隙 [ ( ( 左边缘l, 右边缘r ), 开始行号) ]
            search_start = page_l  # 本轮搜索的线段起始点为页面左边缘
            for u in row:  # 遍历当前行的块
                l = u[0][0]  # 块左侧
                r = u[0][2]  # 块右侧
                # 若块起始点大于搜索起始点，那么将这部分加入到结果
                if l > search_start:
                    row_gaps.append((search_start, l, row_index))
                # 若块结束点大于搜索起始点，更新搜索起始点
                if r > search_start:
                    search_start = r
            # 页面右边缘 加入最后一个间隙
            row_gaps.append((search_start, page_r, row_index))
            # ========== 更新考察中的间隙组 ==========
            gaps, del_gaps = update_gaps(gaps, row_gaps)
            # gaps 中被移除的项，加入生成完毕的竖切线 completed_cuts
            row_max = row_index - 1  # 竖切线结束行号
            for dg1 in del_gaps:
                completed_cuts.append((*dg1, row_max))
            # ========== End ==========
            rows.append(row)  # 总行列表添加当前行
            unit_index += 1
            row_index += 1
        # 遍历结束，收集 gaps 中剩余的间隙，组成延伸到最后一行的竖切线
        row_max = len(rows) - 1  # 竖切线结束行号
        for g in gaps:
            completed_cuts.append((*g, row_max))
        completed_cuts.sort(key=lambda c: c[0])
        return completed_cuts, rows

    # ======================= 求布局树 =====================
    """
    一个布局树节点表示一个区块。定义：
    node = {
        "x_left": 节点左边缘x,
        "x_right": 右边缘x,
        "r_top": 顶部的行号,
        "r_bottom": 底部的行号,
        "units": [], # 节点内部的文本块列表（除了根节点为空，其它节点非空） 
        "children": [], # 子节点，有序
    }
    """

    def _get_layout_tree(self, cuts, rows):
        # 竖切线，将一个横行切开，断开的区域为“间隙”。
        # 生成每一行对应的间隙 (左侧,右侧) 坐标列表
        rows_gaps = [[] for _ in rows]
        for g_i, cut in enumerate(cuts):
            for r_i in range(cut[2], cut[3] + 1):
                rows_gaps[r_i].append((cut[0], cut[1]))

        root = {  # 根节点
            "x_left": cuts[0][0] - 1,
            "x_right": cuts[-1][1] + 1,
            "r_top": -1,
            "r_bottom": -1,
            "units": [],
            "children": [],
        }
        completed_nodes = [root]  # 已经完成结束的节点
        now_nodes = []  # 当前正在考虑的节点。无顺序

        # ========== 结束一个节点，加入节点树 ==========
        def complete(node):
            node_r = node["x_right"] - 2  # 当前节点右边界
            max_nodes = []  # 符合父节点条件的，最低的完成节点列表
            max_r = -2  # 符合父节点条件的最低行数
            # 在完成列表中，寻找父节点
            for com_node in completed_nodes:
                # 父节点的垂直投影必须包含当前右界
                if node_r < com_node["x_left"] or node_r > com_node["x_right"] + 0.001:
                    continue
                # 父节点底部必须在当前之上
                if com_node["r_bottom"] >= node["r_top"]:
                    continue
                # 遇到更低的符合条件节点
                if com_node["r_bottom"] > max_r:
                    max_r = com_node["r_bottom"]
                    max_nodes = [com_node]
                    continue
                # 遇到同样低的符合条件节点
                if com_node["r_bottom"] == max_r:
                    max_nodes.append(com_node)
                    continue
            # 在最低列表中，寻找最右的节点作为父节点
            max_node = max(max_nodes, key=lambda n: n["x_right"])
            max_node["children"].append(node)  # 加入父节点
            completed_nodes.append(node)  # 加入完成列表

        # ========== 遍历每行，更新节点树 ==========
        for r_i, row in enumerate(rows):
            row_gaps = rows_gaps[r_i]  # 当前行的间隙组
            u_i = g_i = 0  # 当前考察的 文本块、间隙下标

            # ========== 检查是否有正在考虑的节点 可以结束 ==========
            new_nodes = []
            for node in now_nodes:  # 遍历节点
                l_flag = r_flag = False  # 标记节点左右边缘是否延续
                completed_flag = False  # 标记节点是否可以结束
                x_left = node["x_left"]  # 左右边缘坐标
                x_right = node["x_right"]
                for gap in row_gaps:  # 遍历该行所有间隙
                    if gap[1] == x_left:  # 节点左边缘被间隙右侧延续
                        l_flag = True
                    if gap[0] == x_right:  # 右边缘被间隙左侧延续
                        r_flag = True
                    # 任意间隙在本节点下方，打断本节点
                    if x_left < gap[0] < x_right or x_left < gap[1] < x_right:
                        completed_flag = True
                        break
                if not l_flag or not r_flag:  # 左右任意一个边缘无法延续
                    completed_flag = True
                if completed_flag:  # 节点结束，加入节点树
                    complete(node)
                else:  # 节点继续
                    node["r_bottom"] = r_i
                    new_nodes.append(node)
            now_nodes = new_nodes

            # ========== 从左到右遍历，将文本块加入对应列的节点 ==========
            while u_i < len(row):
                unit = row[u_i]  # 当前块
                # ========== 当前块 unit 位于间隙 g_i 与 g_i+1 之间的区间 ==========
                x_l = row_gaps[g_i][1]  # 左间隙 g_i 的右边界
                x_r = row_gaps[g_i + 1][0]  # 右间隙 g_i+1 的左边界
                # 检查区间是否正确
                if unit[0][0] > x_r:  # 块比右间隙更右，说明到了下一个区间
                    g_i += 1  # 间隙步进，块不步进
                    continue
                # ========== 检查当前块可否加入已有的节点 ==========
                flag = False
                for node in now_nodes:
                    # 若某个节点的左右侧坐标，与当前块一致，则当前块加入节点
                    if node["x_left"] == x_l and node["x_right"] == x_r:
                        node["units"].append(unit)
                        flag = True
                        break
                if flag:
                    u_i += 1  # 块步进
                    continue
                # ========== 根据当前块创建新的节点，加入待考虑节点 ==========
                now_nodes.append(
                    {
                        "x_left": x_l,
                        "x_right": x_r,
                        "r_top": r_i,
                        "r_bottom": r_i,
                        "units": [unit],
                        "children": [],
                    }
                )
                u_i += 1  # 块步进
        # 将剩余节点也加入节点树
        for node in now_nodes:
            complete(node)
        # 整理所有节点
        for node in completed_nodes:
            # 所有子节点 按从左到右排序
            node["children"].sort(key=lambda n: n["x_left"])
            # 所有块单元 按从上到下排序
            node["units"].sort(key=lambda u: u[0][1])
        return root

    # ======================= 前序遍历布局树，求节点序列 =====================
    def _preorder_traversal(self, root):
        if not root:
            return []
        stack = [root]
        result = []
        while stack:
            node = stack.pop()
            result.append(node)
            # 将当前节点的子节点逆序压入栈中，以保证左子节点先于右子节点处理
            stack += reversed(node["children"])
        return result

    # ======================= 从节点序列中，提取原始文本块序列 =====================
    def _get_text_blocks(self, nodes):
        result = []
        for node in nodes:
            for unit in node["units"]:
                result.append(unit[1])
        return result
