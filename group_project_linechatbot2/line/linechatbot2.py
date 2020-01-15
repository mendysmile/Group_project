# -*- coding: utf-8 -*-
from keras.models import load_model
import pandas as pd
import numpy as np
import pymongo
from gensim.models.keyedvectors import KeyedVectors
import jieba
# 引用Web Server套件
from flask import Flask, request, abort
# 從linebot 套件包裡引用 LineBotApi 與 WebhookHandler 類別
from linebot import (
    LineBotApi, WebhookHandler, WebhookParser
)
# 引用無效簽章錯誤
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from geopy.distance import geodesic
import pandas as pd
import json
from linebot.models import *
from sklearn.externals import joblib

#引入按鍵模板
from linebot.models.template import(
    ButtonsTemplate
)
# 載入基礎設定檔
secretFileContentJson=json.load(open("line_secret_key",'r',encoding="utf-8"))
server_url=secretFileContentJson.get("server_url")

# 設定Server啟用細節
app = Flask(__name__,static_url_path = "/images" , static_folder = "./images/")

# 生成實體物件
line_bot_api = LineBotApi(secretFileContentJson.get("channel_access_token"))
handler = WebhookHandler(secretFileContentJson.get("secret_key"))

# 啟動server對外接口，使Line能丟消息進來
@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def inputs(list_1):
    for n, i in enumerate(list_1):
        try:
            list_1[n] = int(i)
        except:
            list_1[n] = 0
    train_data_range = [36.000000, 1284.1109, 3.0000000, 24980000, 1.0000000, 3.000000]
    train_data_min = [20.0, -6.11089842, 0.00000000, 20000.0000, 0.00000000, 1.0000000]
    userdf = pd.DataFrame(columns=["age", "serveTime", "Loan", "SalPerY", "holdCard", "Career"])
    userdf.loc[0] = list_1
    userdf -= train_data_min
    userdf /= train_data_range
    userdf = userdf.astype(float)
    model = load_model('model.h5')
    preds = model.predict(userdf)
    qq = np.where(preds[0] == np.max(preds[0]))
    #     print(preds)
    # print(max(preds))
    #     print(preds.item(np.argmax(preds)))
    list_2 = ['0萬~5萬', '5萬~10萬', '10萬~15萬', '15萬~20萬', '20萬~25萬', '25萬~30萬', '30萬~35萬', '35萬~40萬', '40萬~45萬', '45萬~50萬',
              '50萬~55萬', '55萬~60萬',
              '60萬~65萬', '65萬~70萬', '70萬~75萬', '75萬~80萬', '80萬~85萬', '85萬~90萬', '90萬~95萬', '95萬~100萬']
    return str(list_2[qq[0][0]])

def managePredict(event, mtext):  #處理LIFF傳回的FORM資料
    flist = mtext[3:].split('/')  #去除前三個「#」字元再分解字串
    flist[1]=str(int(flist[1])*12+int(flist[2]))
    flist[4]=str(int(flist[4])*10000)
    item1 = int(flist[0])  #取得輸入資料
    item2 = int(flist[1])
    item3 = int(flist[3])
    item4 = int(flist[4])
    item5 = int(flist[5])
    item6 = int(flist[6])
#     text1 = "您輸入的資料如下："
#     text1 += "\n年齡："+ flist[0]
#     text1 += "\n年資："+ flist[1] +"個月"
#     text1 += "\n年薪："+ flist[4] +"元"
#     text1 += "\n職業："+ flist[6]
#     text1 += "\n有無貸款："+ flist[3]
#     text1 += "\n有無持卡："+ flist[5]
    list_1=[item1, item2, item3, item4, item5, item6]
    quota=inputs(list_1)
    dict_mongodb = {'age': item1, 'serve_time': item2, 'loan': item3, 'sal_per_year': item4, 'hold_card': item5,
                    'career': item6, 'quota': quota}
    client = pymongo.MongoClient(host='123.241.175.34', port=27017)
    client.admin.authenticate('root', '1qaz@WSX3edc')
    db = client.predict
    db.quota.insert_one(dict_mongodb)
    client.close()
    text1 = "您的預估額度為："+ quota
    try:
        message = TextSendMessage(  #顯示資料
            text = text1
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))

# 0.撈出存在excel的向量轉為matrix
def get_article_matrix(article, i):
    aa = article.loc[:, ["article_vector_matrix"]][i:i + 1]
    # 轉ARRAY再轉list
    b = np.array(aa)
    b = b[0].tolist()  # list
    # 切
    c = str(b[0]).split(',')
    article_matrix = np.mat(c).astype(float)
    return (article_matrix)

