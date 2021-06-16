#!/opt/local/bin/python3
import pandas as pd
import numpy as np
import math
import sys
import subprocess
import argparse
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from mpl_toolkits.basemap import Basemap, cm
from jmaloc import AmedasStation
from readgrib import ReadMSM
from datetime import timedelta
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
import warnings

warnings.filterwarnings('ignore',
                        category=matplotlib.MatplotlibDeprecationWarning)
matplotlib.rcParams['figure.max_open_warning'] = 0
plt.rcParams['xtick.direction'] = 'in'  # x軸目盛線を内側
plt.rcParams['xtick.major.width'] = 1.2  # x軸主目盛線の長さ
plt.rcParams['ytick.direction'] = 'in'  # y軸目盛線を内側
plt.rcParams['ytick.major.width'] = 1.2  # y軸主目盛線の長さ
input_dir_default = "retrieve"

# 予報時刻からの経過時間、１時間毎に指定可能
# この期間の時系列を作成
fcst_str = 0
fcst_end = 36
fcst_step = 1

#1.1:0:grid_template=0:winds(N/S):
#  lat-lon grid:(481 x 505) units 1e-06 input WE:NS output WE:SN res 48
#  lat 47.600000 to 22.400000 by 0.050000
#  lon 120.000000 to 150.000000 by 0.062500 #points=242905

plt_barbs = True  # true: 矢羽を描く
#barbs_kt = False # true: kt, false: m/s
barbs_kt = True  # true: kt, false: m/s

### Start Map Prog ###


