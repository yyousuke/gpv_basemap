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
warnings.filterwarnings('ignore', category=matplotlib.MatplotlibDeprecationWarning)
matplotlib.rcParams['figure.max_open_warning'] = 0
input_dir_default = "retrieve"

# 予報時刻からの経過時間、３時間毎に指定可能
fcst_str = 0
fcst_end = 36
fcst_step = 3
#

#######################################################################
#
def mktheta(pres, tem, rh):
    Rd = 287.04 # gas constant of dry air [J/K/kg]
    Rv = 461.50 # gas constant of water vapor [J/K/kg]
    es0 = 610.7 # Saturate pressure of water vapor at 0C [Pa]
    Lq = 2.5008e6 # latent heat for evapolation at 0C [kg/m3]
    emelt = 3.40e5 # Latent heat of melting [kg/m3]
    Tqice = 273.15 #  Wet-bulb temp. rain/snow [K]
    Tmelt = 273.15 # Melting temperature of water [K]
    Cp = 1004.6 # specific heat at constant pressure of air (J/K/kg)
    p00 = 100000.0 # reference pressure 1000 [hPa]
    # pres [Pa], tem [K], rh [%]
    # 飽和比湿を求める
    qs = (Rd / Rv * es0 / pres) \
       * np.exp( (Lq + emelt / 2.0 * (1.0 - np.sign(tem - Tqice)) ) \
                       / Rv * (1.0 / Tmelt - 1.0 / tem) )
    # 比湿を求める
    q = qs * rh * 0.01
    # 相当温位を求める
    the = (tem + Lq/Cp * q) * np.power(p00/pres, Rd/Cp)
    # 飽和相当温位を求める
    thes = (tem + Lq/Cp * qs) * np.power(p00/pres, Rd/Cp)
    return(the, thes)
#
# rh = q/qs*100 [%]
# thetae = (tmp + EL/CP * q) * (p00 / p)**(Rd/Cp)
#
# ECMWF
# qs = Rd/Rv*es0/p*exp[ 
#       (Lq+emelt/2.0*(1.0-sign(1.0,T-Tqice)))
#       /Rv*(1.0/Tmelt-1.0/T)]
#
# 
#######################################################################


### Start Map Prog ###


# netCDFファイルを読み込む
def readnetcdf(msm_dir, fcst_time, tsel):
    if fcst_time <= 15:
        fcst_flag="00-15"
        rec_num = fcst_time // 3
    elif fcst_time <= 33:
        fcst_flag="18-33"
        rec_num = (fcst_time - 18) // 3
    else:
        fcst_flag="36-39"
        rec_num = (fcst_time - 36) // 3
    # ファイル名
    file_name_g2 = "Z__C_RJTD_"+str(tsel)+"_MSM_GPV_Rjp_L-pall_FH"+str(fcst_flag)+"_grib2.bin"
    file_name_nc = "Z__C_RJTD_"+str(tsel)+"_MSM_GPV_Rjp_L-pall_FH"+str(fcst_flag)+"_grib2.nc"
    #
    if msm_dir == "retrieve":
        file_dir_name = ret_grib(tsel, file_name_g2, file_name_nc, force=False)
    elif msm_dir == "force_retrieve":
        file_dir_name = ret_grib(tsel, file_name_g2, file_name_nc, force=True)
        msm_dir = "retrieve"
    else:
        file_dir_name = msm_dir + "/" + file_name_nc
    #
    # NetCDFデータの読み込み
    nc = netCDF4.Dataset(file_dir_name, 'r')
    # データサイズの取得
    idim = len(nc.dimensions['longitude'])
    jdim = len(nc.dimensions['latitude'])
    num_rec = len(nc.dimensions['time'])
    print("num_lon =", idim, ", num_lat =", jdim, ", num_time =", num_rec)
    # 変数の読み込み(一次元)
    lons_1d = nc.variables["longitude"][:]
    lats_1d = nc.variables["latitude"][:]
    time = nc.variables["time"][:]
    # lons, lats: 二次元配列に変換
    lons, lats = np.meshgrid(lons_1d, lats_1d)
    #
    # 850 hPa 気温データを二次元のndarrayで取り出す
    t85 = nc.variables["TMP_850mb"][rec_num] # (K)
    # 500 hPa 気温データを二次元のndarrayで取り出す
    t50 = nc.variables["TMP_500mb"][rec_num] # (K)
    #
    # 850 hPa 相対湿度データを二次元のndarrayで取り出す
    rh85 = nc.variables["RH_850mb"][rec_num] # ()
    # 500 hPa 相対湿度データを二次元のndarrayで取り出す
    rh50 = nc.variables["RH_500mb"][rec_num] # ()
    # 500 hPa ジオポテンシャル高度データを二次元のndarrayで取り出す
    z50 = nc.variables["HGT_500mb"][rec_num] # (m)

    #
    # ファイルを閉じる
    nc.close()
    print("lon:", lons.shape)
    print("lat:", lats.shape)
    print("z50:", z50.shape)
    return lons_1d, lats_1d, lons, lats, z50, the85, the50, dthdz
    

