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
from readgrib import ReadMSM
import warnings

warnings.filterwarnings('ignore',
                        category=matplotlib.MatplotlibDeprecationWarning)
matplotlib.rcParams['figure.max_open_warning'] = 0
input_dir_default = "retrieve"

# 予報時刻からの経過時間、１時間毎に指定可能
fcst_str = 0
fcst_end = 36
fcst_step = 1

### Start Map Prog ###


def plotmap(fcst_time, sta, lons_1d, lats_1d, lons, lats, rain, tmp, uwnd,
            vwnd, wspd, title, output_filename):
    #
    # MapRegion Classの初期化
    region = MapRegion(sta)
    if sta == "Japan":
        opt_c1 = False
        opt_barbs = False
        bstp = 6
        cstp = 2
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
        cstp = 1
        bstp = 3
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
    # 等温線をひく間隔をlevels1, levels2にリストとして入れる
    # 2度ごとに線をひく
    levels2 = range(math.floor(tmp.min() - math.fmod(tmp.min(), 2)),
                    math.ceil(tmp.max()) + 1, 2)
    # 1度ごとに線をひく
    levels1 = range(math.floor(tmp.min() - math.fmod(tmp.min(), 1)),
                    math.ceil(tmp.max()) + 1, 1)
    # 等温線をひく
    cmap = plt.get_cmap('seismic')  # 色テーブルの選択
    if opt_c1:
        m.contour(lons,
                  lats,
                  tmp,
                  levels=levels1,
                  cmap=cmap,
                  linestyles=':',
                  linewidths=0.8)
    cr = m.contour(lons, lats, tmp, levels=levels2, cmap=cmap, linewidths=0.8)
    clevels = cr.levels
    cr.clabel(clevels[::cstp], fontsize=10, fmt="%d")
    #
    # 降水量の陰影を付ける値をlevelsrにリストとして入れる
    levelsr = [0.2, 1, 5, 10, 20, 50, 80, 100]
    cmap = cm.s3pcpn_l  # 色テーブルの選択
    cmap.set_over('brown')  # 上限を超えた場合の色を指定
    cmap.set_under('gray')  # 下限を下回った場合の色を指定
    # 陰影を描く
    cs = m.contourf(lons, lats, rain, levels=levelsr, cmap=cmap, extend='both')
    #cs=m.contourf(lons_1d,lats_1d,rain,latlon=True,tri=True,levels=levelsr,cmap=cmap,extend='both')
    # カラーバーを付ける
    cbar = m.colorbar(cs, location='bottom', pad="5%")
    cbar.set_label('precipitation (mm/hr)')
    #
    # 矢羽を描く
    if opt_barbs:
        m.barbs(lons[::bstp,::bstp], lats[::bstp,::bstp], \
                uwnd[::bstp,::bstp], vwnd[::bstp,::bstp], \
                color='r', length=4,
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


#   plt.show()

### End Map Prog ###

### utils ###


# convertを使い、pngからgifアニメーションに変換する
def convert_png2gif(input_filenames, delay="80", output_filename="output.gif"):
    args = ["convert", "-delay", delay]
    args.extend(input_filenames)
    args.append(output_filename)
    print(args)
    # コマンドとオプション入出力ファイルのリストを渡し、変換の実行
    res = subprocess.run(args=args,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    print(res.stdout.decode("utf-8"))
    print(res.stderr.decode("utf-8"))


### utils ###

### options ###


# オプションの読み込み
def _construct_parser():
    parser = argparse.ArgumentParser(
        description='Matplotlib Basemap, weather map')

    parser.add_argument('--fcst_date',
                        type=str,
                        help=('forecast date; yyyymmddhhMMss, or ISO date'),
                        metavar='<fcstdate>')
    parser.add_argument('--sta',
                        type=str,
                        help=('Station name; e.g. Japan, Tokyo,,,'),
                        metavar='<sta>')
    parser.add_argument(
        '--input_dir',
        type=str,
        help=
        ('Directory of input files: grib2 (.bin) or NetCDF (.nc); '
         'if --input_dir force_retrieve, download original data from RISH server'
         'if --input_dir retrieve, check avilable download (default)'),
        metavar='<input_dir>')

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
    output_filenames = []
    for fcst_time in np.arange(fcst_str, fcst_end + 1, fcst_step):
        # fcst_timeを設定
        msm.set_fcst_time(fcst_time)
        # NetCDFデータ読み込み
        lons_1d, lats_1d, lons, lats = msm.readnetcdf()
        # 変数取り出し
        # 海面更生気圧を二次元のndarrayで取り出す
        mslp = msm.ret_var("PRMSL_meansealevel", fact=0.01)  # (hPa)
        # 降水量を二次元のndarrayで取り出す
        rain = msm.ret_var("APCP_surface")  # (mm/h)
        # 気温を二次元のndarrayで取り出す (K->℃)
        tmp = msm.ret_var("TMP_1D5maboveground", offset=-273.15)  # (℃)
        # 東西風を二次元のndarrayで取り出す
        uwnd = msm.ret_var("UGRD_10maboveground")  # (m/s)
        # 南北風を二次元のndarrayで取り出す
        vwnd = msm.ret_var("VGRD_10maboveground")  # (m/s)
        wspd = np.sqrt(uwnd**2 + vwnd**2)
        # ファイルを閉じる
        msm.close_netcdf()
        #
        # タイトルの設定
        title = tlab + " forecast, +" + str(fcst_time) + "h"
        # 出力ファイル名の設定
        hh = "{d:02d}".format(d=fcst_time)
        output_filename = "map_msm_stemp_" + sta + "_" + str(hh) + ".png"
        plotmap(fcst_time, sta, lons_1d, lats_1d, lons, lats, rain, tmp, uwnd,
                vwnd, wspd, title, output_filename)
        output_filenames.append(output_filename)
    # gifアニメーションのファイル名
    output_gif_filename = "anim_msm_stemp_" + sta + ".gif"
    # pngからgifアニメーションに変換
    convert_png2gif(input_filenames=output_filenames,
                    delay="80",
                    output_filename=output_gif_filename)