def plotmap(index, mslp, prep, temp, uwnd, vwnd, relh, cfrl, cfrm, cfrh, cfrt):
    #
    # 作図
    # (0) プロットエリアの定義
    #fig, ax1 = plt.subplots()
    fig = plt.figure(figsize=(6, 6))
    ax1 = fig.add_subplot(3, 1, 1)
    # タイトルを付ける
    plt.title(title)

    # (1) 降水量と気温
    # (1-1) 降水量(mm)
    ax1.set_ylim([0, math.ceil(prep.max() + math.fmod(prep.max(), 10)) + 1])
    ax1.bar(index,
            prep,
            color='b',
            width=0.03,
            alpha=0.4,
            label='Precipitation')
    ax1.set_ylabel('Precipitation (mm)')
    # 凡例
    ax1.legend(loc='upper left')
    #
    # (1-2) 気温（K）
    ax2 = ax1.twinx()  # 2つのプロットを関連付ける
    ax2.set_ylim([math.floor(temp.min() - 1), math.ceil(temp.max()) + 2])
    ax2.plot(index, temp, color='r', label='Temperature')
    ax2.set_ylabel('Temperature (K)')
    # 凡例
    ax2.legend(loc='upper right')
    #plt.legend(loc='lower center')
    #
    # (2) RH（%）& wind
    # (2-1) RH（%）
    ax3 = fig.add_subplot(3, 1, 2)
    ax3.set_ylim([0, 100])
    ax3.plot(index, relh, color='b', label='RH')
    ax3.set_ylabel('RH (%)')
    # 凡例
    ax3.legend(loc='best')
    #
    # (2-2) 矢羽
    y = 50
    if plt_barbs:
        if barbs_kt:
            # kt
            ax3.barbs(index, y, uwnd, vwnd, color='k', length=5, sizes=dict(emptybarb=0.001), \
            barb_increments=dict(half=2.57222, full=5.14444, flag=25.7222))
        else:
            # m/s
            ax3.barbs(index,
                      y,
                      uwnd,
                      vwnd,
                      color='k',
                      length=5,
                      sizes=dict(emptybarb=0.001))
    #
    # (3) 地表気圧（hPa）
    ax5 = fig.add_subplot(3, 1, 3)
    #
    ax5.set_ylim([
        math.floor(mslp.min() - math.fmod(mslp.min(), 2)) - 1,
        math.ceil(mslp.max()) + 1
    ])
    ax5.plot(index, mslp, color='k', label='Pressure')
    ax5.set_ylabel('pressure (hPa)')
    #ax5.set_xlabel('Hour')
    # 凡例
    ax5.legend(loc='upper left')
    #
    # (3-2) 気温（K）
    ax6 = ax5.twinx()  # 2つのプロットを関連付ける
    ax6.set_ylim([0, 100])
    ind_l = index - timedelta(minutes=20)
    ind_m = index - timedelta(minutes=5)
    ind_h = index + timedelta(minutes=10)
    ind_t = index + timedelta(minutes=25)
    ax6.bar(ind_l, cfrl, color='r', width=0.01, alpha=0.4, label='low')
    ax6.bar(ind_m, cfrm, color='g', width=0.01, alpha=0.4, label='middle')
    ax6.bar(ind_h, cfrh, color='b', width=0.01, alpha=0.4, label='high')
    ax6.bar(ind_t, cfrt, color='k', width=0.01, alpha=0.4, label='total')
    ax6.set_ylabel('Cloud Cover (%)')
    # 凡例
    ax6.legend(loc='lower left')
    #
    # y軸の目盛り
    ax1.yaxis.set_major_locator(ticker.AutoLocator())
    ax1.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax2.yaxis.set_major_locator(ticker.AutoLocator())
    ax2.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax3.yaxis.set_major_locator(ticker.AutoLocator())
    ax3.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax5.yaxis.set_major_locator(ticker.AutoLocator())
    ax5.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax6.yaxis.set_major_locator(ticker.AutoLocator())
    ax6.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    #
    # x軸の目盛り
    ax1.xaxis.set_major_locator(ticker.AutoLocator())
    ax1.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax3.xaxis.set_major_locator(ticker.AutoLocator())
    ax3.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax5.xaxis.set_major_locator(ticker.AutoLocator())
    ax5.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    #
    ax1.xaxis.set_major_formatter(ticker.NullFormatter())
    ax1.xaxis.set_minor_formatter(ticker.NullFormatter())
    ax3.xaxis.set_major_formatter(ticker.NullFormatter())
    ax3.xaxis.set_minor_formatter(ticker.NullFormatter())
    #
    ax5.set_xticklabels(ax5.get_xticklabels(), rotation=70, size="small")
    ax5.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %HUTC'))
    ax5.xaxis.set_minor_formatter(ticker.NullFormatter())
    #
    # プロット範囲の調整
    plt.subplots_adjust(top=None, bottom=0.15, wspace=0.25, hspace=0.15)
    #plt.subplots_adjust(hspace=0.8,bottom=0.2)

    # (4) ファイルへの書き出し
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()
    #plt.show()


