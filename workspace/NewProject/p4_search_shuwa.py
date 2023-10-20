import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
import seaborn as sns
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
import PySimpleGUI as sg
import shutil
import time
import random


# my code
#import partial_match_DTW
import p_load_handData
import p_partial_match_DTW
import p_gui
import my_functions as my


class Search_shuwa():
    def __init__(self):
        self.keyDataBase = None
        self.tgtDataBase = None
        self.output_dir = None
        self.cost_TH_dict = {}
        self.weight_dict = {}
        self.frame_TH = 10
        self.feature_label_list = None
        self.all_path_sect_cost_list = []

        self.keyName = None
        self.tgtName = None
        self.key_len = None
        self.tgt_len = None

        self.similar_section_file = None

        self.isPlt_sect = True

        self.isSave_path = True
        self.isSave_score = True

        self.isShow_path = True
        self.isShow_score = True

        self.saveFile = None

    def set_values(self, cost_TH_file, weight_file, keyDataDir, tgtDataDir):
        # コスト閾値
        values_dict = {}
        with open(cost_TH_file, "r") as f:
            for line in f:
                key, value = line.split(":")# 行をコロンで分割してキーと値に分ける
                values_dict[key] = float(value.strip()) # 改行コードを削除するためにstrip()を使う
        self.cost_TH_dict = values_dict
        
        # 重みデータ
        values_dict = {}
        with open(weight_file, "r") as f:
            for line in f:
                key, value = line.split(":")# 行をコロンで分割してキーと値に分ける
                values_dict[key] = float(value.strip()) # 改行コードを削除するためにstrip()を使う
        self.weight_dict = values_dict
        
        # 特徴ラベルリスト
        with open("values/feature_label.txt", "r", encoding="utf-8") as f:
            self.feature_label_list = f.read().split('\n')
        
        self.frame_TH = 10
        self.output_dir = "result/"
        self.similar_section_file = "similar_sections/tgt4_key33.txt"

        my.printline("loading handData..")
        self.keyDataBase = p_load_handData.get_handDataBase(keyDataDir)
        self.tgtDataBase = p_load_handData.get_handDataBase(tgtDataDir)
        my.printline("conpleted")

        

    def save_dict(self):
        # cost_TH_dict保存
        with open("result/values/cost_TH_dict.txt", "w") as f:
            for key, value in self.cost_TH_dict.items():
                f.write(f"{key}:{value}\n")
        
        with open("result/values/names.txt", "w") as f:
            f.write('key file : ' + str(self.keyName) + '\n')
            f.write('tgt file : ' + str(self.tgtName) + '\n')
    
    def calc_feature(self):
        # gui
        keyName, tgtName = p_gui.select_key_tgt(self.keyDataBase.handDataName_list, self.tgtDataBase.handDataName_list)
        featureLabel = p_gui.select_feature()

        partial_match_DTW = p_partial_match_DTW.Partial_match_DTW()

        # 指定手話のデータフレームをfloat型で取得
        keyData_df = self.keyDataBase.handData_df_dict[keyName].astype(float)
        tgtData_df = self.tgtDataBase.handData_df_dict[tgtName].astype(float)

        # 指定特徴のデータをリストとして取得
        keyData_feature = keyData_df[featureLabel].tolist()
        tgtData_feature = tgtData_df[featureLabel].tolist()

        self.key_len = len(keyData_feature)
        self.tgt_len = len(tgtData_feature)

        self.keyName = keyName
        self.tgtName = tgtName

        partial_match_DTW.set_values(keyData_feature, 
                                    tgtData_feature, 
                                    self.cost_TH_dict[featureLabel], 
                                    self.frame_TH)

        partial_match_DTW.create_matrix()
        
        path_list, path_sect_cost_list = partial_match_DTW.select_path()

        if path_sect_cost_list == []:
            my.printline("path is not founded")
        else:
            #self.print_path(path_sect_cost_list)
            self.plt_path(partial_match_DTW.costMatrix, 
                        path_list, path_sect_cost_list, 
                        featureLabel, 
                        keyData_feature, 
                        tgtData_feature)

    def calc_syuwa(self):
        # gui
        keyName, tgtName = p_gui.select_key_tgt(self.keyDataBase.handDataName_list, self.tgtDataBase.handDataName_list)
        # 指定手話のデータフレームをfloat型で取得
        keyData_df = self.keyDataBase.handData_df_dict[keyName].astype(float)
        tgtData_df = self.tgtDataBase.handData_df_dict[tgtName].astype(float)

        self.saveFile = "search_" + str(keyName) + "_from_" + str(tgtName)
        
        p_gui_progressBar = p_gui.ProgressBar()
        p_gui_progressBar.set_window(len(self.feature_label_list))

        for featureLabel in self.feature_label_list:
            partial_match_DTW = p_partial_match_DTW.Partial_match_DTW()


            # 指定特徴のデータをリストとして取得
            keyData_feature = keyData_df[featureLabel].tolist()
            tgtData_feature = tgtData_df[featureLabel].tolist()

            self.key_len = len(keyData_feature)
            self.tgt_len = len(tgtData_feature)

            self.keyName = keyName
            self.tgtName = tgtName

            partial_match_DTW.set_values(keyData_feature, 
                                        tgtData_feature, 
                                        self.cost_TH_dict[featureLabel], 
                                        self.frame_TH)

            partial_match_DTW.create_matrix()

            #########################
            ########################
            
            path_list, path_sect_cost_list = partial_match_DTW.select_path()

            self.all_path_sect_cost_list.append(path_sect_cost_list)


            self.plt_path(partial_match_DTW.costMatrix, 
                        path_list, path_sect_cost_list, 
                        featureLabel, 
                        keyData_feature, 
                        tgtData_feature)
            
            self.plt_path(partial_match_DTW.costMatrix, path_list, path_sect_cost_list, featureLabel, keyData_feature, tgtData_feature)

            # gui更新
            p_gui_progressBar.update_window()


    # パスをグラフに描画して表示
    def plt_path(self, list_2d, path_list, path_sect_cost_list, featureLabel, keyData, tgtData):

        # ウィンドウ横幅
        #aspectRatio = self.tgt_len/self.key_len # フレーム数に変動させる
        aspectRatio = 4

        graphWindowSizeBase = 5
        plt.figure(figsize=(graphWindowSizeBase*aspectRatio, graphWindowSizeBase)) # ウィンドウサイズ

        gs = gridspec.GridSpec(2, 2, width_ratios=[1, 5*aspectRatio], height_ratios=[5, 1]) # グラフの個数，サイズ定義
        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1])
        ax4 = plt.subplot(gs[3])

        # ヒートマップ作成操作
        list_2d = np.transpose(list_2d) # 転置
        sns.heatmap(list_2d, square=False, cmap='Greys', xticklabels=50, yticklabels=50, cbar=False, ax=ax2)
        ax2.invert_yaxis()  # 上下反転

        
        # ヒートマップにパスを描画
        if not path_list == []:
            for i, path in enumerate(path_list):
                cost = path_sect_cost_list[i][2]
                color = cm.Reds((cost/self.cost_TH_dict[featureLabel])**3) # コストの値に応じて色変更
                path_np = np.array(path)
                ax2.plot(path_np[:,0], path_np[:,1], c=color)

        ax4.plot(tgtData)
        ax4.set_xlabel("$X$")

        ax1.plot(keyData, range(len(keyData)), c="C1")
        ax1.set_ylabel("$Y$")
        
        
        
        if self.isPlt_sect:
            self.plt_similar_section(ax2, "similar_sections/tgt4_key33.txt")

        if self.isSave_path:
            plt.savefig("result/path/" + featureLabel +'.png')

        if self.isShow_path:
            plt.show()
        
        plt.clf()
        plt.close()


    # 設定した類似区間に矢印を描画
    def plt_similar_section(self, ax, sections_file):
        with open(sections_file) as f:
            section_list = []
            for line in f.readlines():
                head, end = line.split(',')
                head =int(head)
                end = int(end)
                '''
                section_list.append([int(head),int(end)])
                similar_sect_path = []
                for j in range(int(head), int(end)+1):
                    similar_sect_path.append([0,j])
                similar_sect_path_np = np.array(similar_sect_path)
                ax.plot(similar_sect_path_np[:,1], similar_sect_path_np[:,0], c="b")
                '''
                arrow_props = dict(arrowstyle="->", mutation_scale=10, color="blue", linewidth=1)
                ax.annotate("", xy=[head, 0], xytext=[end-5, 0], arrowprops=arrow_props)
                ax.annotate("", xy=[end, 0], xytext=[head+5, 0], arrowprops=arrow_props)

    def plt_scoreData(self):
        #totalNum_frame_tgt = self.tgtDataBase.originallyTotalFrame_list[self.tgtDataNum]
        #print(self.tgtDataBase.handData_df_dict[self.tgtName].index.tolist())
        #tgtLen = len(self.tgtDataBase.handData_df_dict[self.tgtName].index.tolist())
    
        # all_path_sect_cost_listを展開，関節要素についてパスとスコアの情報を取得，時系列スコアデータを行列計算
        scoreM = np.zeros((self.tgt_len, len(self.all_path_sect_cost_list)), float)

        for j, path_sect_cost_list in enumerate(self.all_path_sect_cost_list):
            #label = self.feature_labels[1+j]
            label = self.feature_label_list[j]
            weight = self.weight_dict[label]
            Reference_value = self.cost_TH_dict[label]
            for path_Xrange in path_sect_cost_list:
                
                path_head = path_Xrange[0]
                path_end = path_Xrange[1]
                path_cost = path_Xrange[2]

                #maxPathScore = (len_Y + ((path_end - path_head))) * MAX_DIST
                #maxPathScore =  (len_Y + (len_Y * 1.5)) * MAX_DIST

                path_score = (Reference_value - path_cost)*weight # スコアに変換（スコア : 値が大きいほど類似度高い）
                for i in range(path_head, (path_end)): # path_head ~ path_end の値をiに代入
                    if scoreM[i][j] == 0: # スコアが入ってなければスコアを代入
                        scoreM[i][j] = path_score
                    elif scoreM[i][j] < path_score: # すでにスコアが入っているなら比較して代入
                        scoreM[i][j] = path_score
        
        frame_nums = list(range(0, self.tgt_len))
        frame_score = np.sum(scoreM, axis=1)
        plt.plot(frame_nums, frame_score, c="r") # 点列(x,y)を黒線で繋いだプロット

        # 保存，出力の選択
        if self.isSave_score:
            plt.savefig(self.output_dir + self.saveFile + "_score.png")
        
        if self.isShow_score:
            plt.show()
        
        plt.clf()
        plt.close()

def main():
    keyDataDir = "handData/key/d3_feature/"
    tgtDataDir = "handData/tgt/d3_feature/"
    #tgtDataDir = "handData/tgt/d3_feature_key/"

    cost_TH_file = "values/cost_TH_dict.txt"
    weight_file = "values/weight_dict.txt"

    search_shuwa = Search_shuwa()
    search_shuwa.set_values(cost_TH_file, weight_file, keyDataDir, tgtDataDir)
    #search_shuwa.calc_syuwa()
    search_shuwa.calc_feature()
    
    #search_shuwa.plt_scoreData()


if __name__ == '__main__':
    #p_gui.select_feature()

    
    main()