def plotmap(fcst_time, sta, lons_1d, lats_1d, lons, lats, z50, the85, the50, dthdz, title, output_filename):
    #
    # MapRegion Classの初期化
    region = MapRegion(sta)
    if sta == "Japan":
        cstp = 5         # 等温位線ラベルを何個飛ばしに付けるか
        mres = "l"       # 地図の解像度
        # 変数を指定(all)
        lon_step = 5
        lon_min  = lons_1d.min()
        lon_max  = lons_1d.max()
        lat_step = 5
        lat_min  = lats_1d.min()
        lat_max  = lats_1d.max()
        print(lats_1d.min(), lats_1d.max(), lons_1d.min(), lons_1d.max())
    else:
        cstp = 1         # 等温位線ラベルを何個飛ばしに付けるか
        mres = "h"       # 地図の解像度
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
    # 850 hPa等相当温位線
    # 等相当温位線を描く値のリスト
    # 3Kごとに等値線を描く、15Kごとにラベルを付ける
    levels_tc = range(210, 390, 3)
    levels_ta = range(210, 390, 15)
    #levels_tc = range(math.floor(the85.min()-math.fmod(the85.min(),15)), math.ceil(the85.max())+1,3)
    #levels_ta = range(math.floor(the85.min()-math.fmod(the85.min(),15)), math.ceil(the85.max())+1,15)
    # 等温位線をひく
    cr1 = m.contour(lons, lats, the85, levels=levels_tc, colors='k', linewidths=0.8)
    cr2 = m.contour(lons, lats, the85, levels=levels_ta, colors='k', linewidths=1.2)
    clevels = cr1.levels # 細実線を描いた値
    # ラベルを付ける
    try:
        cr1.clabel(clevels[::cstp], fontsize=12, fmt="%d") # 細実線ラベル
        cr2.clabel(clevels[::cstp], fontsize=12, fmt="%d") # 太実線ラベル
    except Exception as e:
        print(str(e))
    #
    # 500 hPa ジオポテンシャル高度
    # 等高線を描く値のリスト
    levels_zc = range(4800, 6000, 60)
    levels_za = [4800, 5100, 5400, 5700, 6000]
    # 等高線を描く
    cr3 = m.contour(lons, lats, z50, levels=levels_zc, colors='gray', linewidths=0.8)
    cr4 = m.contour(lons, lats, z50, levels=levels_za, colors='gray', linewidths=1.2)
    # ラベルを付ける
    clevels = cr3.levels # 細実線を描いた値
    try:
        cr3.clabel(clevels[::5], fontsize=10, fmt="%d") # 細実線ラベル
        cr4.clabel(clevels[::5], fontsize=10, fmt="%d") # 太実線ラベル
    except Exception as e:
        print(str(e))
    #
    # dThe/dz
    # 陰影を描く値のリスト
    levels_r = [-9, -6, -3, 0, 3, 6, 9]
    # 色テーブルの設定
    cmap = cm.GMT_haxby # 色テーブルの選択
    cmap.set_over('w') # 上限を超えた場合の色を指定
    cmap.set_under('purple') # 下限を下回った場合の色を指定
    # 陰影を描く
    cs = m.contourf(lons, lats, dthdz, levels=levels_r, cmap=cmap, extend='both')
    # カラーバーを付ける
    cbar = m.colorbar(cs, location='bottom', pad="5%")
    cbar.set_label('${\\theta}_e(\mathrm{500 hPa}) - {\\theta}_e(\mathrm{850 hPa})$')
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
    res = subprocess.run(args=args, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    print(res.stdout.decode("utf-8"))
    print(res.stderr.decode("utf-8"))

### utils ###


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
    pr85 = 85000.0 # pressure (Pa) for 850 hPa
    pr50 = 50000.0 # pressure (Pa) for 500 hPa
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
    msm = ReadMSM(tsel, file_dir, "plev")
    #
    # fcst_timeを変えてplotmapを実行
    output_filenames = []
    for fcst_time in np.arange(fcst_str, fcst_end+1, fcst_step):
        # fcst_timeを設定
        msm.set_fcst_time(fcst_time)
        # NetCDFデータ読み込み
        lons_1d, lats_1d, lons, lats = msm.readnetcdf()
        # 変数取り出し
        # 850 hPa 気温データを二次元のndarrayで取り出す
        t85 = msm.ret_var("TMP_850mb") # (K)
        # 500 hPa 気温データを二次元のndarrayで取り出す
        t50 = msm.ret_var("TMP_500mb") # (K)
        # 850 hPa 相対湿度データを二次元のndarrayで取り出す
        rh85 = msm.ret_var("RH_850mb") # ()
        # 500 hPa 相対湿度データを二次元のndarrayで取り出す
        rh50 = msm.ret_var("RH_500mb") # ()
        # 500 hPa ジオポテンシャル高度データを二次元のndarrayで取り出す
        z50 = msm.ret_var("HGT_500mb") # (m)
        #
        # 850 hPaの相当温位と飽和相当温位を求める
        the85, thes85 = mktheta(pr85, t85, rh85)
        # 
        # 500 hPaの相当温位と飽和相当温位を求める
        the50, thes50 = mktheta(pr50, t50, rh50)
        # 
        # 500 hPaの飽和相当温位から850 hPaの相当温位を引いて安定度を調べる
        dthdz = the50 - the85
        # ファイルを閉じる
        msm.close_netcdf()
        #
        # タイトルの設定
        title = tlab + " forecast, +" + str(fcst_time) + "h"
        # 出力ファイル名の設定
        hh = "{d:02d}".format(d=fcst_time)
        output_filename = "map_msm_ept_" + sta + "_" + str(hh) + ".png"
        plotmap(fcst_time, sta, lons_1d, lats_1d, lons, lats, z50, the85, the50, dthdz, \
            title, output_filename)
        output_filenames.append(output_filename)
    # gifアニメーションのファイル名
    output_gif_filename = "anim_msm_ept_" + sta + ".gif"
    # pngからgifアニメーションに変換
    convert_png2gif(input_filenames=output_filenames, delay="80", output_filename=output_gif_filename)