### End Map Prog ###

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
    # タイトルの設定
    title = tlab + " MSM forecast, +" + str(fcst_str) + "-" + str(fcst_end)
    # オプションの読み込み
    args = _parse_command(sys.argv)
    # 予報時刻, 作図する地域の指定
    fcst_date = args.fcst_date
    sta = args.sta
    file_dir = args.input_dir
    # 作図する地域の指定
    if sta == "Tokyo":
        ilon = 316
        ilat = 238
        #rlon=139.75
        #rlat=35.692
    elif sta == "Yokohama":
        ilon = 314  #lon =  139.625
        ilat = 243  #lat =  35.45
        #rlon=139.65
        #rlat=35.438
    else:
        print("not supported yet: sta =", sta)
        quit()
    #
    # datetimeに変換
    tinfo = pd.to_datetime(fcst_date)
    #
    tsel = tinfo.strftime("%Y%m%d%H%M%S")
    tlab = tinfo.strftime("%m/%d %H UTC")
    #
    # ReadMSM初期化
    msm = ReadMSM(tsel, file_dir, "surf")
    #
    # アメダス地点の位置を取得
    amedas = AmedasStation()
    rlon, rlat = amedas.get_staloc(en_name=sta)
    print(sta, ": lon, lat = ", rlon, rlat)
    #
    # 時系列データの準備
    index_add = []
    mslp_add = []
    rain_add = []
    temp_add = []
    uwnd_add = []
    vwnd_add = []
    relh_add = []
    cfrl_add = []
    cfrm_add = []
    cfrh_add = []
    cfrt_add = []
    # fcst_timeを変えてplotmapを実行
    for fcst_time in np.arange(fcst_str, fcst_end + 1, fcst_step):
        index_add.append(tinfo + timedelta(hours=int(1 * fcst_time)))
        # fcst_timeを設定
        msm.set_fcst_time(fcst_time)
        # NetCDFデータ読み込み
        lons_1d, lats_1d, lons, lats = msm.readnetcdf()
        # グリッド番号の取得
        if fcst_time == fcst_str:
            ilon = get_gridloc(lons_1d, rlon)
            ilat = get_gridloc(lats_1d, rlat)
            print("lon grid, lat grid, lon, lat = ", ilon, ilat,
                  np.array(lons_1d)[ilon],
                  np.array(lats_1d)[ilat])
        # 変数取り出し
        # 海面更生気圧を二次元のndarrayで取り出す
        mslp = msm.ret_var("PRMSL_meansealevel", fact=0.01)  # (hPa)
        mslp_add.append(mslp[ilat, ilon])
        # 降水量を二次元のndarrayで取り出す
        rain = msm.ret_var("APCP_surface")  # (mm/h)
        rain_add.append(rain[ilat, ilon])
        # 気温を二次元のndarrayで取り出す (K->℃)
        temp = msm.ret_var("TMP_1D5maboveground", offset=-273.15)  # (℃)
        temp_add.append(temp[ilat, ilon])
        # 東西風を二次元のndarrayで取り出す
        uwnd = msm.ret_var("UGRD_10maboveground")  # (m/s)
        uwnd_add.append(uwnd[ilat, ilon])
        # 南北風を二次元のndarrayで取り出す
        vwnd = msm.ret_var("VGRD_10maboveground")  # (m/s)
        vwnd_add.append(vwnd[ilat, ilon])
        # 相対湿度を二次元のndarrayで取り出す
        relh = msm.ret_var("RH_1D5maboveground")  # ()
        relh_add.append(relh[ilat, ilon])
        # 下層雲量を二次元のndarrayで取り出す
        cfrl = msm.ret_var("LCDC_surface")  # ()
        cfrl_add.append(cfrl[ilat, ilon])
        # 中層雲量を二次元のndarrayで取り出す
        cfrm = msm.ret_var("MCDC_surface")  # ()
        cfrm_add.append(cfrm[ilat, ilon])
        # 上層雲量を二次元のndarrayで取り出す
        cfrh = msm.ret_var("HCDC_surface")  # ()
        cfrh_add.append(cfrh[ilat, ilon])
        # 全雲量を二次元のndarrayで取り出す
        cfrt = msm.ret_var("TCDC_surface")  # ()
        cfrt_add.append(cfrt[ilat, ilon])
        # ファイルを閉じる
        msm.close_netcdf()
        #
    #
    # 出力ファイル名の設定
    output_filename = "map_tvar_msm_" + str(fcst_str) + "-" + str(
        fcst_end) + "_" + sta + ".png"
    nt = len(index_add)

    index = np.vstack(index_add).reshape(nt)
    rain = np.vstack(rain_add).reshape(nt)
    mslp = np.vstack(mslp_add).reshape(nt)
    rain = np.vstack(rain_add).reshape(nt)
    temp = np.vstack(temp_add).reshape(nt)
    uwnd = np.vstack(uwnd_add).reshape(nt)
    vwnd = np.vstack(vwnd_add).reshape(nt)
    relh = np.vstack(relh_add).reshape(nt)
    cfrl = np.vstack(cfrl_add).reshape(nt)
    cfrm = np.vstack(cfrm_add).reshape(nt)
    cfrh = np.vstack(cfrh_add).reshape(nt)
    cfrt = np.vstack(cfrt_add).reshape(nt)
    print(rain.shape)
    #
    # 作図
    plotmap(index, mslp, rain, temp, uwnd, vwnd, relh, cfrl, cfrm, cfrh, cfrt)
