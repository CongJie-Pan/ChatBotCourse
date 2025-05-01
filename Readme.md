- 執行linebot指南
  - cd linebottest
  - 在anaconda新創虛擬環境 : `python -m venv venv`
  - 執行該指令安裝依賴項：`pip install -r requirements.txt`
  - (已建立虛擬環境，開啟虛擬環境) run venv : `venv\Scripts\activate`
  - (anaconda) run python server : `python manage.py runserver`
  - (cmd) run ngrok server in cmd : `ngrok http 8000`
  - 將ngrok server新產生的 webhook 網址加上 `/callback` 輸入到 LINE Official Account Manager 的Messaging API的webhook欄位，如：
    `https://36b4-140-135-113-238.ngrok-free.app/callback`
