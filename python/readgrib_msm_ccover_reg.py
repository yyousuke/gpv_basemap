#!/opt/local/bin/python3
import pandas as pd
import numpy as np
import math
import sys
from datetime import timedelta
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.ticker as ticker
from jmaloc import MapRegion
from readgrib import ReadMSM
from utils import val2col
from utils import convert_png2gif
from utils import parse_command
from utils import post
import utils.common

### Start Map Prog ###


def plotmap(fcst_time, sta, lons_1d, lats_1d, lons, lats, mslp, cfrl, cfrm,
            cfrh, title, output_filename):
    """作図を行う
    
    Parameters:
    ----------
    fcst_time: int
        予報開始時刻からの経過時間（時）
    sta: str
        地点名 
    lons_1d: str
        経度データ（1次元）
    lats_1d: ndarray
        緯度データ（1次元）
    lons: ndarray
        経度データ（2次元）
    lats: ndarray
        緯度データ（2次元） 
    mslp: ndarray
        SLPデータ（2次元）
    cfrl: ndarray
        下層雲量（2次元）
    cfrm: ndarray
        中層雲量（2次元）
    cfrh: ndarray
        上層雲量（2次元）
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
    ax = fig.add_axes((0.1, 0.3, 0.8, 0.6))
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
        # 等圧線をひく間隔(1hPaごと)をlevels1にリストとして入れる
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
        cr1.clabel(cr1.levels[::cstp], fontsize=12, fmt="%d")
    else:
        # 等圧線をひく間隔(2hPaごと)をlevels2にリストとして入れる
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
        cr2.clabel(cr2.levels[::cstp], fontsize=12, fmt="%d")
    #
    # 雲量の陰影を付ける値をlevelsrにリストとして入れる
    levelsc = np.arange(0, 100.1, 5)
    # 色テーブル取得
    cmapl = plt.get_cmap('Reds')  # 下層
    cmapm = plt.get_cmap('Greens')  # 中層
    cmaph = plt.get_cmap('Blues')  # 上層
    # 陰影を描く（下層雲）
    csl = m.contourf(lons, lats, cfrl, levels=levelsc, cmap=cmapl, alpha=0.3)
    # 陰影を描く（中層雲）
    csm = m.contourf(lons, lats, cfrm, levels=levelsc, cmap=cmapm, alpha=0.3)
    # 陰影を描く（上層雲）
    csh = m.contourf(lons, lats, cfrh, levels=levelsc, cmap=cmaph, alpha=0.3)
    #
    # 海岸線を描く
    m.drawcoastlines()
    #
    # タイトルを付ける
    plt.title(title)
    #
    # val2colクラスの初期化（気温の範囲はtmin、tmaxで設定、tstepで刻み幅）
    cbarh = val2col(cmap='Blues', tmin=0., tmax=100.1, tstep=20.)
    cbarm = val2col(cmap='Greens', tmin=0., tmax=100.1, tstep=20.)
    cbarl = val2col(cmap='Reds', tmin=0., tmax=100.1, tstep=20.)
    # カラーバーを付ける
    cbarh.colorbar(fig, anchor=(0.40, 0.24), size=(0.3, 0.02), label=False)
    cbarm.colorbar(fig, anchor=(0.40, 0.20), size=(0.3, 0.02), label=False)
    cbarl.colorbar(fig, anchor=(0.40, 0.16), size=(0.3, 0.02), label=True)
    # ラベルを付ける
    cbarh.clabel(fig,
                 anchor=(0.39, 0.235),
                 size=(0.1, 0.02),
                 text="High cloud cover")
    cbarm.clabel(fig,
                 anchor=(0.39, 0.195),
                 size=(0.1, 0.02),
                 text="Middle cloud cover")
    cbarl.clabel(fig,
                 anchor=(0.39, 0.155),
                 size=(0.1, 0.02),
                 text="Low cloud cover")
    #
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
        # 海面更生気圧を二次元のndarrayで取り出す
        mslp = msm.ret_var("PRMSL_meansealevel", fact=0.01)  # (hPa)
        # 降水量を二次元のndarrayで取り出す
        #rain = msm.ret_var("APCP_surface")  # (mm/h)
        # 下層雲量を二次元のndarrayで取り出す
        cfrl = msm.ret_var("LCDC_surface")  # ()
        # 中層雲量を二次元のndarrayで取り出す
        cfrm = msm.ret_var("MCDC_surface")  # ()
        # 上層雲量を二次元のndarrayで取り出す
        cfrh = msm.ret_var("HCDC_surface")  # ()
        # ファイルを閉じる
        msm.close_netcdf()
        #
        # タイトルの設定
        title = tlab + " MSM forecast, +" + str(
            fcst_time) + "h (" + tlab_fcst + ")"
        # 出力ファイル名の設定
        hh = "{d:02d}".format(d=fcst_time)
        output_filename = "map_msm_ccover_" + sta + "_" + str(hh) + ".png"
        plotmap(fcst_time, sta, lons_1d, lats_1d, lons, lats, mslp, cfrl, cfrm,
                cfrh, title, output_filename)
        output_filenames.append(output_filename)
    # pngからgifアニメーションに変換
    convert_png2gif(input_filenames=output_filenames,
                    delay="80",
                    output_filename="anim_msm_ccover_" + sta + ".gif")
    # 後処理
    post(output_filenames)
