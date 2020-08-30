#!/opt/local/bin/python3
import pandas as pd
import numpy as np
import math
import sys
import os
import subprocess
import argparse
import urllib.request
import netCDF4
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm
from jmaloc import MapRegion
from readgrib import ReadMSM
import warnings
warnings.filterwarnings('ignore', category=matplotlib.MatplotlibDeprecationWarning)
matplotlib.rcParams['figure.max_open_warning'] = 0
input_dir_default = "retrieve"

# 予報時刻からの経過時間、１時間毎に指定可能
fcst_str = 0
fcst_end = 36
fcst_step = 1
#

### Start Map Prog ###

def plotmap(fcst_time, sta, lons_1d, lats_1d, lons, lats, mslp, rain, title, output_filename):
    #
    # MapRegion Classの初期化
    region = MapRegion(sta)
    if sta == "Japan":
        opt_c1 = False
        cstp = 2
        mres = "l"
        # 変数を指定(all)
        lon_step = 5
        lon_min  = lons_1d.min()
        lon_max  = lons_1d.max()
        lat_step = 5
        lat_min  = lats_1d.min()
        lat_max  = lats_1d.max()
        print(lats_1d.min(), lats_1d.max(), lons_1d.min(), lons_1d.max())
    else:
        opt_c1 = True
        cstp = 1
        mres = "h"
        # Map.regionの変数を取得
        lon_step = region.lon_step
        lon_min  = region.lon_min
        lon_max  = region.lon_max
        lat_step = region.lat_step
        lat_min  = region.lat_min
        lat_max  = region.lat_max

    # マップを作成
    fig = plt.figure()
    # 最初の4つのパラメータは描画する範囲の指定、最後は解像度
    m = Basemap(llcrnrlon=lon_min, urcrnrlon=lon_max, llcrnrlat=lat_min, urcrnrlat=lat_max, resolution=mres)
    #
    # 緯度線、経度線を引く
    m.drawmeridians(np.arange(0, 360, lon_step), color="k", fontsize='small', 
        labels=[False,False,False,True])
    m.drawparallels(np.arange(-90, 90, lat_step), color="k", fontsize='small', 
        labels=[True,False,False,False])
    # 
    # 等圧線をひく間隔をlevelsにリストとして入れる
    # 2hPaごとに線をひく
    levels = range(math.floor(mslp.min()-math.fmod(mslp.min(),2)), math.ceil(mslp.max())+1,2)
    # 1hPaごとに線をひく
    levels1 = range(math.floor(mslp.min()-math.fmod(mslp.min(),1)), math.ceil(mslp.max())+1,1)
    # 等圧線をひく
    if opt_c1:
        m.contour(lons, lats, mslp, levels=levels1, colors='k', linestyles=':', linewidths=0.8)
        #m.contour(lons_1d, lats_1d, mslp, latlon=True, tri=True, levels=levels1, colors='k', linestyles=':', linewidths=0.8)
    cr = m.contour(lons, lats, mslp, levels=levels, colors='k', linewidths=0.8)
    #cr = m.contour(lons_1d, lats_1d, mslp, latlon=True, tri=True, levels=levels, colors='k', linewidths=0.8)
    # ラベルを付ける
    clevels = cr.levels
    cr.clabel(clevels[::cstp], fontsize=12, fmt="%d")
    #    
    # 
    # 降水量の陰影を付ける値をlevelsrにリストとして入れる
    levelsr = [1, 5, 10, 20, 50, 80, 100, 200, 400, 600]
    cmap = cm.GMT_wysiwyg # 色テーブルの選択
    cmap.set_over('r') # 上限を超えた場合の色を指定
    cmap.set_under('gray') # 下限を下回った場合の色を指定
    # 陰影を描く
    cs = m.contourf(lons, lats, rain, levels=levelsr, cmap=cmap, extend='both')
    #cs=m.contourf(lons_1d,lats_1d,rain,latlon=True,tri=True,levels=levelsr,cmap=cmap,extend='both')
    # カラーバーを付ける
    cbar = m.colorbar(cs,location='bottom', pad="5%")
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
#   plt.show()

### End Map Prog ###


### options ###

# オプションの読み込み
def _construct_parser():
    parser = argparse.ArgumentParser(description='Matplotlib Basemap, weather map')

    parser.add_argument(
        '--fcst_date',
        type=str,
        help=('forecast date; yyyymmddhhMMss, or ISO date'),
        metavar='<fcstdate>'
    )
    parser.add_argument(
        '--sta',
        type=str,
        help=('Station name; e.g. Japan, Tokyo,,,'),
        metavar='<sta>'
    )
    parser.add_argument(
        '--input_dir',
        type=str,
        help=('Directory of input files: grib2 (.bin) or NetCDF (.nc); '
               'if --input_dir force_retrieve, download original data from RISH server' 
               'if --input_dir retrieve, check avilable download (default)' ),
        metavar='<input_dir>'
    )

    return parser

def _parse_command(args):
    parser = _construct_parser()
    parsed_args = parser.parse_args(args[1:])
    if parsed_args.input_dir is None:
        parsed_args.input_dir = input_dir_default
    return parsed_args

### options ###


if __name__ == '__main__':
    # オプションの読み込み
    args = _parse_command(sys.argv)
    # 予報時刻, 作図する地域の指定
    fcst_date = args.fcst_date
    sta = args.sta
    file_dir = args.input_dir
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
    rain_add = []
    for fcst_time in np.arange(fcst_str, fcst_end+1, fcst_step):
        # fcst_timeを設定
        msm.set_fcst_time(fcst_time)
        # NetCDFデータ読み込み
        lons_1d, lats_1d, lons, lats = msm.readnetcdf()
        # 変数取り出し
        # 海面更生気圧を二次元のndarrayで取り出す
        mslp = msm.ret_var("PRMSL_meansealevel", fact=0.01) # (hPa)
        # 降水量を二次元のndarrayで取り出す
        rain = msm.ret_var("APCP_surface") # (mm/h)
        rain_add.append(rain)
        # ファイルを閉じる
        msm.close_netcdf()
    #
    #
    nt = len(rain_add)
    rain_add = np.vstack(rain_add).reshape(nt, lons.shape[0], lons.shape[1])
    print(rain_add.shape)
    rain = rain_add.sum(axis=0)
    #
    # タイトルの設定
    title = tlab + " forecast, +" + str(fcst_str) + "-" + str(fcst_end) + "h rain & +"  + str(fcst_end) + "h SLP"
    # 出力ファイル名の設定
    output_filename = "map_msm_rain_sum" + str(fcst_str) + "-" + str(fcst_end) + "_" + sta + ".png"
    plotmap(fcst_time, sta, lons_1d, lats_1d, lons, lats, mslp, rain, title, output_filename)

