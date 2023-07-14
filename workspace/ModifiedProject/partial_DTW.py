import numpy as np
import myfunc
import os

key_data = None # key data
tgt_data = None # tgt data 

key_data_usedFrames = None # key data


paths = []
costs = [] 
dataDist = None


PATH_TH = None
FRAME_TH = None
dataCost = None

len_x = 1
len_y = 1


costM = None
pathM = None
headM = None

pathsAndCostData = [] # [パス開始フレーム, パス終了フレーム, コスト]*パス数 のデータセットを保存

class Calc_PartialDtw():
    def __init__(self):
        key_data_usedFrames = None # key data

        paths = []
        costs = [] 
        dataDist = None

        PATH_TH = None
        FRAME_TH = None
        dataCost = None

        costMatrix = None
        pathMatrix = None
        headMatrix = None

        len_x = 1
        len_y = 1

    # 距離計算
    def get_dist(self, x, y):
        return np.sqrt((x-y)**2) # ユークリッド距離

    # 最小値返却
    def get_min_cell(self, m0, m1, m2, i, j):
        if m0 < m1:
            if m0 < m2:
                return i - 1, j, m0
            else:
                return i - 1, j - 1, m2
        else:
            if m1 < m2:
                return i, j - 1, m1
            else:
                return i - 1, j - 1, m2

    def create_matrix(self):
        x = self.tgt_data # 検索される対象(ターゲット)
        y = self.key_data # 検索キー
        #dataDist = np.array(x).reshape(1, -1)**2 + np.array(y).reshape(-1, 1)**2
        #dataDist = np.sqrt((np.array(x).reshape(1, -1) - np.array(y).reshape(-1, 1))**2)

        len_x = len(x)
        len_y = len(y)
        #myfunc.printline(len_x)
        #myfunc.printline(len_y)

        costM = np.zeros((len_x, len_y))            # 合計距離行列 各点におけるパス開始点までの最短合計コストを保存
        pathM = np.zeros((len_x, len_y, 2), int)    # パス連結行列 各点において，その点を通るパスのひとつ前の点(連結関係)を保存
        headM = np.zeros((len_x, len_y), int)       # パス開始点行列 各点において，その点を通るパスの開始点を保存



        # 0列目
        costM[0, 0] = self.get_dist(x[0], y[0])
        for j in range(1, len_y):
            costM[0, j] = costM[0, j - 1] + self.get_dist(x[0], y[j])
            pathM[0, j] = [0, j - 1] # 1列目のパスは固定(縦直線)
            headM[0, j] = 0

        # i列目
        for i in range(1, len_x):
            # 0行目
            costM[i, 0] = self.get_dist(x[i], y[0])
            pathM[i, 0] = [i, 0]
            headM[i, 0] = i


            # i行目
            for j in range(1, len_y):
                # 左，下，左下のセルのうちコストが最小のセルを選択
                m_i, m_j, m_cost = self.get_min_cell(costM[i - 1, j],
                                    costM[i, j - 1],
                                    costM[i - 1, j - 1],
                                    i, j)
                costM[i, j] = m_cost + self.get_dist(x[i], y[j])
                pathM[i, j] = [m_i, m_j]
                headM[i, j] = headM[m_i, m_j]

            # ↑各種行列生成 
            # ↓パスの選択
            
            
            

            '''
            imin = np.argmin(costM[:(i+1), -1]) # リストの先頭からi+1の範囲
            #myfunc.printline(imin)

            dmin = costM[imin, -1]

            if dmin > PATH_TH: # 累算コストしきい値より小さい場合のみ以降のパス出力コードを実行
                continue

            for j in range(1, len_y):
                if (costM[i,j] < dmin) and (headM[i, j] < imin):
                    break
            else: # 直前のfor内でbreakが使用されなかった場合とforが実行されなかった場合処理される
                path = [[imin, len_y - 1]]
                temp_i = imin
                temp_j = len_y - 1

                while (pathM[temp_i, temp_j][0] != 0 or pathM[temp_i, temp_j][1] != 0):
                    path.append(pathM[temp_i, temp_j])
                    temp_i, temp_j = pathM[temp_i, temp_j].astype(int)
                
                #costM[headM <= imin] = 10000000
                #for ci in range(imin):
                #    costM[ci, -1] = 10000000
                #costM[headM <= imin] = 10000000

                
                original_path = np.array(path)

                path_head = original_path[0]
                #myfunc.printline(len(original_path))
                #myfunc.printline(len_y - 1)

                path_tail = original_path[len(original_path) - 1]
                #path_tail = original_path[len_y - 1]
                #myfunc.printline(len_y)

                #myfunc.printline((path_head[0] - path_tail[0]))

                #if int((path_head[0] - path_tail[0])) > FRAME_TH: # パスが指定フレーム数をまたがないときは出力しない
                paths.append(np.array(path))
                costs.append(dmin)
            '''
        dataCost = costM
        self.costMatrix = costM
        self.pathMatrix = pathM
        self.headMatrix = headM
        self.len_x = len_x
        self.len_y = len_y
    

    # プログラム見直しで高速化可能と思う
    def select_path(self):
        costM = self.costMatrix
        pathM = self.pathMatrix
        headM = self.headMatrix

        
        # しきい値未満のコストをもつパスを選択
        below_pathTH_i = np.where((costM[:, -1] < self.PATH_TH)) # return (list, type)　しきい値以下のコストを持つパスを取得

        pathEnd_SelByTH_list = [] # しきい値により選択されたパスの終了地点のi座標を保存
        # しきい値以上ののフレーム範囲であるパスを選択
        for path_end in below_pathTH_i[0]:
            path_range = path_end - headM[path_end, -1]
            if not path_range < self.FRAME_TH:
                pathEnd_SelByTH_list.append(path_end)


        path_list = []
        path_Xrange_list = []


        if not pathEnd_SelByTH_list == []:

            # パス絞り込み処理初期設定
            reservation_i = pathEnd_SelByTH_list[0]
            reservation_head = headM[reservation_i, -1]
            reservation_cost = costM[reservation_i, -1]
            for i in pathEnd_SelByTH_list[1:]: 
                #path_Xrange_list.append([headM[i, -1], i, costM[i, -1]]) # 閾値以下のパス全部ver
            


                # パスの開始地点が同じものが複数ある場合，最小コストのパスを選択
                if headM[i, -1] == reservation_head: # 一つ前に参照したパスと開始地点が同じかどうか
                    if costM[i, -1] <= reservation_cost: # 一つ前に参照したパスのコストとの比較
                        reservation_i = i
                        reservation_head = headM[reservation_i, -1]
                        reservation_cost = costM[reservation_i, -1]
                    if i != pathEnd_SelByTH_list[-1]: # pathEnd_SelByTH_listリストの最後の要素を参照したかどうか
                        continue # for内の以降の処理をスキップ

                # 条件を満たすパスを出力用リストに追加
                path_Xrange_list.append([headM[reservation_i, -1], reservation_i, costM[reservation_i, -1]]) # [開始フレーム, 終了フレーム]
                reservation_j = self.len_y - 1
                path_conn = [[reservation_i, reservation_j]]
                while pathM[reservation_i, reservation_j][1] != 0: # パスの終了地点から開始点までたどる
                    ref_i = reservation_i # 参照用変数として使用（値更新処理の順番によるミス防止）
                    ref_j = reservation_j
                    reservation_i = pathM[ref_i, ref_j][0]
                    reservation_j = pathM[ref_i, ref_j][1]
                    path_conn.append([reservation_i, reservation_j]) # 通過したマスとコストを保存
                path_list.append(path_conn)

                reservation_i = i
                reservation_head = headM[reservation_i, -1]
                reservation_cost = costM[reservation_i, -1]
                

        return path_list, path_Xrange_list
    
    # パスのコストが小さい順に三つを取得
    def select_path_topThree(self):
        costM = self.costMatrix
        pathM = self.pathMatrix
        headM = self.headMatrix

        
        # しきい値未満のコストをもつパスを選択
        below_pathTH_i = np.where((costM[:, -1] < self.PATH_TH)) # return (list, type)　しきい値以下のコストを持つパスを取得

        # しきい値以下のフレーム範囲であるパスのコストを例外値で上書き
        for i, cost in enumerate(costM[:, -1]):
            path_range = i - headM[i, -1]
            if not path_range < self.FRAME_TH:
                costM[i, -1] = 100
                

        # 値の小さい順から三つのコスト取得
        pathCost_topThree_np = np.sort(costM[:, -1])[:3]

        # 該当コストのパスの位置取得
        pathEnd_topThree = []
        for pathcost in pathCost_topThree_np:
            path_end = (np.where(costM[:, -1] == pathcost))[0]
            pathEnd_topThree.append(path_end[0])

        print(pathEnd_topThree)
        #pathCost_topThree_np = np.array(pathCost_topThree)

        
        #pathEnd_topThree = [np.where(costM[:, -1] == i) for i in pathCost_topThree_np]
        #pathEnd_topThree = pathEnd_topThree_np.tolist()

        path_list = []
        path_Xrange_list = []
        if not pathEnd_topThree == []:

            # パス絞り込み処理初期設定
            reservation_i = pathEnd_topThree[0]
            reservation_head = headM[reservation_i, -1]
            reservation_cost = costM[reservation_i, -1]
            for i in pathEnd_topThree[1:]: 
                #path_Xrange_list.append([headM[i, -1], i, costM[i, -1]]) # 閾値以下のパス全部ver
            


                # パスの開始地点が同じものが複数ある場合，最小コストのパスを選択
                if headM[i, -1] == reservation_head: # 一つ前に参照したパスと開始地点が同じかどうか
                    if costM[i, -1] <= reservation_cost: # 一つ前に参照したパスのコストとの比較
                        reservation_i = i
                        reservation_head = headM[reservation_i, -1]
                        reservation_cost = costM[reservation_i, -1]
                    if i != pathEnd_topThree[-1]: # pathEnd_topThreeリストの最後の要素を参照したかどうか
                        continue # for内の以降の処理をスキップ

                # 条件を満たすパスを出力用リストに追加
                path_Xrange_list.append([headM[reservation_i, -1], reservation_i, costM[reservation_i, -1]]) # [開始フレーム, 終了フレーム]
                reservation_j = self.len_y - 1
                path_conn = [[reservation_i, reservation_j]]
                while pathM[reservation_i, reservation_j][1] != 0: # パスの終了地点から開始点までたどる
                    ref_i = reservation_i # 参照用変数として使用（値更新処理の順番によるミス防止）
                    ref_j = reservation_j
                    reservation_i = pathM[ref_i, ref_j][0]
                    reservation_j = pathM[ref_i, ref_j][1]
                    path_conn.append([reservation_i, reservation_j]) # 通過したマスとコストを保存
                path_list.append(path_conn)

                reservation_i = i
                reservation_head = headM[reservation_i, -1]
                reservation_cost = costM[reservation_i, -1]
                

        return path_list, path_Xrange_list
