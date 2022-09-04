#!/opt/local/bin/python3
import pandas as pd
import numpy as np
import sys
from datetime import timedelta
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from jmaloc import MapRegion
from readgrib import ReadMSM
from utils import ColUtils
from utils import convert_png2gif
from utils import parse_command
from utils import post
import utils.common


def plotmap(sta, lons_1d, lats_1d, lons, lats, uwnd, vwnd, tmp, rh, title,
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
    uwnd: ndarray
        東西風（2次元、m/s）
    vwnd: ndarray
        南北風（2次元、m/s）
    tmp: ndarray
        気温データ（2次元、K）
    rh: ndarray
       相対湿度（2次元、%）
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
        opt_c1 = False  # 1度の等温線を描かない
        opt_barbs = True  # 矢羽を描く
        bstp = 10  # 矢羽を何個飛ばしに描くか
        cstp = 1  # 等値線ラベルを何個飛ばしに付けるか
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
        opt_c1 = True  # 1度の等温線を描く
        opt_barbs = True  # 矢羽を描く
        bstp = 2  # 矢羽を何個飛ばしに描くか
        cstp = 3  # 等値線ラベルを何個飛ばしに付けるか
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
    # 850 hPa 気温
    # 1度の等温線を描く
    if opt_c1:
        # 等温線を描く値のリスト（1Kごと）
        levels_t = np.arange(-60, 61, 1)
        # 等温線をひく
        cr1 = m.contour(lons,
                        lats,
                        tmp,
                        levels=levels_t,
                        colors='k',
                        linestyles=['-', ':', ':'],
                        linewidths=[1.8, 1.2, 1.2])
        cr1.clabel(cr1.levels[::cstp], fontsize=12, fmt="%d")
    else:
        # 等温線を描く値のリスト（3Kごと）
        levels_t = np.arange(-60, 61, 3)
        # 等温線をひく
        cr2 = m.contour(lons,
                        lats,
                        tmp,
                        levels=levels_t,
                        colors='k',
                        linestyles='-',
                        linewidths=1.8)
        cr2.clabel(cr2.levels[::cstp], fontsize=12, fmt="%d")

    #
    # 850 hPa 相対湿度
    # 陰影を描く値のリスト
    levels_r = [60, 75, 80, 90, 100]
    # 色テーブルの設定
    cutils = ColUtils('drywet')  # 色テーブルの選択
    cmap = cutils.get_ctable(under='w')  # 色テーブルの取得
    # 陰影を描く
    cs = m.contourf(lons, lats, rh, levels=levels_r, cmap=cmap, extend='min')
    # カラーバーを付ける
    cbar = m.colorbar(cs, location='bottom', pad="5%")
    cbar.set_label('RH (%)')
    #
    # 850 hPa東西風、南北風
    # 矢羽を描く
    if opt_barbs:
        m.barbs(lons[::bstp, ::bstp],
                lats[::bstp, ::bstp],
                uwnd[::bstp, ::bstp],
                vwnd[::bstp, ::bstp],
                color='r',
                length=5,
                linewidth=1.5,
                sizes=dict(emptybarb=0.00, spacing=0.16, height=0.4))
    #
    # 海岸線を描く
    m.drawcoastlines()
    #
    # タイトルを付ける
    plt.title(title)
    # 図を保存
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    # オプションの読み込み
    args = parse_command(sys.argv, opt_lev=True)
    # 予報時刻、作図する地域、高度の指定
    fcst_date = args.fcst_date
    sta = args.sta
    file_dir = args.input_dir
    level = args.level
    # 予報時刻からの経過時間（3時間毎に指定可能）
    fcst_end = args.fcst_time
    fcst_str = 0  # 開始時刻
    fcst_step = 3  # 作図する間隔
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
    for fcst_time in np.arange(fcst_str, fcst_end + 1, fcst_step):
        # fcst_timeを設定
        msm.set_fcst_time(fcst_time)
        # fcst時刻
        tinfo_fcst = tinfo + timedelta(hours=int(fcst_time))
        tlab_fcst = tinfo_fcst.strftime("%m/%d %H UTC")
        # NetCDFデータ読み込み
        lons_1d, lats_1d, lons, lats = msm.readnetcdf()
        # 変数取り出し
        # 850 hPa 東西風、南北風データを二次元のndarrayで取り出す
        uwnd = msm.ret_var("UGRD_" + str(level) + "mb")  # (m/s)
        vwnd = msm.ret_var("VGRD_" + str(level) + "mb")  # (m/s)
        #        uwnd = msm.ret_var("UGRD_850mb") # (m/s)
        #        vwnd = msm.ret_var("VGRD_850mb") # (m/s)
        # 850 hPa 気温データを二次元のndarrayで取り出す (K->℃)
        tmp = msm.ret_var("TMP_" + str(level) + "mb", offset=-273.15)  # (℃)
        #        tmp = msm.ret_var("TMP_850mb", offset=-273.15) # (℃)
        # 850 hPa 相対湿度データを二次元のndarrayで取り出す ()
        rh = msm.ret_var("RH_" + str(level) + "mb")  # ()
        #        rh = msm.ret_var("RH_850mb") # ()
        # ファイルを閉じる
        msm.close_netcdf()
        #
        # タイトルの設定
        title = str(level) + "hPa " + tlab + " MSM forecast, +" + str(
            fcst_time) + "h (" + tlab_fcst + ")"
        #        title = tlab + " forecast, +" + str(fcst_time) + "h"
        # 出力ファイル名の設定
        hh = "{d:02d}".format(d=fcst_time)
        output_filename = "map_msm_temp_" + str(
            level) + "hPa_" + sta + "_" + str(hh) + ".png"
        # 作図
        plotmap(sta, lons_1d, lats_1d, lons, lats, uwnd, vwnd, tmp, rh, title,
                output_filename)
        output_filenames.append(output_filename)
    # pngからgifアニメーションに変換
    convert_png2gif(input_filenames=output_filenames,
                    delay="80",
                    output_filename="anim_msm_temp_" + str(level) + "hPa_" +
                    sta + ".gif")
    # 後処理
    post(output_filenames)
