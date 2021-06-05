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
import matplotlib.ticker as ticker
from jmaloc import MapRegion
from readgrib import ReadGSM
import warnings

warnings.filterwarnings('ignore',
                        category=matplotlib.MatplotlibDeprecationWarning)
matplotlib.rcParams['figure.max_open_warning'] = 0
input_dir_default = "retrieve"

# 予報時刻からの経過時間、１時間毎に指定可能
fcst_str = 0
fcst_end = 36
fcst_step = 1

#


### Start Map Prog ###
class val2col():
    def __init__(self, tmin=0., tmax=1., tstep=0.2, cmap='jet'):
        self.tmin = tmin
        self.tmax = tmax
        self.tstep = tstep
        self.cmap = cmap
        self.cm = plt.get_cmap(self.cmap)

    def conv(self, temp):
        n = (temp - self.tmin) / (self.tmax - self.tmin) * self.cm.N
        n = max(min(n, self.cm.N), 0)
        return self.cm(int(n))

    def colorbar(self,
                 fig=None,
                 anchor=(0.35, 0.24),
                 size=(0.3, 0.02),
                 fmt="{f:.0f}",
                 label=True):
        if fig is None:
            raise Exception('fig is needed')
        ax = fig.add_axes(anchor + size)
        gradient = np.linspace(0, 1, self.cm.N)
        gradient_array = np.vstack((gradient, gradient))
        ticks = list()
        labels = list()
        ll = np.arange(self.tmin, self.tmax, self.tstep)
        for t in ll:
            ticks.append((t - self.tmin) / (self.tmax - self.tmin) * self.cm.N)
            if label:
                labels.append(fmt.format(f=t))
        # カラーバーを描く
        ax.imshow(gradient_array, aspect='auto', cmap=self.cm)
        ax.yaxis.set_major_locator(ticker.NullLocator())
        ax.yaxis.set_minor_locator(ticker.NullLocator())
        ax.set_xticks(ticks)
        if label:
            ax.set_xticklabels(labels)
        else:
            ax.xaxis.set_major_formatter(ticker.NullFormatter())
            ax.xaxis.set_minor_formatter(ticker.NullFormatter())
        #ax.set_axis_off()

    def clabel(self,
               fig=None,
               anchor=(0.34, 0.24),
               size=(0.1, 0.02),
               text=None,
               ha='right',
               va='bottom',
               fontsize=10):
        if fig is None:
            raise Exception('fig is needed')
        ax = fig.add_axes(anchor + size)
        ax.text(0.0, 0.0, text, ha=ha, va=va, fontsize=fontsize)
        ax.set_axis_off()


def plotmap(fcst_time, sta, lons_1d, lats_1d, lons, lats, mslp, cfrl, cfrm,
            cfrh, title, output_filename):
    #
    # MapRegion Classの初期化
    region = MapRegion(sta)
    if sta == "Japan":
        opt_c1 = False
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
        cstp = 1
        bstp = 1
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
        levels1 = range(math.floor(mslp.min() - math.fmod(mslp.min(), 1)),
                        math.ceil(mslp.max()) + 1, 1)
        # 等圧線をひく
        m.contour(lons,
                  lats,
                  mslp,
                  levels=levels1,
                  colors='k',
                  linestyles=':',
                  linewidths=0.8)
    # 等圧線をひく間隔(2hPaごと)をlevels2にリストとして入れる
    levels2 = range(math.floor(mslp.min() - math.fmod(mslp.min(), 2)),
                    math.ceil(mslp.max()) + 1, 2)
    # 等圧線をひく
    cr2 = m.contour(lons,
                    lats,
                    mslp,
                    levels=levels2,
                    colors='k',
                    linewidths=0.8)
    # ラベルを付ける
    clevels2 = cr2.levels
    cr2.clabel(clevels2[::cstp], fontsize=10, fmt="%d")
    #
    #

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
    cbarh.colorbar(fig, anchor=(0.35, 0.24), size=(0.3, 0.02), label=False)
    cbarm.colorbar(fig, anchor=(0.35, 0.20), size=(0.3, 0.02), label=False)
    cbarl.colorbar(fig, anchor=(0.35, 0.16), size=(0.3, 0.02), label=True)
    # ラベルを付ける
    cbarh.clabel(fig,
                 anchor=(0.34, 0.235),
                 size=(0.1, 0.02),
                 text="High cloud cover")
    cbarm.clabel(fig,
                 anchor=(0.34, 0.195),
                 size=(0.1, 0.02),
                 text="Middle cloud cover")
    cbarl.clabel(fig,
                 anchor=(0.34, 0.155),
                 size=(0.1, 0.02),
                 text="Low cloud cover")
    #
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
        # 降水量を二次元のndarrayで取り出す
        #rain = gsm.ret_var("APCP_surface")  # (mm/h)
        # 下層雲量を二次元のndarrayで取り出す
        cfrl = gsm.ret_var("LCDC_surface")  # ()
        # 中層雲量を二次元のndarrayで取り出す
        cfrm = gsm.ret_var("MCDC_surface")  # ()
        # 上層雲量を二次元のndarrayで取り出す
        cfrh = gsm.ret_var("HCDC_surface")  # ()
        # ファイルを閉じる
        gsm.close_netcdf()
        #
        # タイトルの設定
        title = tlab + " forecast, +" + str(fcst_time) + "h"
        # 出力ファイル名の設定
        hh = "{d:02d}".format(d=fcst_time)
        output_filename = "map_gsm_ccover_" + sta + "_" + str(hh) + ".png"
        plotmap(fcst_time, sta, lons_1d, lats_1d, lons, lats, mslp, cfrl, cfrm,
                cfrh, title, output_filename)
        output_filenames.append(output_filename)
    # gifアニメーションのファイル名
    output_gif_filename = "anim_gsm_ccover_" + sta + ".gif"
    # pngからgifアニメーションに変換
    convert_png2gif(input_filenames=output_filenames,
                    delay="80",
                    output_filename=output_gif_filename)
