# gpv_basemap

気象庁数値予報GPVデータを取得し、cartopyで作図する。データは京都大学生存圏研究所（RISH）のサーバから取得する。データ利用時の注意事項等については、RISHのページ（http://database.rish.kyoto-u.ac.jp/arch/jmadata/）参照のこと。

./main.py：手動で./python/以下の全プログラムを実行する場合

./main_auto.py：自動で./python/以下の全プログラムを実行する場合（crontabに登録した場合など。5時間前の予報時刻のデータを取得）

作図プログラムは./python/*.py：これらのファイルは個別実行も可能

# オプション
--fcst_date 予報時刻

--sta 作図する地域

--input_dir 入力ファイルを置いたディレクトリ、または、retrieve(デフォルト)、force_retrieve

--fcst_time 何時間先までの予報データを作図するか

--lev 作図する気圧面（気圧面データのみ）

# 予報時刻の指定：--fcst_date
"20180902210000" （UTC） 、または、"2018-01-21 00:00:00"（UTC、ISO形式）


# 作図する地域の指定：--sta
指定可能なものは以下

"Japan"  全国、"Rumoi" 北海道（北西部）、"Abashiri" 北海道（東部）、"Sapporo" 北海道（南西部）、"Akita" 東北地方（北部）、"Sendai" 東北地方（南部）、"Tokyo" 関東地方、"Kofu" 甲信地方、"Niigata" 北陸地方（東部）、"Kanazawa" 北陸地方（西部）、"Nagoya" 東海地方、"Osaka" 近畿地方、"Okayama" 中国地方、"Kochi" 四国地方、"Fukuoka" 九州地方（北部）、"Kagoshima" 九州地方（南部）、"Naze" 奄美地方、"Naha" 沖縄本島地方、"Daitojima"   大東島地方、"Miyakojima" 宮古・八重山地方


# 入力するファイルを置いたディレクトリ：--input_dir 
指定可能なものは以下

--input_dir ディレクトリへのpath

--input_dir force_retrieve：gribデータをRISHサーバからダウンロード

--input_dir retrieve：ファイルが存在しない場合には、gribデータをRISHサーバからダウンロード（デフォルト）

入力ファイルはRISHサーバからダウンロードしたgrib2ファイル、または、
wgrib2 入力ファイル.bin -netcdf 出力ファイル.nc
で変換したNetCDFファイル


ダウンロードしたファイルを置いたディレクトリを、DATADIR_GPVという環境変数にしておくこともできる。
export DATADIR_GPV=${HOME}/Downloads


# 作図する予報時刻最大値：--fcst_time
整数で指定する（デフォルト36）。
 
 
# 作図する気圧面：--lev
指定可能な気圧面は以下

1000、975、950、925、900、850、800、700、600、500、400、300、250、200、150、100
 
 
