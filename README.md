# 用途・目的
これらのファイルは，ESP32のDeepsleepからの復帰にかかる時間を計測するためのプログラムである．時間を測定するESP32(測定器)にboot.pyを実装し、測定されるESP32(被測定器)にmain.pyとespnow_helper.pyを実装する．これらのプログラムについて説明する．外部ウェイクアップを使用して，測定器がGPIO2をHighにすると，被測定器がDeepsleepから復帰する．復帰後，ネットワーク機能などの初期化を行い，それらが終了したらGPIO19をHighにして，復帰が完了したことを測定器に知らせる．測定器はGPIO2をHighにした時間から，GPIO19がHighになった時間までをDeepsleepの復帰にかかった時間としてcsvファイルに記録する．

# ファイル構成
測定器と被測定器のファイル構造は以下の通りである．

```
測定器/
└─boot.py

被測定器/
├─lib
| └─espnow_helper.py
└─boot.py
```

# プログラム紹介
## 測定器
### boot.py
GPIO4をHighにした時間から、GPIO19がHighになった時間までを計測してwake_time.csvに記録する．GPIO19がHighになったときにGPIO4をLowに変更し，任意の時間が経過したあとに，再度GPIO2をHighにする．

## 被測定器
### boot.py
外部ウェイクアップによりDeepsleepから復帰し任意の時間経過したあと，GPIO19をHighにして再度Deepsleepに入る．

### espnow_helper.py
ESPNOWのセットアップとデータの送受信を行う．今回はセットアップのみを使用する．
# 実行結果
## 測定器
以下は測定器のターミナルの出力である。初期化シーケンスのみ表示される。

<img width="664" height="208" alt="image" src="https://github.com/user-attachments/assets/54d92011-d8f9-4dc1-a366-ed2057ce8fdc" />

以下は測定器のwake_time.csvに出力された復帰にかかった時間(ms)である．

![image](https://github.com/cdsl-research/ESP32_measurement_Deepsleep_wakeup_time/blob/master/%E6%B8%AC%E5%AE%9A%E5%99%A8%E3%81%AE%E5%AE%9F%E8%A1%8C%E7%B5%90%E6%9E%9C.png)


## 被測定器
以下は被測定器のターミナルの出力結果である．Deepsleepからの復帰を繰り返しているため，「ets Jun 8 2016 00:22:57」から始まる、初期化シーケンスが並んで表示されている．

![image](https://github.com/cdsl-research/ESP32_measurement_Deepsleep_wakeup_time/blob/master/%E8%A2%AB%E8%A8%88%E6%B8%AC%E5%99%A8%E3%81%AE%E5%AE%9F%E8%A1%8C%E7%B5%90%E6%9E%9C.png)

