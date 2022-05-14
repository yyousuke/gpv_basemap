# gpv_basemap

気象庁数値予報GPVデータを取得し、cartopyで作図する。データは京都大学生存圏研究所（RISH）のサーバから取得する。データ利用時の注意事項等については、[RISHのページ](http://database3.rish.kyoto-u.ac.jp/arch/jmadata/ "京都大学生存圏研究所")参照のこと。

## 制御プログラム

- **main.py**：手動で./python/以下の全プログラムを実行する場合

    opt_gsm = TrueとするとGSMデータも作図する（00, 06, 12, 18UTCのみ）

    stationsで作図地域を指定する

- **main_auto.py**：自動で./python/以下の全プログラムを実行する場合（crontabに登録して実行する場合などを想定。デフォルトでは、5時間前の予報時刻のデータを取得）

## 作図プログラム

./python/*.py：制御プログラムから実行される。個別実行も可能

- **readgrib_gsm_ccover_reg.py**：GSMデータから下層・中層・上層雲量と海面気圧を描く

- **readgrib_gsm_mslp_reg.py**：GSMデータから海面気圧と前1時間降水量を描く

- **readgrib_gsm_rain_sum_reg.py**：GSMデータから積算降水量を描く

- **readgrib_gsm_stemp_reg.py**：GSMデータから地表気温と降水量を描く

- **readgrib_gsm_tvar_reg.py**：GSMデータからアメダス地点近傍の時系列図を描く

- **readgrib_msm_ccover_reg.py**：MSMデータから下層・中層・上層雲量と海面気圧を描く

- **readgrib_msm_mslp_reg.py**：MSMデータから海面気圧と前1時間降水量を描く

- **readgrib_msm_rain_sum_reg.py**：MSMデータから積算降水量を描く

- **readgrib_msm_stemp_reg.py**：MSMデータから地表気温と降水量を描く

- **readgrib_msm_ept_reg.py**：MSMデータから850 hPa等相当温位と安定度を描く

- **readgrib_msm_temp_reg.py**：MSMデータから指定気圧面の温度と相対湿度、風向・風速を描く

- **readgrib_msm_tvar_reg.py***：MSMデータからアメダス地点近傍の時系列図を描く

### 作図プログラムオプション

- **--fcst_date** <予報時刻UTCの文字列>：YYYYMMDDHHMMSSの形式またはISO形式

    2018年1月21日00UTCを予報時刻とする例：--fcst_date 20180902210000
    
    ISO形式で指定する場合には、--fcst_date "2018-01-21 00:00:00"

- **--sta** <作図する地域の文字列>：指定可能なものは以下

    "Japan"  全国、"Rumoi" 北海道（北西部）、"Abashiri" 北海道（東部）、"Sapporo" 北海道（南西部）、"Akita" 東北地方（北部）、"Sendai" 東北地方（南部）、"Tokyo" 関東地方、"Kofu" 甲信地方、"Niigata" 北陸地方（東部）、"Kanazawa" 北陸地方（西部）、"Nagoya" 東海地方、"Osaka" 近畿地方、"Okayama" 中国地方、"Kochi" 四国地方、"Fukuoka" 九州地方（北部）、"Kagoshima" 九州地方（南部）、"Naze" 奄美地方、"Naha" 沖縄本島地方、"Daitojima"   大東島地方、"Miyakojima" 宮古・八重山地方

- **--fcst_time** <整数値>（デフォルト36）： 何時間先までの予報データを作図するか、または、何時間積算値を作図するか（降水量の場合）

- **--lev** <整数値>：作図する気圧面をhPaで（readgrib_msm_temp_reg.pyのみ、デフォルト値：850）

    指定可能な気圧面は以下

    1000、975、950、925、900、850、800、700、600、500、400、300、250、200、150、100
 
- **--input_dir** <文字列>：入力ファイルを置いたディレクトリ、または、retrieve(デフォルト)、force_retrieveのいずれかを指定する

    --input_dir ディレクトリへのpath：指定したディレクトリから読み込み

    --input_dir retrieve：ファイルが存在しない場合には、gribデータをRISHサーバからダウンロード（デフォルト）
    
    --input_dir force_retrieve：ファイルが存在している場合にも、gribデータをRISHサーバからダウンロード

    入力ファイルはRISHサーバからダウンロードしたgrib2ファイル、または、wgrib2 入力ファイル.bin -netcdf 出力ファイル.ncで変換したNetCDFファイル

    ＊ダウンロードしたファイルを置いたディレクトリを、DATADIR_GPVという環境変数に格納しておくと、そのディレクトリにあるファイルを読みにいく。

    % export DATADIR_GPV=${HOME}/Downloads

### デバッグモード

- **-python/readgrib/__init__.py** GRIB2データ読み込み

    デバッグモードにする場合、コード内で`verbose = True`とする

## 変換プログラム

- **grib2nc_msm_3d.py***：MSMデータの3次元データをNetCDFデータに変換

### 変換プログラムオプション

- **--fcst_date** <予報時刻UTCの文字列>：YYYYMMDDHHMMSSの形式またはISO形式

    2018年1月21日00UTCを予報時刻とする例：--fcst_date 20180902210000
    
    ISO形式で指定する場合には、--fcst_date "2018-01-21 00:00:00"

### デバッグモード

- **-python/grib2nc_msm_3d.py** GRIB2データからNetCDFデータに変換するスクリプト

    デバッグモードにする場合、コード内で`verbose = True`とする

## エラー

次のようなSSL証明書のエラーが発生する場合
    
    urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired (_ssl.c:1129)>

https://database3.rish.kyoto-u.ac.jp/arch/jmadata/data/gpv/original にアクセスして、SSL証明書が期限切れになっていることを確認する。
`python/readgrib/__init__.py`の最初に、次のようなコードを加える（セキュリティ上は安全とは言えないので、一時的に回避したい場合に行う）

    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    
