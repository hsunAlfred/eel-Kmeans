# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime

import eel
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn import metrics, preprocessing
from sklearn.cluster import KMeans


'''進行數據分析時如果不知道從何下手，可使用分群方法中的kmeans將數據分成不同群組。
這個程式將kmeans方法包裝起來，方便未來再次使用。
這次分析的檔案是某個地方某家商店的銷售資料，每次每位顧客消費紀錄
檔名: purchase.csv；欄位: cid(顧客id)、amount(消費金額)、date(日期);
只要將分析的檔案檔名及欄位名稱設定完成，並取代原路徑下的 purchase.csv即可針對不同資料進行分析。
預設最大分群數為10，最佳分群數選擇為4；如要修改請透過參數設定，程式步驟如下：
1.先設定最大分群數，點選執行，執行過程中請勿關閉視窗，執行完成後會出現相關提示。
程式會從第1群開始到你設定的最大分群數分別計算第2步驟圖形資訊，進兔可透過IPython Console查看
2.此時會出現Marginal sum of squared distances及Silhouette Score的圖，可透過此圖選擇最佳分群數量，
3.設定完成後再點選執行，執行結果可透過最佳結果頁籤檢視
如果已有最佳分群數也可直接設定最佳分群數並計算，完成後可在最佳結果頁籤檢視
註1: Marginal sum of squared distances小於0代表多增加的分群數有助於降低變異
註2: Silhouette Score，介於1和-1間，越接近1越好，離1越遠越不好
註3: Silhouette Score輪廓係數參考網站https://reurl.cc/vDEXgl
註4: 圖片儲存於web資料夾下fig資料夾
註5: 最大分群數設定為10時約需2.5分鐘的運算時間，請耐心等候'''

def checkFolder(loc = './web/fig'):
    '''檢查圖片資料夾是否存在，如果存在回傳True，不存在就先建立在回傳True'''
    check = False
    if os.path.exists(loc):
        check = True
    else: 
        os.mkdir(loc)
        check = True
    return check

def dateChange(date):
    '''return 經過幾天, 格式化後日期'''
    today = datetime.now()
    #today = datetime(2016,1,1)
    dayChange, formatDate = [], []
    for i in date:
        i = i.split('-')
        dateF = datetime(int(i[0]), int(i[1]), int(i[2]))
        dayChange.append( (today-dateF).days )
        formatDate.append( dateF )
    return dayChange, formatDate

def RFM():
    # 讀取'purchase.csv'
    df = pd.read_csv('purchase.csv').sort_values(by = 'cid', ascending = True)
    
    '''以cid計算RFM欄位，return 有RFM欄位的df'''
    dayChange, formatDate = dateChange( list(df['date']) )
    df['formatDate'] = formatDate
    df['dayChange'] = dayChange
    
    df_groupby = df.groupby('cid')

    outDict = {
        'cid': df_groupby.size().index,
        'recent': df_groupby.min()['dayChange'],
        'freq': df_groupby.size().values,
        'money': df_groupby.mean()['amount'].values,
        'first_days': df_groupby.max()['dayChange'],
        'first_date': df_groupby.min()['formatDate'],
    }
    df_RFM = pd.DataFrame(outDict)
    df_RFM['money_log'] = np.log(df_RFM['money'])
    return df_RFM

def statisInfo(df):
    '''敘述統計，存入staInfo.json'''
    des = df.describe()
    
    staInfoDict = {}

    staInfoDict["rowname"] = list(des.index)
    for i in ["recent", "freq", "money", 'first_days']:
        staInfoDict[i] = list(des[i])
    with open('staInfo.json', 'w') as fn:
        json.dump(staInfoDict, fn)

