#!/opt/local/bin/python3
import pandas as pd
import numpy as np
import math
import sys
import subprocess
import argparse
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm
from jmaloc import MapRegion
from readgrib import ReadGSM
from utils import ColUtils
from utils import convert_png2gif
from utils import parse_command
from utils import post
import utils.common

opt_stmp = False  # 等温線を引く（-2、2℃）

### Start Map Prog ###


def plotmap(sta, lons_1d, lats_1d, lons, lats, mslp, rain, tmp, uwnd, vwnd,
            title, output_filename):
    #
    # MapRegion Classの初期化
    region = MapRegion(sta)
    if sta == "Japan":
        opt_c1 = False
        opt_barbs = False
        bstp = 6
        cstp = 1
        mres = "l"
        # 変数を指定(all)
        lon_step = 5
        lon_min = lons_1d.min()
        lon_max = lons_1d.max()
        lat_step = 5
        lat_min = lats_1d.min()
        lat_max = lats_1d.max()
        print(lats_1d.min(), lats_1d.max(), lons_1d.min(), lons_1d.max())
    else:
        opt_c1 = True
        opt_barbs = False
        bstp = 1
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
    fig = plt.figure()
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
    #
    if opt_c1:
        # 等圧線をひく間隔(1hPaごと)をlevelsにリストとして入れる
        levels1 = range(math.floor(mslp.min() - math.fmod(mslp.min(), 2)),
                        math.ceil(mslp.max()) + 1, 1)
        # 等圧線をひく
        cr1 = m.contour(lons,
                        lats,
                        mslp,
                        levels=levels1,
                        colors='k',
                        linestyles=['-', ':'],
                        linewidths=1.2)
        # ラベルを付ける
        cr1.clabel(cr1.levels[::cstp], fontsize=10, fmt="%d")
    else:
        # 等圧線をひく間隔(2hPaごと)をlevelsにリストとして入れる
        levels2 = range(math.floor(mslp.min() - math.fmod(mslp.min(), 2)),
                        math.ceil(mslp.max()) + 1, 2)
        # 等圧線をひく
        cr2 = m.contour(lons,
                        lats,
                        mslp,
                        levels=levels2,
                        colors='k',
                        linewidths=1.2)
        # ラベルを付ける
        cr2.clabel(cr2.levels[::cstp], fontsize=10, fmt="%d")
    #
    if opt_stmp:
        # 等温線をひく
        cr3 = m.contour(lons,
                        lats,
                        tmp,
                        levels=[2],
                        colors='cornflowerblue',
                        linestyles='-',
                        linewidths=0.8)
        cr3.clabel(cr3.levels[::1], fontsize=12, fmt="%d")
        #
        # 等温線をひく
        cr4 = m.contour(lons,
                        lats,
                        tmp,
                        levels=[-2],
                        colors='blue',
                        linestyles='-',
                        linewidths=0.8)
        # ラベルを付ける
        cr4.clabel(cr4.levels[::1], fontsize=12, fmt="%d")
    #
    # 色テーブルの設定
    cutils = ColUtils('s3pcpn_l')  # 色テーブルの選択
    cmap = cutils.get_ctable(under='gray', over='brown')  # 色テーブルの取得
    # 降水量の陰影を付ける値をlevelsrにリストとして入れる
    levelsr = [0.2, 1, 5, 10, 20, 50, 80, 100]
    # 陰影を描く
    cs = m.contourf(lons, lats, rain, levels=levelsr, cmap=cmap, extend='both')
    # カラーバーを付ける
    cbar = m.colorbar(cs, location='bottom', pad="5%")
    cbar.set_label('precipitation (mm/hr)')
    #
    # 矢羽を描く
    if opt_barbs:
        m.barbs(lons[::bstp, ::bstp],
                lats[::bstp, ::bstp],
                uwnd[::bstp, ::bstp],
                vwnd[::bstp, ::bstp],
                color='r',
                length=4,
                sizes=dict(emptybarb=0.01, spacing=0.12, height=0.4))
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
    # ReadGSM初期化
    gsm = ReadGSM(tsel, file_dir, "surf")
    #
    # fcst_timeを変えてplotmapを実行
    output_filenames = []
    for fcst_time in np.arange(fcst_str, fcst_end + 1, fcst_step):
        # fcst_timeを設定
        gsm.set_fcst_time(fcst_time)
        # NetCDFデータ読み込み
        lons_1d, lats_1d, lons, lats = gsm.readnetcdf()
        # 変数取り出し
        # 海面更生気圧を二次元のndarrayで取り出す
        mslp = gsm.ret_var("PRMSL_meansealevel", fact=0.01)  # (hPa)
        # 累積降水量を二次元のndarrayで取り出す
        rain = gsm.ret_var("APCP_surface")  # (mm/h)
        # 気温を二次元のndarrayで取り出す (K->℃)
        tmp = gsm.ret_var("TMP_2maboveground", offset=-273.15)  # (℃)
        # 東西風を二次元のndarrayで取り出す
        uwnd = gsm.ret_var("UGRD_10maboveground")  # (m/s)
        # 南北風を二次元のndarrayで取り出す
        vwnd = gsm.ret_var("VGRD_10maboveground")  # (m/s)
        # ファイルを閉じる
        gsm.close_netcdf()
        #
        # タイトルの設定
        title = tlab + " forecast, +" + str(fcst_time) + "h"
        # 出力ファイル名の設定
        hh = "{d:02d}".format(d=fcst_time)
        output_filename = "map_gsm_mslp_" + sta + "_" + str(hh) + ".png"
        # 作図
        plotmap(sta, lons_1d, lats_1d, lons, lats, mslp, rain, tmp, uwnd, vwnd,
                title, output_filename)
        output_filenames.append(output_filename)
    # pngからgifアニメーションに変換
    convert_png2gif(input_filenames=output_filenames,
                    delay="80",
                    output_filename="anim_gsm_mslp_" + sta + ".gif")
    # 後処理
    post(output_filenames)
