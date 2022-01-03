#!/opt/local/bin/python3
import pandas as pd
import numpy as np
import math
import sys
from datetime import timedelta
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from jmaloc import MapRegion
from readgrib import ReadGSM
from utils import ColUtils
from utils import parse_command
from utils import post
import utils.common

### Start Map Prog ###


def plotmap(sta, lons_1d, lats_1d, lons, lats, mslp, rain, title,
            output_filename):
    #
    # MapRegion Classの初期化
    region = MapRegion(sta)
    if sta == "Japan":
        opt_c1 = False
        cstp = 1
        mres = "l"
        # 変数を指定(all)
        lon_step = region.lon_step
        lon_min = lons_1d.min()
        lon_max = lons_1d.max()
        lat_step = region.lat_step
        lat_min = lats_1d.min()
        lat_max = lats_1d.max()
        print(lats_1d.min(), lats_1d.max(), lons_1d.min(), lons_1d.max())
    else:
        opt_c1 = True
        cstp = 2
        mres = "h"
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
    # 等圧線をひく
    if opt_c1:
        # 等圧線をひく間隔(1hPaごと)をlevelsにリストとして入れる
        levels1 = range(math.floor(mslp.min() - math.fmod(mslp.min(), 1)),
                        math.ceil(mslp.max()) + 1, 2)
        cr1 = m.contour(lons,
                        lats,
                        mslp,
                        levels=levels1,
                        colors='k',
                        linestyles=['-', ':'],
                        linewidths=1.2)
        # ラベルを付ける
        cr1.clabel(cr1.levels[::cstp], fontsize=12, fmt="%d")
    else:
        # 等圧線をひく間隔(2hPaごと)をlevelsにリストとして入れる
        levels2 = range(math.floor(mslp.min() - math.fmod(mslp.min(), 2)),
                        math.ceil(mslp.max()) + 1, 2)
        cr2 = m.contour(lons,
                        lats,
                        mslp,
                        levels=levels2,
                        colors='k',
                        linewidths=1.2)
        # ラベルを付ける
        cr2.clabel(cr2.levels[::cstp], fontsize=12, fmt="%d")
    #
    # 色テーブルの設定
    cutils = ColUtils('wysiwyg')  # 色テーブルの選択
    cmap = cutils.get_ctable(under='gray', over='r')  # 色テーブルの取得
    # 降水量の陰影を付ける値をlevelsrにリストとして入れる
    levelsr = [1, 5, 10, 20, 50, 80, 100, 200, 400, 600]
    # 陰影を描く
    cs = m.contourf(lons, lats, rain, levels=levelsr, cmap=cmap, extend='both')
    # カラーバーを付ける
    cbar = m.colorbar(cs, location='bottom', pad="5%")
    cbar.set_label('precipitation (mm)')
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
    # 予報時刻からの経過時間
    fcst_time = args.fcst_time
    # datetimeに変換
    tinfo = pd.to_datetime(fcst_date)
    #
    tsel = tinfo.strftime("%Y%m%d%H%M%S")
    tlab = tinfo.strftime("%m/%d %H UTC")
    #
    # ReadGSM初期化
    gsm = ReadGSM(tsel, file_dir, "surf")
    #
    # fcst_timeを設定
    gsm.set_fcst_time(fcst_time)
    # NetCDFデータ読み込み
    lons_1d, lats_1d, lons, lats = gsm.readnetcdf()
    # 変数取り出し
    # 海面更生気圧を二次元のndarrayで取り出す
    mslp = gsm.ret_var("PRMSL_meansealevel", fact=0.01)  # (hPa)
    # 累積降水量を二次元のndarrayで取り出す
    rain = gsm.ret_var("APCP_surface", cum_rain=True)  # (mm/h)
    # ファイルを閉じる
    gsm.close_netcdf()
    #
    # タイトルの設定
    title = tlab + " GSM forecast, +" + "0-" + str(
        fcst_time) + "h rain & +" + str(fcst_time) + "h SLP"
    # 出力ファイル名の設定
    output_filename = "map_gsm_rain_sum" + "0-" + str(
        fcst_time) + "_" + sta + ".png"
    # 作図
    plotmap(sta, lons_1d, lats_1d, lons, lats, mslp, rain, title,
            output_filename)