def EDA(df_RFM):
    '''Exploratory Data Analysis， save fig'''
    
    if checkFolder() == False : return '建立檔案資料失敗'
    fn = []

    plt.figure(figsize=(35, 35))
    sns.set(font_scale = 1.7)
    sns.pairplot( df_RFM[['recent', 'freq', 'money_log', 'first_days']] )
    plt.tick_params(axis = 'both', size = 30)
    plt.savefig('./web/fig/variableRelation.jpg', bbox_inches = 'tight')
    fn.append(['variableRelation.jpg', '變數間散布圖\n'])
    
    plt.figure(figsize=(35, 35))
    sns.set(font_scale = 4)
    sns.heatmap( df_RFM[['recent', 'freq', 'money_log', 'first_days']].corr() )
    plt.tick_params(axis = 'both', size = 30)
    plt.savefig('./web/fig/variableCorr.jpg', bbox_inches = 'tight')
    fn.append(['variableCorr.jpg', '變數間相關係數熱區圖\n'])
    
    plt.figure(figsize=(35, 35))
    sns.set(font_scale = 6)
    sns.heatmap(df_RFM.isnull(),yticklabels=False,cbar=False,cmap='viridis')
    plt.tick_params(axis = 'both', size = 30)
    plt.savefig('./web/fig/variableIsNull.jpg', bbox_inches = 'tight')
    fn.append(['variableIsNull.jpg', '空值檢查圖\n'])
    
    plt.figure(figsize=(200, 75))
    n = 0
    sns.set(font_scale = 13)
    for i in ['recent', 'freq', 'money', 'first_days']:
        n += 1
        plt.subplot( 2, 4, n )
        sns.distplot( df_RFM[i])
        
        plt.subplot( 2, 4, n+4 )
        sns.boxplot(df_RFM[i], palette='winter')
    plt.tick_params(axis = 'both', size = 70)
    plt.tight_layout()
    plt.savefig('./web/fig/boxDistribution.jpg', bbox_inches = 'tight')
    fn.append(['boxDistribution.jpg', '箱型圖 & 分布圖\n'])
    
    '''
    plt.figure(figsize=(7, 7))
    for i in ['recent', 'freq', 'money_log', 'first_days']:
        sns.jointplot(x = 'cid', y = i, data = df_RFM)
    plt.savefig('./web/fig/jointplot.jpg', bbox_inches = 'tight')
    '''
    with open('./web/fig/EDA.txt', 'w') as f:
        for i in fn:
            f.write(i[0] + '-' + i[1])

def kmeansAnalysis(df_RFM, n_cluster = 10):
    '''執行kmeans，找出各分群數下WCSS，score。return WCSS, score'''
    WCSS, score = {}, {}

    df_scaler = preprocessing.StandardScaler().fit_transform( df_RFM[['recent', 'freq', 'money']] )
    
    for i in range(0, n_cluster):
        print(i+1, end = ' ')
        km = KMeans(n_clusters = i+1, init = 'k-means++', n_init = 5, max_iter = 300,
                    tol = 0.0001, verbose = 0, random_state = None, copy_x = True, 
                      algorithm = 'auto').fit(df_scaler)
                    #algorithm = "elkan" for dense data and "full" for sparse data
        
        WCSS[i+1] = (km.inertia_)
        if i != 0: score[i+1] = metrics.silhouette_score(df_RFM[['recent', 'freq', 'money']], km.labels_)
    return WCSS, score