# 1.載入檔案
article = pd.read_excel(r"/app/article_news_vector _final.xlsx")
articles_matrix = [get_article_matrix(article, i) for i in range(5594)]

# 2.載入bin檔
wv_from_bin = KeyedVectors.load_word2vec_format(r'/app/100win20min_count3cbow1.bin',binary=True)

# 3.輸入文字
def please_input_words(rlist):
    # 斷詞
    wordlist = jieba.lcut(rlist, cut_all=False)
    print(wordlist)
    input_vector_matrix = get_article_avgvector(wordlist)
    print()
    print("這幾個字的平均向量是:")
    print(input_vector_matrix)
    return (input_vector_matrix)

# 4.獲取輸入詞的平均向量
def get_article_avgvector(wordlist):
    # 取每篇文章平均向量
    # x=np.matrix(wv_from_bin[word])安安?
    len_wordlist = 0
    input_avgvector_matrix = 0
    for word in wordlist:
        try:
            x = np.matrix(wv_from_bin[word])
            input_avgvector_matrix += x
            len_wordlist += 1
        except:
            pass
    if type(input_avgvector_matrix) == int:
        input_avgvector_matrix = np.matrix(wv_from_bin['購物'])
    else:
        input_avgvector_matrix = input_avgvector_matrix / len_wordlist
    return (input_avgvector_matrix)

# 5.餘弦相似度
def cos_similar(vector_a, vector_b):
    """
    计算两个向量之间的余弦相似度
    :param vector_a: 向量 a
    :param vector_b: 向量 b
    :return: sim
    """
    vector_a = np.mat(vector_a)
    vector_b = np.mat(vector_b)
    num = float(vector_a * vector_b.T)
    denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    cos = num / denom
    similar = 0.5 + 0.5 * cos
    return similar

# 測試開始_餘弦相似度
def manageRecommend(event, mtext):
    rlist = mtext[1:]
    input_vector_matrix = please_input_words(rlist)
    most_similar_article = cosine_similar_find_article(rlist, input_vector_matrix)
    text_1 = str(most_similar_article)
    try:
        message = TextSendMessage(  # 顯示資料
            text=text_1
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))

# 比對
def cosine_similar_find_article(rlist, input_vector_matrix):
    articles_matrix_list = []
    for b in range(5594):
        result = cos_similar(input_vector_matrix, articles_matrix[b])
        articles_matrix_list.append(result)
    print("第", articles_matrix_list.index(max(articles_matrix_list)), "篇新聞最相似")
    most_similar = articles_matrix_list.index(max(articles_matrix_list))
    most_similar_article = np.array(article[most_similar:most_similar + 1]['content'])[0]
    print("文章內文為:", "\n", "\n", "------------------------------------------------------------", "\n",
          np.array(article[most_similar:most_similar + 1]['content'])[0])
    return most_similar_article

