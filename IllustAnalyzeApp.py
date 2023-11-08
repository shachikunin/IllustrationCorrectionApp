import streamlit as st
import base64
import time
import os
import re
import numpy as np
import urllib.request,urllib.parse
import datetime
from openai import OpenAI
from PIL import Image
import io

if "chatHistory" not in st.session_state:
      st.session_state.execInitProcess = False
      st.session_state.chatAction = ""
      st.session_state.checkpoint = []
      st.session_state.reviewer = ""

os.environ["OPENAI_API_KEY"] = st.secrets.GPT3ApiKey.api_key
client = OpenAI()

checkpointList = ["テーマ性",
                  "構図",
                  "光と影",
                  "テクスチャ",
                  "デッサン",
                  "遠近法",
                  "全体のバランス",
                  "カラーバランス",
                  "透視図法",
                  "人体解剖学",]

reviewerList = [
                  "辛口で鋭いが、とても面倒見の良いプロイラストレーターの関西弁の男",
                  "爽やかで優しく、初心者に寄り添うプロイラストレーターの男",
                  "デザインの知識が豊富で、重要なことをきちんと強調してくれるプロイラストレーターの男",
                  "モチベーションが上がるように応援してくれるが、時々辛辣になる17歳のプロイラストレーターの女",
                  "母性があり、わかりやすい説明を意識しているプロイラストレーターの女",]

def make_image(image_url):
      
      checkpoint = ','.join(st.session_state.checkpoint)
      start = time.time()  # 現在時刻（処理開始前）を取得
      response = client.chat.completions.create(
      model="gpt-4-vision-preview",
      messages=[
            {
                  "role": "user",
                  "content": [
                  {
                        "type": "text", 
                        "text": f"これは私が描いたイラストです。このイラストを{st.session_state.chatAction}ようにしてください。ただし、文章は{st.session_state.reviewer}のように振舞い、次の観点を重点的に述べてください。\n評価観点:{checkpoint}"
                  },
                  {
                        "type": "image_url",
                        "image_url":  {
                              "url": f"data:image/jpeg;base64,{image_url}"
                        }
                  },
                  ],
            }
      ],
      max_tokens=1000,
      )
      
      end = time.time()

      time_diff = end - start
      st.write("処理時間:" + str(round(time_diff, 2)) + "[s]")
      
      return response.choices[0]

def main():
      #アプリ起動時の処理、二重にロードしたくない処理はここで行う
      if st.session_state.execInitProcess == False:
            
            #初期化処理完了
            st.session_state.execInitProcess = True
      
      st.set_page_config(page_title = "手軽にイラストを添削してもらおう！")
      st.title("イラスト添削アプリ")
      
      st.sidebar.title("各種設定")
      st.session_state.chatAction = st.sidebar.radio("イラストの評価", ("褒める", "添削する"))
      st.session_state.checkpoint = st.sidebar.multiselect("評価のポイント", checkpointList)
      st.session_state.reviewer = st.sidebar.radio("評価員の性格", reviewerList)
      
      uploaded_file = st.file_uploader("画像をアップロードしてください。")
      if uploaded_file is not None:
            file_type = uploaded_file.type
            if file_type == "image/png" or file_type == "image/jpeg":
                  image = Image.open(uploaded_file)
                  st.image(image)
                  
                  if st.button("レビュー開始", key=0):
                        buffered = io.BytesIO()
                        image.save(buffered, format="PNG")
                        base64_image  = base64.b64encode(buffered.getvalue()).decode()
                        
                        response = make_image(base64_image)
                        st.info(st.session_state.reviewer + " による評価")
                        st.write(response.message.content)
                        
                        st.balloons()
            else:
                  st.error('PNGまたはJPGファイルのみアップロード可能です。')
            

if __name__ == "__main__":
      main()