def scorePicture(WCSS, score):
    '''將分數資訊繪圖'''

    if checkFolder() == False : return '建立檔案資料失敗'
    
    WCSS_gap = {}
    WCSS_gap = {k:(WCSS[k]-WCSS[k-1]) for k in WCSS.keys() if k != 1}
    
    plt.figure( figsize = (80, 40) )
    sns.set(font_scale = 1)
    fig, ax1 = plt.subplots()
    plt.xticks( [i for i in WCSS.keys() ] )
    ax1.scatter( WCSS_gap.keys(), WCSS_gap.values(), s = 5, c = 'DarkMagenta', 
                label = 'Marginal Sum of Squared Distances')
    
    ax2 = ax1.twinx()
    ax2.scatter( score.keys(), score.values(), s = 5, c = 'Salmon', 
                label = 'Silhouette Score')
    fig.legend(loc = 'upper right', bbox_to_anchor = (0.75, 1.01))
    plt.savefig('./web/fig/score.jpg')
    with open('./web/fig/score.txt', 'w') as f:
        f.write('./web/fig/score.jpg'+'-績效圖')
    
    WCSS_mean = pd.Series( list(WCSS_gap.values()) ).mean()
    WCSS_std = pd.Series( list(WCSS_gap.values()) ).std()
    score_mean = pd.Series( list(score.values()) ).mean()
    score_std = pd.Series( list(score.values()) ).std()
    
    WCSS_scale = [ (i-WCSS_mean)/WCSS_std for i in list(WCSS_gap.values()) ]
    score_scale = [ (i-score_mean)/score_std for i in list(score.values()) ]
    
    f = False
    for i in range(len(WCSS_scale)):
        if WCSS_scale[i] > score_scale[i]: 
            f = True
            with open('best.json', 'w') as fn:
                json.dump(i+1, fn)
            break
    if f == False:
        with open('best.json', 'w') as fn:
            json.dump(3, fn)

def reScaler(df_temp, df_RFM):
    '''反標準化'''
    centerPoint = pd.DataFrame()
    for i in df_temp.columns:
        ave = df_RFM[i].mean()
        std = df_RFM[i].std()
        
        centerPoint[i] = df_temp[i]*std+ave
    return centerPoint

def resultKmeans(df_RFM, n):
    '''透過最適分群數量執行kmeans'''
    df_scaler = preprocessing.StandardScaler().fit_transform( df_RFM[['recent', 'freq', 'money']] )
    km = KMeans(n_clusters = n, init = 'k-means++', n_init = 5, max_iter = 300, 
                         tol = 0.0001, verbose = 0, random_state = None, copy_x = True, 
                          algorithm = 'auto').fit(df_scaler)
    
    df_temp = pd.DataFrame(km.cluster_centers_)
    df_temp.columns = ['recent', 'freq', 'money']
    
    #centerPoint = reScaler(df_temp, df_RFM)
    
    return km

def bubblePlot(df_RFM, km):
    '''繪製泡泡圖，return fig'''
    df_RFM['label'] = km.labels_
    df_RFM['num'] = 1
    gbMean = df_RFM.groupby('label').mean()
    gbSum = df_RFM.groupby('label').sum()
    forBubble = pd.DataFrame()
    forBubble['group'] = list(set(km.labels_))
    forBubble['recent'] = np.log(gbMean['recent'] )*10
    forBubble['freq'] = gbMean['freq']
    forBubble['money'] = gbMean['money']
    forBubble['size'] = gbSum['num']
    forBubble['revenue'] = forBubble['size']*forBubble['money']/10
    
    plt.figure( figsize = (27, 18) )
    sns.set(font_scale = 4)
    plt.scatter( forBubble['freq'], forBubble['money'], c = forBubble['recent'], 
                cmap = 'OrRd', s = forBubble['revenue'], alpha = 0.5)
    plt.tick_params(axis = 'both', size = 20)
    plt.savefig('./web/fig/bubblePlot.jpg', bbox_inches = 'tight')
    with open("./web/fig/bubble.txt", 'w') as f:
        f.write('./web/fig/bubblePlot.jpg'+'-泡泡圖，x:平均消費次數/10，平均消費金額，顏色:最近一次消費時間，泡泡大小:營收貢獻度')