df_store_list=pd.read_excel(r'/app/store_location.xlsx',encoding='utf-16',index_col=0)
def manageLocation(event, latitude, longitude):
    lat = latitude
    lng = longitude
    neardf = near_by_info(lat,lng)
    text_1 = neardf
    try:
        message = TextSendMessage(  #顯示資料
            text = text_1
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
def near_by_info(lat, lng):
    store=[]
    addr=[]
    info=[]
    distance=[]
    for i in range(len(df_store_list)):
        address=(df_store_list['lat'][i],df_store_list['lng'][i])
        #計算當下位置與商家位置距離
        dist=geodesic(address,(lat,lng)).kilometers
        #若小於3公里
        if dist<3:
            store.append(df_store_list['store'][i])
            if df_store_list['store'][i]=='屈臣氏':
                info.append('刷LINEPay卡5%回饋')
            elif df_store_list['store'][i]=='美廉社':
                info.append('刷LINEPay卡2%回饋')
            addr.append(df_store_list['address'][i])
            distance.append(str(round(dist,2))+'km')
    neardf = pd.DataFrame({'店家':store,'優惠內容':info,'地址':addr,'距離':distance},columns=['店家','優惠內容','地址','距離'])
    if len(neardf)==0:
        neardf = '附近沒有優惠店家'
        return neardf
    elif len(neardf)<=5:
        neardf=str(neardf)
        return neardf
    elif len(neardf)>5:
        neardf=neardf.sort_values(by='距離')[:5]
        neardf=str(neardf)
        return neardf

# 消息清單
reply_message_list = [
TextSendMessage(text="關注信手卡來，找到適合你的卡片。"),
    TextSendMessage(text="哈囉！😊歡迎加入信手卡來，我們提供關於信用卡💳的各種資訊，歡迎點擊您有興趣的功能喔！😄"),
    ImageSendMessage(original_content_url='https://i.imgur.com/YXXiCvZ.jpg',
    preview_image_url='https://i.imgur.com/Zs6btto.jpg'),
    ImageSendMessage(original_content_url='https://i.imgur.com/x0vZwjt.jpg',
    preview_image_url='https://i.imgur.com/GEVyxIt.jpg')
]

# 預測額度流程
reply_message_list_predict = [
TextSendMessage(text="想知道您的核卡額度？🤔輸入下列訊息，我們就會幫您預測喔！😉"),
    TemplateSendMessage(
     alt_text='Buttons template',
      template=ButtonsTemplate(
      title='信用卡核卡額度',
    text='輸入訊息，開始預測',
    actions=[
      {
        "type": "uri",
        "label": "開始預測",
        "uri": "line://app/1653471513-2vnJK4EJ"
      }
    ],
  )
  )
]

# 新聞推薦流程
reply_message_list_news = [
TextSendMessage(text="您想知道哪一類的信用卡相關資訊呢？點選下方按鈕或是輸入@加上您感興趣的內容，例如:@我想知道2020最強神卡，我們就會提供相關訊息給您🙂"),
ImagemapSendMessage(
    base_url='https://i.imgur.com/Ohn59DU.png#',
    alt_text='新聞推薦',
    base_size=BaseSize(height=1686, width=2500),
    actions=[
        MessageImagemapAction(
            text='#旅遊優惠新聞',
            area=ImagemapArea(
                x=178, y=71, width=986, height=407
            )
        ),
        MessageImagemapAction(
            text='#行動支付新聞',
            area=ImagemapArea(
                x=768, y=619, width=970, height=414
            )
        ),
        MessageImagemapAction(
            text='#交通加油新聞',
            area=ImagemapArea(
                x=183, y=1152, width=970, height=440
            )
        ),
        MessageImagemapAction(
            text='#促銷活動新聞',
            area=ImagemapArea(
                x=1327, y=47, width=999, height=416
            )
        ),
        MessageImagemapAction(
            text='#繳費繳稅新聞',
            area=ImagemapArea(
                x=1330, y=1140, width=966, height=436
            )
        )
    ]
)
]

# 卡片推薦流程
reply_message_list_recommend = [
TextSendMessage(text="不知道哪張信用卡適合自己嗎？😥讓我們來幫你挑選適合您的卡片吧！🤗"),
    TemplateSendMessage(
     alt_text='Buttons template',
      template=ButtonsTemplate(
      thumbnail_image_url='https://i.imgur.com/lNxWpfE.png',
        title='您想要什麼樣的卡片？',
        text='您是初次辦卡？還是已經有信用卡了呢？',
    actions=[
      {
        "type": "uri",
        "label": "已持有：類似卡片推薦",
        "uri": "https://.ngrok.io/card"
      },
      {
        "type": "uri",
        "label": "初辦卡：卡片功能推薦",
        "uri": "https://.ngrok.io"
      }
    ],
  )
  )
]

#統計資料
reply_message_list_statics = [
    TemplateSendMessage(
     alt_text='Buttons template',
      template=ButtonsTemplate(
      title='使用者統計資訊',
    text='觀看統計資訊',
    actions=[
      {
        "type": "uri",
        "label": "立即前往",
        "uri": "http://.ngrok.io/kibana"
      }
    ],
  )
  )
]

#用戶行動軌跡
reply_message_list_googlemap = [
    TemplateSendMessage(
     alt_text='Buttons template',
      template=ButtonsTemplate(
        title='用戶行動軌跡',
        text='請點選您想觀看的行動軌跡資料',
    actions=[
      {
        "type": "uri",
        "label": "行動軌跡(不含停留點)",
        "uri": "https://.ngrok.io/tracking_map"
      },
      {
        "type": "uri",
        "label": "行動軌跡(含停留點)",
        "uri": "https://.ngrok.io/stay_point_map"
      }
    ],
  )
  )
]
'''

設計一個字典
    當用戶輸入相應文字消息時，系統會從此挑揀消息

'''

# 根據自定義菜單故事線的圖，設定相對應訊息
template_message_dict = {
    "[::text:]請幫我預測核卡額度":reply_message_list_predict,
    "[::text:]請給我相關新聞":reply_message_list_news,
    "[::text:]請幫我推薦信用卡":reply_message_list_recommend,
    "[::text:]請給我相關統計資料":reply_message_list_statics,
    "[::text:]請給我用戶行動軌跡":reply_message_list_googlemap,
}

'''

當用戶發出文字消息時，判斷文字內容是否包含[::text:]，
    若有，則從template_message_dict 內找出相關訊息
當用戶發出文字消息含有###時，進入額度預測功能
當用戶發出文字消息含有@時，進入新聞推薦功能

'''

# 用戶發出文字消息時， 按條件內容, 回傳文字消息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if (event.message.text.find('::text:') != -1):
        #         print(event.message.text)
        line_bot_api.reply_message(
            event.reply_token,
            template_message_dict.get(event.message.text)
        )
    elif event.message.text.find('###') != -1 and len(event.message.text) > 3:
        managePredict(event, event.message.text)
    elif event.message.text.find('@') != -1 and len(event.message.text) > 2:
        manageRecommend(event, event.message.text)
    elif event.message.text == "#旅遊優惠新聞":
        article = pd.read_excel(r"/app/article_news_vector _final_30_1225.xlsx")
        a = np.random.randint(len(np.array(article[article['label'] == 29]['content'])))
        text_1 = str(np.array(article[article['label'] == 29]['content'])[a])
        try:
            message = TextSendMessage(  # 顯示資料
                text=text_1
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif event.message.text == "#行動支付新聞":
        article = pd.read_excel(r"/app/article_news_vector _final_30_1225.xlsx")
        b = np.random.randint(len(np.array(article[article['label'] == 13]['content'])))
        text_1 = str(np.array(article[article['label'] == 13]['content'])[b])
        try:
            message = TextSendMessage(  # 顯示資料
                text=text_1
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif event.message.text == "#交通加油新聞":
        article = pd.read_excel(r"/app/article_news_vector _final_30_1225.xlsx")
        c = np.random.randint(len(np.array(article[article['label'] == 23]['content'])))
        text_1 = str(np.array(article[article['label'] == 23]['content'])[c])
        try:
            message = TextSendMessage(  # 顯示資料
                text=text_1
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif event.message.text == "#促銷活動新聞":
        article = pd.read_excel(r"/app/article_news_vector _final_30_1225.xlsx")
        d = np.random.randint(len(np.array(article[article['label'] == 0]['content'])))
        text_1 = str(np.array(article[article['label'] == 0]['content'])[d])
        try:
            message = TextSendMessage(  # 顯示資料
                text=text_1
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif event.message.text == "#繳費繳稅新聞":
        article = pd.read_excel(r"/app/article_news_vector _final_30_1225.xlsx")
        e = np.random.randint(len(np.array(article[article['label'] == 26]['content'])))
        text_1 = str(np.array(article[article['label'] == 26]['content'])[e])
        try:
            message = TextSendMessage(  # 顯示資料
                text=text_1
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))

# #用戶傳送地理位置後，取其經緯度
@handler.add(MessageEvent, message=LocationMessage)
def handle_post_message(event):
    latitude=event.message.latitude
    longitude=event.message.longitude
    manageLocation(event, latitude, longitude)
#     print(event.message.latitude)
#     print(event.message.longitude)

'''

撰寫用戶關注時，我們要處理的商業邏輯
1. 取得用戶個資，並存回伺服器
2. 把先前製作好的自定義菜單，與用戶做綁定
3. 回應用戶，歡迎用的文字消息與圖片消息

'''

# 載入Follow事件
from linebot.models.events import (
    FollowEvent
)

# 告知handler，如果收到FollowEvent，則做下面的方法處理
@handler.add(FollowEvent)
def reply_text_and_get_user_profile(event):
    # 取出消息內User的資料
    user_profile = line_bot_api.get_profile(event.source.user_id)

    # 將用戶資訊存在檔案內
    with open("/app/users.txt", "a") as myfile:
        myfile.write(json.dumps(vars(user_profile), sort_keys=True))
        myfile.write('\r\n')

        # 將菜單綁定在用戶身上
    linkRichMenuId = secretFileContentJson.get("rich_menu_id")
    linkResult = line_bot_api.link_rich_menu_to_user(secretFileContentJson["self_user_id"], linkRichMenuId)

    # 回覆文字消息與圖片消息
    line_bot_api.reply_message(
        event.reply_token,
        reply_message_list
    )

'''

執行此句，啟動Server，觀察後，按左上方塊，停用Server

'''

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=False)