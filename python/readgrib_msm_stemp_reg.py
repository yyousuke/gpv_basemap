#!/opt/local/bin/python3
import pandas as pd
import numpy as np
import math
import sys
from datetime import timedelta
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm
from jmaloc import MapRegion
from readgrib import ReadMSM
from utils import ColUtils
from utils import convert_png2gif
from utils import parse_command
from utils import post
import utils.common

### Start Map Prog ###


def plotmap(sta, lons_1d, lats_1d, lons, lats, tmp, rain, title,
            output_filename):
    """作図を行う
    
    Parameters:
    ----------
    sta: str
        地点名 
    lons_1d: str
        経度データ（1次元、度）
    lats_1d: ndarray
        緯度データ（1次元、度）
    lons: ndarray
        経度データ（2次元、度）
    lats: ndarray
        緯度データ（2次元、度）
    tmp: ndarray
        気温データ（2次元、K）
    rain: ndarray
        降水量データ（2次元、mm/hr）
    title: str
        タイトル
    output_filename: str
        出力ファイル名 
    ----------
    """
    #
    # MapRegion Classの初期化
    region = MapRegion(sta)
    if sta == "Japan":
        opt_c1 = False  # 1Kの等温線を描かない
        cstp = 1  # # 等値線ラベルを何個飛ばしに付けるか
        mres = "l"  # 地図の解像度
        # 変数を指定(all)
        lon_step = region.lon_step
        lon_min = lons_1d.min()
        lon_max = lons_1d.max()
        lat_step = region.lat_step
        lat_min = lats_1d.min()
        lat_max = lats_1d.max()
        print(lats_1d.min(), lats_1d.max(), lons_1d.min(), lons_1d.max())
    else:
        opt_c1 = True  # 1Kの等温線を描く
        cstp = 2  # # 等値線ラベルを何個飛ばしに付けるか
        mres = "h"  # 地図の解像度
        # Map.regionの変数を取得
        lon_step = region.lon_step
        lon_min = region.lon_min
        lon_max = region.lon_max
        lat_step = region.lat_step
        lat_min = region.lat_min
        lat_max = region.lat_max

    # マップを作成
    fig = plt.figure(figsize=(10, 10))
    # 最初の4つのパラメータは描画する範囲の指定、最後は解像度
    m = Basemap(llcrnrlon=lon_min,
                urcrnrlon=lon_max,
                llcrnrlat=lat_min,
                urcrnrlat=lat_max,
                resolution=mres)
    #
    # 緯度線、経度線を引く
    m.drawmeridians(np.arange(0, 360, lon_step),
                    color="k",
                    fontsize='small',
                    labels=[False, False, False, True])
    m.drawparallels(np.arange(-90, 90, lat_step),
                    color="k",
                    fontsize='small',
                    labels=[True, False, False, False])
    #
    # 陸地に色を付ける
    #m.fillcontinents(color='gray')
    #m.fillcontinents(color='gray',lake_color='aqua')
    #
    # 等温線をひく
    cmap = plt.get_cmap('seismic')  # 色テーブルの選択
    if opt_c1:
        # 等温線をひく間隔(1度)をにリストとして入れる
        levels1 = range(math.floor(tmp.min() - math.fmod(tmp.min(), 2)),
                        math.ceil(tmp.max()) + 1, 1)
        cr1 = m.contour(lons,
                        lats,
                        tmp,
                        levels=levels1,
                        cmap=cmap,
                        linestyles=['-', ':'],
                        linewidths=0.8)
        cr1.clabel(cr1.levels[::cstp], fontsize=10, fmt="%d")
    else:
        # 等温線をひく間隔(2度)をにリストとして入れる
        levels2 = range(math.floor(tmp.min() - math.fmod(tmp.min(), 2)),
                        math.ceil(tmp.max()) + 1, 2)
        cr2 = m.contour(lons,
                        lats,
                        tmp,
                        levels=levels2,
                        cmap=cmap,
                        linewidths=0.8)
        cr2.clabel(cr2.levels[::cstp], fontsize=10, fmt="%d")
    #
    # 色テーブルの設定
    cutils = ColUtils('s3pcpn_l')  # 色テーブルの選択
    cmap = cutils.get_ctable(under='gray', over='brown')  # 色テーブルの取得
    # 降水量の陰影を付ける値をlevelsrにリストとして入れる
    levelsr = [0.2, 1, 5, 10, 20, 50, 80, 100]
    # 陰影を描く
    cs = m.contourf(lons, lats, rain, levels=levelsr, cmap=cmap, extend='both')
    #cs=m.contourf(lons_1d,lats_1d,rain,latlon=True,tri=True,levels=levelsr,cmap=cmap,extend='both')
    # カラーバーを付ける
    cbar = m.colorbar(cs, location='bottom', pad="5%")
    cbar.set_label('precipitation (mm/hr)')
    #
    # 海岸線を描く
    m.drawcoastlines()
    #
    # タイトルを付ける
    plt.title(title)
    # 図を保存
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()


### End Map Prog ###

if __name__ == '__main__':
    # オプションの読み込み
    args = parse_command(sys.argv)
    # 予報時刻, 作図する地域の指定
    fcst_date = args.fcst_date
    sta = args.sta
    file_dir = args.input_dir
    # 予報時刻からの経過時間（１時間毎に指定可能）
    fcst_end = args.fcst_time
    fcst_str = 0  # 開始時刻
    fcst_step = 1  # 作図する間隔
    # datetimeに変換
    tinfo = pd.to_datetime(fcst_date)
    #
    tsel = tinfo.strftime("%Y%m%d%H%M%S")
    tlab = tinfo.strftime("%m/%d %H UTC")
    #
    # ReadMSM初期化
    msm = ReadMSM(tsel, file_dir, "surf")
    #
    # fcst_timeを変えてplotmapを実行
    output_filenames = []
    for fcst_time in np.arange(fcst_str, fcst_end + 1, fcst_step):
        # fcst_timeを設定
        msm.set_fcst_time(fcst_time)
        # fcst時刻
        tinfo_fcst = tinfo + timedelta(hours=int(fcst_time))
        tlab_fcst = tinfo_fcst.strftime("%m/%d %H UTC")
        # NetCDFデータ読み込み
        lons_1d, lats_1d, lons, lats = msm.readnetcdf()
        # 変数取り出し
        # 降水量を二次元のndarrayで取り出す
        rain = msm.ret_var("APCP_surface")  # (mm/h)
        # 気温を二次元のndarrayで取り出す (K->℃)
        tmp = msm.ret_var("TMP_1D5maboveground", offset=-273.15)  # (℃)
        # ファイルを閉じる
        msm.close_netcdf()
        #
        # タイトルの設定
        title = tlab + " MSM forecast, +" + str(
            fcst_time) + "h (" + tlab_fcst + ")"
        # 出力ファイル名の設定
        hh = "{d:02d}".format(d=fcst_time)
        output_filename = "map_msm_stemp_" + sta + "_" + str(hh) + ".png"
        plotmap(sta, lons_1d, lats_1d, lons, lats, tmp, rain, title,
                output_filename)
        output_filenames.append(output_filename)
    # pngからgifアニメーションに変換
    convert_png2gif(input_filenames=output_filenames,
                    delay="80",
                    output_filename="anim_msm_stemp_" + sta + ".gif")
    # 後処理
    post(output_filenames)
