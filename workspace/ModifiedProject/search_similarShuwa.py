import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
# my code
import partial_DTW
import load_handData
import myfunc

MAX_DIST = 2



class Similarity_search():
    def __init__(self):
        self.keyDataNum = 0
        self.tgtDataNum = 0
        self.data_X = None
        self.data_Y = None
        self.indexLabel = '0y_L'
        # 中身忘れそうだから辞書型で書いてる
        self.weights_dict = {'0x_L':1, '0y_L':3, '1x_L':1, '1y_L':1, '2x_L':1, '2y_L':1, '3x_L':1, '3y_L':1, '4x_L':1, '4y_L':1, '5x_L':1, '5y_L':1, '6x_L':1, '6y_L':1, '7x_L':1, '7y_L':1, '8x_L':1, '8y_L':1, '9x_L':1, '9y_L':1,
            '10x_L':1, '10y_L':1, '11x_L':1, '11y_L':1, '12x_L':1, '12y_L':1, '13x_L':1, '13y_L':1, '14x_L':1, '14y_L':1, '15x_L':1, '15y_L':1, '16x_L':1, '16y_L':1, '17x_L':1, '17y_L':1, '18x_L':1, '18y_L':1, '19x_L':1, '19y_L':1, '20x_L':1, '20y_L':1,
            '0x_R':1, '0y_R':3, '1x_R':1, '1y_R':1, '2x_R':1, '2y_R':1, '3x_R':1, '3y_R':1, '4x_R':1, '4y_R':1, '5x_R':1, '5y_R':1, '6x_R':1, '6y_R':1, '7x_R':1, '7y_R':1, '8x_R':1, '8y_R':1, '9x_R':1, '9y_R':1,
            '10x_R':1, '10y_R':1, '11x_R':1, '11y_R':1, '12x_R':1, '12y_R':1, '13x_R':1, '13y_R':1, '14x_R':1, '14y_R':1, '15x_R':1, '15y_R':1, '16x_R':1, '16y_R':1, '17x_R':1, '17y_R':1, '18x_R':1, '18y_R':1, '19x_R':1, '19y_R':1, '20x_R':1, '20y_R':1}
        self.pathThreshold = 0.1
        self.frameThreshold = 20
        self.maxPathCost_tentative = 20
        self.all_path_Xrange_list = []

    def set_values(self):
        try:
            self.keyDataNum = int(input("key data number is (0~153):"))
            self.tgtDataNum = int(input("target data number is (0~4):"))
            print("select joint name in >>> ", end="")
            print(load_handData.frameNumAndjointLabel[1:])
            indexLabel = str(input("Please enter :"))
            #pathThreshold = int(input("path threshold is :"))
            #pathThreshold = int(input("frame threshold is :"))
        except:
            input("something is wrong")
            

    #　全ての手の情報要素についてパスを計算，結果を表示
    def calc_handElementPath(self):
        calc_partialDtw = partial_DTW.Calc_PartialDtw()
        self.data_Y = keyDataBase.AllHandData_df[self.keyDataNum][self.indexLabel].tolist()
        self.data_X = tgtDataBase.AllHandData_df[self.tgtDataNum][self.indexLabel].tolist()
        calc_partialDtw.key_data = self.data_Y
        calc_partialDtw.tgt_data = self.data_X
        calc_partialDtw.PATH_TH = self.pathThreshold # 出力パスの最大合計スコア
        calc_partialDtw.FRAME_TH = self.frameThreshold # 出力パスの最低経由フレーム数
        
        calc_partialDtw.create_matrix()

        path_list, path_Xrange_list = calc_partialDtw.select_path()

        if path_Xrange_list == []:
            myfunc.printline("path is not founded")
        else:
            self.print_path(path_Xrange_list)
            self.show_path(calc_partialDtw.costMatrix, self.data_X, self.data_Y, path_list)

    
    

    #　全ての手の情報要素についてパスを計算，all_path_Xrange_list に結果を保存
    def calc_handAllElementPath(self):
        all_path_Xrange_list = []
        for indexLabel in tqdm(load_handData.frameNumAndjointLabel[1:], bar_format="{l_bar}{bar:10}{r_bar}{bar:-10b}", colour='green'):
            calc_partialDtw = partial_DTW.Calc_PartialDtw()
            self.data_Y = keyDataBase.AllHandData_df[self.keyDataNum][indexLabel].tolist()
            self.data_X = tgtDataBase.AllHandData_df[self.tgtDataNum][indexLabel].tolist()
            calc_partialDtw.key_data = self.data_Y
            calc_partialDtw.tgt_data = self.data_X
            calc_partialDtw.PATH_TH = self.pathThreshold # 出力パスの最大合計スコア
            calc_partialDtw.FRAME_TH = self.frameThreshold # 出力パスの最低経由フレーム数
        
            calc_partialDtw.create_matrix()

            path_list, path_Xrange_list = calc_partialDtw.select_path()

            all_path_Xrange_list.append(path_Xrange_list)

            """
            if path_Xrange_list == []:
                myfunc.printline("path is not founded")
            else:
                self.print_path(path_Xrange_list)
                self.show_path(calc_partialDtw.costMatrix, self.data_X, self.data_Y, path_list)
            """

        self.calc_scoreData(all_path_Xrange_list)
        
    
    def calc_scoreData(self, all_path_Xrange_list):
        #len_Y = keyDataBase.AllHandData_df[self.keyDataNum].shape[0]
        totalNum_frame_tgt = tgtDataBase.originallyTotalFrame_list[self.tgtDataNum]

        scoreM = np.zeros((totalNum_frame_tgt, len(all_path_Xrange_list)), float)
        for j, path_Xrange_list in enumerate(all_path_Xrange_list):
            label = load_handData.frameNumAndjointLabel[1+j]
            weight = self.weights_dict[label]
            for path_Xrange in path_Xrange_list:
                
                path_head = (tgtDataBase.AllHandData_df[self.tgtDataNum]['frame'][path_Xrange[0] + 1])
                path_end = (tgtDataBase.AllHandData_df[self.tgtDataNum]['frame'][path_Xrange[1] + 1])
                path_cost = path_Xrange[2]

                #maxPathScore = (len_Y + ((path_end - path_head))) * MAX_DIST
                #maxPathScore =  (len_Y + (len_Y * 1.5)) * MAX_DIST

                path_score = (self.pathThreshold - path_cost)*weight # スコアに変換（スコア : 値が大きいほど類似度高い）
                for i in range(path_head, (path_end)): # path_head ~ path_end の値をiに代入
                    if scoreM[i][j] == 0: # スコアが入ってなければスコアを代入
                        scoreM[i][j] = path_score
                    elif scoreM[i][j] < path_score: # すでにスコアが入っているなら比較して代入
                        scoreM[i][j] = path_score
            

        frame_nums = list(range(0, totalNum_frame_tgt))
        frame_score = np.sum(scoreM, axis=1)
        plt.plot(frame_nums, frame_score, color="k") # 点列(x,y)を黒線で繋いだプロット
        plt.show() # プロットを表示
        #print(np.sum(scoreM, axis=1))



    
    # パスをグラフに描画して表示
    def show_path(self, list_2d, data_X, data_Y, path_list):

        aspectRatio = len(self.data_X)/len(self.data_Y) # 縦横比

        graphWindowSizeBase = 5
        plt.figure(figsize=(graphWindowSizeBase*aspectRatio, graphWindowSizeBase)) # ウィンドウサイズ

        gs = gridspec.GridSpec(2, 2, width_ratios=[1, 5*aspectRatio], height_ratios=[5, 1]) # グラフの個数，サイズ定義
        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1])
        ax4 = plt.subplot(gs[3])

        # ヒートマップ作成操作
        list_2d = np.transpose(list_2d) # 転置
        sns.heatmap(list_2d, square=False, cmap="Oranges", xticklabels=50, yticklabels=50, cbar=False, ax=ax2)
        ax2.invert_yaxis()  # 上下反転

        # ヒートマップにパスを描画
        for path in path_list:
            path_np = np.array(path)
            ax2.plot(path_np[:,0], path_np[:,1], c="C3")

        ax4.plot(range(self.data_X), self.data_X)
        ax4.set_xlabel("$X$")

        ax1.plot(self.data_Y, range(self.data_Y), c="C1")
        ax1.set_ylabel("$Y$")

        plt.show()

    # コンソールにパスをプリント
    def print_path(self, path_Xrange_list):
        for path_Xrange in path_Xrange_list:
            #myfunc.printline(path_Xrange[0])
            #myfunc.printline(tgtDataBase.AllHandData_df[keyDataNum]['frame'])
            path_head = tgtDataBase.AllHandData_df[self.tgtDataNum]['frame'][path_Xrange[0] + 1]
            path_end = tgtDataBase.AllHandData_df[self.tgtDataNum]['frame'][path_Xrange[1] + 1]
            path_cost = path_Xrange[2]
            #myfunc.printline("range -> {} ~ {} | cost -> {} ".format(path_Xrange[0], path_Xrange[1], path_cost)) # グラフ中のパスの範囲
            myfunc.printline("range -> {} ~ {} | cost -> {} ".format(path_head, path_end, path_cost))  # グラフ中のパスの範囲に対応する，元のデータでのフレーム範囲


