import requests
from typing import Any


class LINE_Alert():
    def __init__(self, token:str = 'bdiFQTBKUI7QEJRTPCs5oNPGQ0ALlWUMMYQkDrtTK4n') -> None:
        # 若沒有給，預設為系統開發者
        self.token = token
    
    def req_line_alert(self, str_msg: Any):
        # 記錄Line Notify服務資訊
        Line_Notify_Account = {'Client ID': 'xxxxxxxxxxxxxxxxx',
                               'Client Secret': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                               'token': f'{self.token}'}

        # 將token放進headers裡面
        headers = {'Authorization': 'Bearer ' + Line_Notify_Account['token'],
                   "Content-Type": "application/x-www-form-urlencoded"}

        # 回傳測試文字
        params = {"message": f"\n{str(str_msg)}"}

        # 執行傳送測試文字
        # 使用post方法
        try:
            r = requests.post("https://notify-api.line.me/api/notify",
                              headers=headers, params=params)

        except Exception as e:
            return "訊息無法傳送"