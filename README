
./main.py：手動でpython以下の全プログラムを実行する場合

./main_auto.py：crontabに登録した場合など。自動でpython以下の全プログラムを実行する場合(5時間前の予報時刻のデータを取得)


./python/*.py
--fcst_date 予報時刻
--sta 作図する地域
--input_dir 入力ファイルを置いたディレクトリ、またはretrieve(デフォルト)、force_retrieve


# 予報時刻の指定 --fcst_date
#fcst_date = "20180902210000" # UTC , or "2018-01-21 00:00:00" # UTC (ISO)
#
# 作図する地域の指定 --sta
#sta="Japan" # all
#sta="Rumoe" # 北海道（北西部）
#sta="Abashiri" # 北海道（東部）
#sta="Sapporo" # 北海道（南西部）
#sta="Akita" # 東北地方（北部）
#sta="Sendai" # 東北地方（南部）
#sta="Tokyo" # 関東地方
#sta="Kofu" # 甲信地方
#sta="Niigata" # 北陸地方（東部）
#sta="Kanazawa" # 北陸地方（西部）
#sta="Nagoya" # 東海地方
#sta="Osaka" # 近畿地方
#sta="Okayama" # 中国地方
#sta="Kochi" # 四国地方
#sta="Fukuoka" # 九州地方（北部）
#sta="Kagoshima" # 九州地方（南部）
#sta="Naze" # 奄美地方
#sta="Naha" # 沖縄本島地方
#sta="Daitojima" #  大東島地方
#sta="Miyakojima" # 宮古・八重山地方


# 入力するファイルを置いたディレクトリ
--input_dir ディレクトリへのpath：
--input_dir force_retrievem：gribデータをRISHサーバからダウンロード
--input_dir retrievem：ファイルが存在しない場合には、gribデータをRISHサーバからダウンロード（デフォルト）

入力ファイルはRISHサーバからダウンロードしたgrib2ファイル、または、
wgrib2 入力ファイル.bin -netcdf 出力ファイル.nc
で変換したNetCDFファイル


ダウンロードしたファイルを置いたディレクトリを、DATADIR_MSMという環境変数にしておくこともできる。
export DATADIR_MSM=${HOME}/Downloads