if __name__ == '__main__':
    #userDir = "C:/Users/hisa/Desktop/research/"
    userDir = "C:/Users/root/Desktop/hisa_reserch/"
    keyData_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/tango/"
    tgtData_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/bunsyo/"

    keyDataBase = load_handData.HandDataBase() # データベース空箱
    tgtDataBase = load_handData.HandDataBase()



    # すべてのファイルを読み込み
    #load_handData.loadToDataBase(keyData_dirPath, keyDataBase, 'key')
    #load_handData.loadToDataBase(tgtData_dirPath, tgtDataBase, 'target')

    # 指定ファイルのみ読み込み
    #keyData_filePath = keyData_dirPath + '156_taiki.csv'
    keyData_filePath = keyData_dirPath + '154_part33.csv'
    tgtData_filePath = tgtData_dirPath + '4.csv'
    load_handData.loadToDataBase_one(keyData_dirPath, keyDataBase, 'key', keyData_filePath)
    load_handData.loadToDataBase_one(tgtData_dirPath, tgtDataBase, 'target', tgtData_filePath)

    #myfunc.printlist(tgtDataBase.AllHandData_df)
    #myfunc.printlines(tgtDataBase.AllFileNames)

    #myfunc.printline(keyDataBase.AllwristVelAndJointPos_L)
    
    similarity_search = Similarity_search()

    #similarity_search.calc_handElementPath()
    similarity_search.calc_handAllElementPath()