def findBest(nc = 10):
    #供calAll函數呼叫
    try:
        # 讀檔及計算RFM欄位
        df_RFM = RFM()
        #input(str(df_RFM.columns))
        
        # 敘述統計
        statisInfo(df_RFM.drop(['cid'], axis = 1))    #axis = 1  column
        #print(staInfo, '\n\n')
        
        # Exploratory Data Analysis
        EDA(df_RFM)
        #print(fn)
        
        # kmeans分析
        WCSS, score = kmeansAnalysis(df_RFM, nc)
        
        # 分群數量評分圖
        scorePicture(WCSS, score)
        
        with open('max.json', 'w') as fn:
            json.dump(nc, fn)
        print('success1')
        return True
    except Exception as e:
        print(e)
        return False

def showBest(bn = 0):
    #供calBest函數呼叫
    try:
        if bn == 0:
            with open('best.json', 'r') as fn:
                fnJson = json.load(fn)
            bn = int(fnJson)
        
        # 讀檔及計算RFM欄位
        df_RFM = RFM()
        #input(str(df_RFM.columns))
        
        # 最佳分群數kmeans資訊
        km = resultKmeans(df_RFM, bn)
        bubblePlot(df_RFM, km)
        #print(bp)
        with open('best.json', 'w') as fn:
            json.dump(bn, fn)
        print('success2')
        return True
    except Exception as e:
        print(e)
        return False


#if __name__ == '__main__':
    #print(findBest())
    #print(showBest())

@eel.expose
def calAll(a=10):
    #設定最大分群後計算
    return findBest(a)

@eel.expose
def calBest(b=4):
    #設定最是分群數後計算
    return showBest(b)
    
@eel.expose
def setBest():
    #讀取最佳分群數
    with open('best.json', 'r') as fn:
        fnJson = json.load(fn)
    staInfoJson = json.dumps(fnJson)
    return staInfoJson

@eel.expose
def setMax():
    #讀取最大分群數
    with open('max.json', 'r') as fn:
        fnJson = json.load(fn)
    staInfoJson = json.dumps(fnJson)
    return staInfoJson

@eel.expose
def sta():
    #讀取統計資訊
    with open('staInfo.json', 'r') as fn:
        fnJson = json.load(fn)
    staInfoJson = json.dumps(fnJson)
    return staInfoJson

@eel.expose
def about():
    #關於這個程式
    info = "進行數據分析時如果不知道從何下手，可使用分群方法中的kmeans將數據分成不同群組。<br>"
    info += "這個程式將kmeans方法包裝起來，方便未來再次使用。<br>"
    info += "這次分析的檔案是某個地方某家商店的銷售資料，每次每位顧客消費紀錄<br>"
    info += "檔名: purchase.csv；欄位: cid(顧客id)、amount(消費金額)、date(日期);<br>"
    info += "路徑:"+ str(os.path.abspath('..')) + "\\purchase.csv。<br>"
    info += "只要將分析的檔案檔名及欄位名稱設定完成，並取代原路徑下的 purchase.csv即可針對不同資料進行分析。<br>"
    info += "預設最大分群數為10，最佳分群數選擇為4；如要修改請透過參數設定，步驟如下：<br>"
    info += "1.先設定最大分群數，點選執行，執行過程中請勿關閉視窗，執行完成後會出現相關提示。<br>"
    info += "程式會從第1群開始到你設定的最大分群數分別計算第2步驟圖形資訊，進兔可透過IPython Console查看<br>"
    info += "2.此時會出現Marginal sum of squared distances及Silhouette Score的圖，可透過此圖選擇最佳分群數量，<br>"
    info += "3.設定完成後再點選執行，執行結果可透過最佳結果頁籤檢視<br>"
    info += "如果已有最佳分群數也可直接設定最佳分群數並計算，完成後可在最佳結果頁籤檢視<br>"
    info += "註1: Marginal sum of squared distances小於0代表多增加的分群數有助於降低變異<br>"
    info += "註2: Silhouette Score，介於1和-1間，越接近1越好，離1越遠越不好<br>"
    info += "註3: <a href = https://reurl.cc/vDEXgl>Silhouette Score輪廓係數參考網站</a>"

    return info
eel.init('web')
eel.start('index.html')

#findBest()
#showBest()
