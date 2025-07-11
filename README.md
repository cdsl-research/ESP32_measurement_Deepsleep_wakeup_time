# 用途・目的
これらのファイルは，ESP32のDeepsleepからの復帰にかかる時間を計測するためのプログラムである．時間を測定するESP32(測定器)にboot.pyを実装し、測定されるESP32(被測定器)にmain.pyとespnow_helper.pyを実装する．これらのプログラムについて説明する．外部ウェイクアップを使用して，測定器がPin19をHighにすると，被測定器がDeepsleepから復帰する．復帰後，ネットワーク機能などの初期化を行い，それらが終了したらPin23をHighにして，復帰が完了したことを測定器に知らせる．測定器はPin19をHighにした時間から，Pin23がHighになった時間までをDeepsleepの復帰にかかった時間としてcsvファイルに記録する．

# ファイル構成
測定器ではルートディレクトリにboot.pyを置く．被測定機ではルートディレクトリにmain.pyを置き，libディレクトリ内にespnow_helper.pyを置く．

# プログラム紹介
## boot.py
Pin19をHighにした時間から、Pin23がHighになった時間までを計測してcsvファイルに記録する．Pin23がHighになったときにPin19をLowに変更し，任意の時間が経過したあとに，再度Pin19をHighにする．

## main.py
外部ウェイクアップによりDeepsleepから復帰し任意の時間経過したあと，Pin23をHighにして再度Deepsleepに入る．

## espnow_helper.py
ESPNOWのセットアップとデータの送受信を行う．今回はセットアップのみを使用する．
# 実行結果
## 測定器
以下はcsvファイルに出力された復帰にかかった時間(ms)である．

![image](https://github.com/cdsl-research/ESP32_measurement_Deepsleep_wakeup_time/blob/master/%E6%B8%AC%E5%AE%9A%E5%99%A8%E3%81%AE%E5%AE%9F%E8%A1%8C%E7%B5%90%E6%9E%9C.png)

## 被測定器
以下はターミナルの出力結果である．Deepsleepからの復帰を繰り返しているため，初期化シーケンスが並んで表示されている．

![image](https://github.com/cdsl-research/ESP32_measurement_Deepsleep_wakeup_time/blob/master/%E8%A2%AB%E6%B8%AC%E5%AE%9A%E5%99%A8%E3%81%AE%E5%AE%9F%E8%A1%8C%E7%B5%90%E6%9E%9C.png)

