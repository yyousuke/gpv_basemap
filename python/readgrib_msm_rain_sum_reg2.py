#!/opt/local/bin/python3
import pandas as pd
import numpy as np
import math
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from jmaloc import MapRegion
from readgrib import ReadMSM
from utils import ColUtils
from utils import parse_command
import utils.common


def plotmap(sta, lons_1d, lats_1d, lons, lats, mslp, rain, title,
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
    mslp: ndarray
        SLPデータ（2次元、hPa）
    rain: ndarray
        降水量（2次元、mm）
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
    # ランベルト正角円錐図法、4つのパラメータは描画する範囲の指定、最後は解像度
    m = Basemap(projection='lcc',
                lon_0=135,
                lat_0=35,
                llcrnrlon=lon_min,
                urcrnrlon=lon_max,
                llcrnrlat=lat_min,
                urcrnrlat=lat_max,
                resolution=mres)
    # 図法の座標系に変換
    x, y = m(lons, lats)
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
        levels1 = range(math.floor(mslp.min() - math.fmod(mslp.min(), 2)),
                        math.ceil(mslp.max()) + 1, 1)
        cr1 = m.contour(x,
                        y,
                        mslp,
                        levels=levels1,
                        colors='k',
                        linestyles=['-', ':'],
                        linewidths=1.2)
        # ラベルを付ける
        cr1.clabel(cr1.clevels[::cstp], fontsize=12, fmt="%d")
    else:
        # 等圧線をひく間隔(1hPaごと)をlevelsにリストとして入れる
        levels2 = range(math.floor(mslp.min() - math.fmod(mslp.min(), 2)),
                        math.ceil(mslp.max()) + 1, 2)
        cr2 = m.contour(x, y, mslp, levels=levels2, colors='k', linewidths=1.2)
        # ラベルを付ける
        cr2.clabel(cr2.levels[::cstp], fontsize=12, fmt="%d")
    #
    #
    # 色テーブルの設定
    cutils = ColUtils('wysiwyg')  # 色テーブルの選択
    cmap = cutils.get_ctable(under='gray', over='r')  # 色テーブルの取得
    # 降水量の陰影を付ける値をlevelsrにリストとして入れる
    levelsr = [1, 5, 10, 20, 50, 80, 100, 200, 400, 600]
    # 陰影を描く
    cs = m.contourf(x, y, rain, levels=levelsr, cmap=cmap, extend='both')
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


if __name__ == '__main__':
    # オプションの読み込み
    args = parse_command(sys.argv)
    # 予報時刻, 作図する地域の指定
    fcst_date = args.fcst_date
    sta = args.sta
    file_dir = args.input_dir
    # 予報時刻からの経過時間
    fcst_end = args.fcst_time
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
    for fcst_time in np.arange(0, fcst_end + 1, 1):
        # fcst_timeを設定
        msm.set_fcst_time(fcst_time)
        # NetCDFデータ読み込み
        lons_1d, lats_1d, lons, lats = msm.readnetcdf()
        # 変数取り出し
        # 海面更生気圧を二次元のndarrayで取り出す
        mslp = msm.ret_var("PRMSL_meansealevel", fact=0.01)  # (hPa)
        # 降水量を二次元のndarrayで取り出す
        rain = msm.ret_var("APCP_surface")  # (mm/h)
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
    title = tlab + " MSM forecast, +" + "0-" + str(
        fcst_end) + "h rain & +" + str(fcst_end) + "h SLP"
    # 出力ファイル名の設定
    output_filename = "map_msm_rain_sum" + "0-" + str(
        fcst_end) + "_" + sta + ".png"
    plotmap(sta, lons_1d, lats_1d, lons, lats, mslp, rain, title,
            output_filename)
