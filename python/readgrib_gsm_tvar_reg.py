#!/opt/local/bin/python3
import pandas as pd
import numpy as np
import math
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from jmaloc import AmedasStation
from readgrib import ReadGSM
from datetime import timedelta
from utils import parse_command
from utils import get_gridloc
import utils.common

plt.rcParams['xtick.direction'] = 'in'  # x軸目盛線を内側
plt.rcParams['xtick.major.width'] = 1.2  # x軸主目盛線の長さ
plt.rcParams['ytick.direction'] = 'in'  # y軸目盛線を内側
plt.rcParams['ytick.major.width'] = 1.2  # y軸主目盛線の長さ

# 121x151
# lat-lon grid:(121 x 151) units 1e-06 input WE:NS output WE:SN res 48
# lat 50.000000 to 20.000000 by 0.200000
# lon 120.000000 to 150.000000 by 0.250000 #points=18271

plt_barbs = True  # true: 矢羽を描く
#barbs_kt = False # true: kt, false: m/s
barbs_kt = True  # true: kt, false: m/s

### Start Map Prog ###


def plotmap(index, mslp, prep, temp, uwnd, vwnd, relh, cfrl, cfrm, cfrh, cfrt,
            title, output_filename):
    #
    # 作図
    # (0) プロットエリアの定義
    fig = plt.figure(figsize=(10, 10))
    ax1 = fig.add_subplot(3, 1, 1)
    # タイトルを付ける
    plt.title(title, fontsize=20)

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
            ax3.barbs(index,
                      y,
                      uwnd,
                      vwnd,
                      color='k',
                      length=5,
                      sizes=dict(emptybarb=0.001),
                      barb_increments=dict(half=2.57222,
                                           full=5.14444,
                                           flag=25.7222))
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
    # (3) 地表気圧と気温
    # (3-1) 地表気圧（hPa）
    ax5 = fig.add_subplot(3, 1, 3)
    #
    ax5.set_ylim([
        math.floor(mslp.min() - math.fmod(mslp.min(), 2)) - 1,
        math.ceil(mslp.max()) + 1
    ])
    ax5.plot(index, mslp, color='k', label='Pressure')
    ax5.set_ylabel('pressure (hPa)')
    #
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
    ax1.yaxis.set_major_locator(mticker.AutoLocator())
    ax1.yaxis.set_minor_locator(mticker.AutoMinorLocator())
    ax2.yaxis.set_major_locator(mticker.AutoLocator())
    ax2.yaxis.set_minor_locator(mticker.AutoMinorLocator())
    ax3.yaxis.set_major_locator(mticker.AutoLocator())
    ax3.yaxis.set_minor_locator(mticker.AutoMinorLocator())
    ax5.yaxis.set_major_locator(mticker.AutoLocator())
    ax5.yaxis.set_minor_locator(mticker.AutoMinorLocator())
    ax6.yaxis.set_major_locator(mticker.AutoLocator())
    ax6.yaxis.set_minor_locator(mticker.AutoMinorLocator())
    #
    # x軸の目盛り
    ax1.xaxis.set_major_locator(mticker.AutoLocator())
    ax1.xaxis.set_minor_locator(mticker.AutoMinorLocator())
    ax3.xaxis.set_major_locator(mticker.AutoLocator())
    ax3.xaxis.set_minor_locator(mticker.AutoMinorLocator())
    ax5.xaxis.set_major_locator(mticker.AutoLocator())
    ax5.xaxis.set_minor_locator(mticker.AutoMinorLocator())
    #
    ax1.xaxis.set_major_formatter(mticker.NullFormatter())
    ax1.xaxis.set_minor_formatter(mticker.NullFormatter())
    ax3.xaxis.set_major_formatter(mticker.NullFormatter())
    ax3.xaxis.set_minor_formatter(mticker.NullFormatter())
    #
    ax5.xaxis.set_major_locator(mticker.FixedLocator(
        ax5.get_xticks().tolist()))
    ax5.set_xticklabels(ax5.get_xticklabels(), rotation=70, size="small")
    ax5.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %HUTC'))
    ax5.xaxis.set_minor_formatter(mticker.NullFormatter())
    #
    # プロット範囲の調整
    plt.subplots_adjust(top=None, bottom=0.15, wspace=0.25, hspace=0.15)
    #plt.subplots_adjust(hspace=0.8,bottom=0.2)

    # (4) ファイルへの書き出し
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()
    #plt.show()


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
    # アメダス地点の位置を取得
    amedas = AmedasStation()
    rlon, rlat = amedas.get_staloc(en_name=sta)
    print(sta, ": lon, lat = ", rlon, rlat)
    #
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
        gsm.set_fcst_time(fcst_time)
        # NetCDFデータ読み込み
        lons_1d, lats_1d, lons, lats = gsm.readnetcdf()
        # グリッド番号の取得
        if fcst_time == fcst_str:
            ilon = get_gridloc(lons_1d, rlon)
            ilat = get_gridloc(lats_1d, rlat)
            print("lon grid, lat grid, lon, lat = ", ilon, ilat,
                  np.array(lons_1d)[ilon],
                  np.array(lats_1d)[ilat])
        # 変数取り出し
        # 海面更生気圧を二次元のndarrayで取り出す
        mslp = gsm.ret_var("PRMSL_meansealevel", fact=0.01)  # (hPa)
        mslp_add.append(mslp[ilat, ilon])
        # 降水量を二次元のndarrayで取り出す
        rain = gsm.ret_var("APCP_surface")  # (mm/h)
        rain_add.append(rain[ilat, ilon])
        # 気温を二次元のndarrayで取り出す (K->℃)
        temp = gsm.ret_var("TMP_2maboveground", offset=-273.15)  # (℃)
        temp_add.append(temp[ilat, ilon])
        # 東西風を二次元のndarrayで取り出す
        uwnd = gsm.ret_var("UGRD_10maboveground")  # (m/s)
        uwnd_add.append(uwnd[ilat, ilon])
        # 南北風を二次元のndarrayで取り出す
        vwnd = gsm.ret_var("VGRD_10maboveground")  # (m/s)
        vwnd_add.append(vwnd[ilat, ilon])
        # 相対湿度を二次元のndarrayで取り出す
        relh = gsm.ret_var("RH_2maboveground")  # ()
        relh_add.append(relh[ilat, ilon])
        # 下層雲量を二次元のndarrayで取り出す
        cfrl = gsm.ret_var("LCDC_surface")  # ()
        cfrl_add.append(cfrl[ilat, ilon])
        # 中層雲量を二次元のndarrayで取り出す
        cfrm = gsm.ret_var("MCDC_surface")  # ()
        cfrm_add.append(cfrm[ilat, ilon])
        # 上層雲量を二次元のndarrayで取り出す
        cfrh = gsm.ret_var("HCDC_surface")  # ()
        cfrh_add.append(cfrh[ilat, ilon])
        # 全雲量を二次元のndarrayで取り出す
        cfrt = gsm.ret_var("TCDC_surface")  # ()
        cfrt_add.append(cfrt[ilat, ilon])
        # ファイルを閉じる
        gsm.close_netcdf()
        #
    #
    # タイトルの設定
    title = tlab + " GSM forecast, +" + str(fcst_str) + "-" + str(fcst_end)
    #
    # 出力ファイル名の設定
    output_filename = "map_tvar_gsm_" + str(fcst_str) + "-" + str(
        fcst_end) + "_" + sta + ".png"
    nt = len(index_add)

    index = np.vstack(index_add).reshape(nt)
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
    plotmap(index, mslp, rain, temp, uwnd, vwnd, relh, cfrl, cfrm, cfrh, cfrt,
            title, output_filename)
