# WorkFlow
部屬虛擬機:https://192.168.2.250/ui/#/host/vms/12  
部屬容器:git_server  
部屬網址:http://192.168.2.118:4080/index  




<img src="/MVC.png" width="500">



## 專案目的
建置屬於公司內自己的工作流系統,提升各部門之間的工作追蹤進度。


## 專案描述
前段技術:html,jquery,bootstrap,css,javescript  
後段框架:python django  
資料庫採用:MSSQL  






<img src="/工作流流程.png" width="1000">



## 靜態文件配置
<img src="/靜態文件配置.jpg" width="500">




## 專案指令紀錄




# 修改使用者 確保和系統使用者一致

```
sudo nano /etc/nginx/nginx.conf
```

![使用者](/user.jpg)




# 創建設定檔
```
sudo nano /etc/nginx/sites-available/Workflow


```

一律從4080進入會由Nginx進入統一配置  
![創建設定檔](/Nginx配置圖.jpg)



# 創建允許連結
```
sudo ln -s /etc/nginx/sites-available/Workflow /etc/nginx/sites-enabled
```
![允許連結](/允許連結.jpg)



# 重新啟動nginx
```
sudo systemctl restart nginx
```

# 查看錯誤訊息
```
cat /var/log/nginx/error.log
```

# 查看Cached的地方
```
cat /etc/memcached.conf
```




# 重新佈署注意事項

## 檢查Debug模式
![注意事項01](/注意事項01.jpg)


## 檢查靜態文件導向
![注意事項02](/注意事項02.jpg)




## 使用gunicorn server 提供服務








# 系統維護專區
![使用者介紹01](/使用者介紹01.jpg)
![使用者介紹02](/使用者介紹02.jpg)
![使用者介紹03](/使用者介紹03.jpg)