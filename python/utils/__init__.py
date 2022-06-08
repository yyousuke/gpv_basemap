#
#  2021/06/01 Yamashita
#
import os
import subprocess
import argparse
import numpy as np
from .cutil import ColUtils
from .cbar import val2col

# ファイルが保存された入力ディレクトリのデフォルト（webから新規取得：retrieve）
input_dir_default = "retrieve"

# 予報時刻からの経過時間、１時間毎に指定可能
fcst_time_default = 36

# 最後に変換前のpngファイルを消すかどうか
opt_remove_png = True

__all__ = ["ColUtils", "val2col"]


def get_gridloc(loc_list, loc):
    """近傍のデータ点取り出し

    Parameters:
    ----------
    loc_list: list(float, float, ...) or numpy.ndarray
        データ点のリスト
    loc: float
        取り出す点
    ----------
    Returns:
    ----------
    iloc: int
        近傍データ点のグリッド番号
    ----------
    """
    r = 360.
    iloc = 0
    for n, x in enumerate(loc_list):
        d = np.absolute(x - loc)
        if d < r:
            r = d
            iloc = n
    return iloc


#
def mktheta(pres, tem, rh):
    """気圧、気温、相対湿度の入力から相当温位、飽和相当温位を求める

    rh = q/qs*100 [%]
    thetae = (tmp + EL/CP * q) * (p00 / p)**(Rd/Cp)
    
    ECMWF
    qs = Rd/Rv*es0/p*exp[
           (Lq+emelt/2.0*(1.0-sign(1.0,T-Tqice))) / Rv*(1.0/Tmelt-1.0/T)]

    Parameters:
    ----------
    pres: float or numpy.ndarray
        気圧 [Pa]
    tem: float or numpy.ndarray
        気温 [K]
    rh: float or numpy.ndarray
        相対湿度 [%]
    ----------
    Returns:
    ----------
    the: float
        相当温位 [K]
    thes: float
        飽和相当温位 [K]
    ----------
    """
    Rd = 287.04  # gas constant of dry air [J/K/kg]
    Rv = 461.50  # gas constant of water vapor [J/K/kg]
    es0 = 610.7  # Saturate pressure of water vapor at 0C [Pa]
    Lq = 2.5008e6  # latent heat for evapolation at 0C [kg/m3]
    emelt = 3.40e5  # Latent heat of melting [kg/m3]
    Tqice = 273.15  # Wet-bulb temp. rain/snow [K]
    Tmelt = 273.15  # Melting temperature of water [K]
    Cp = 1004.6  # specific heat at constant pressure of air (J/K/kg)
    p00 = 100000.0  # reference pressure 1000 [hPa]
    # pres [Pa], tem [K], rh [%]
    # 飽和比湿を求める
    qs = (Rd / Rv * es0 / pres) \
        * np.exp((Lq + emelt / 2.0 * (1.0 - np.sign(tem - Tqice)))
                 / Rv * (1.0 / Tmelt - 1.0 / tem))
    # 比湿を求める
    q = qs * rh * 0.01
    # 相当温位を求める
    the = (tem + Lq / Cp * q) * np.power(p00 / pres, Rd / Cp)
    # 飽和相当温位を求める
    thes = (tem + Lq / Cp * qs) * np.power(p00 / pres, Rd / Cp)
    return (the, thes)


def convert_png2gif(input_filenames, delay="80", output_filename="output.gif"):
    """convertを使い、pngからgifアニメーションに変換する"""
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


def convert_png2mp4(
        input_file="input_%02d.png",
        pfrate="1",  # framerate of input pictures (files/s)
        mfrate="30",  # movie framerate for output (fps)
        output_filename="output.mp4"):
    """ffmpegを使い、pngからmp4アニメーションに変換する"""
    args = [
        "ffmpeg", "-f", "image2", "-framerate", pfrate, "-i", input_file, "-r",
        mfrate, "-an", "-vcodec", "libx264", "-pix_fmt", "yuv420p"
    ]
    print(args)
    args.append(output_filename)
    # 既に出力ファイルがある場合には消す
    if os.path.exists(output_filename):
        os.remove(output_filename)
    # コマンドとオプション入出力ファイルのリストを渡し、変換の実行
    res = subprocess.run(args=args,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    print(res.stdout.decode("utf-8"))
    print(res.stderr.decode("utf-8"))
    if os.path.getsize(output_filename) == 0:
        os.remove(output_filename)


def post(output_filenames):
    """後処理(中間ファイルの削除)

    Parameters:
    ----------
    output_filenames: str
        途中で出力したpngファイル名
    """
    if opt_remove_png:
        for f in output_filenames:
            os.remove(f)


def _construct_parser(opt_sta, opt_lev, opt_dset):
    """ オプションの読み込み

    Parameters:
    ----------
    opt_sta: bool
        地点データを読み込むかどうか
    opt_lev: bool
        気圧面を指定するかどうか
    opt_dset: bool
        GSMかMSMを指定するかどうか
    Returns
    ----------
    parser: argparse.ArgumentParse
        読み込んだオプションのparser
    ----------
    """
    parser = argparse.ArgumentParser(
        description='Matplotlib basemap, weather map')

    parser.add_argument('--fcst_date',
                        type=str,
                        help=('forecast date; yyyymmddhhMMss, or ISO date'),
                        metavar='<fcstdate>')
    parser.add_argument(
        '--fcst_time',
        type=int,
        help=('forecast time; hour (starting from forecast date)'),
        metavar='<fcsttime>')
    if opt_sta:
        parser.add_argument('--sta',
                            type=str,
                            help=('Station name; e.g. Japan, Tokyo,,,'),
                            metavar='<sta>')
    if opt_lev:
        parser.add_argument('--level',
                            type=str,
                            help=('level (hPa); e.g. 925, 850, 700, 500,,,'),
                            metavar='<level>')
    if opt_dset:
        parser.add_argument('--dset',
                            type=str,
                            help=('dataset name: GSM or MSM'),
                            metavar='<dset>')
    parser.add_argument(
        '--input_dir',
        type=str,
        help=
        ('Directory of input files: grib2 (.bin) or NetCDF (.nc); '
         'if --input_dir force_retrieve, download original data from RISH server'
         'if --input_dir retrieve, check avilable download (default)'),
        metavar='<input_dir>')

    return parser


def parse_command(args, opt_sta=True, opt_lev=False, opt_dset=False):
    """ オプションの読み込み

    Parameters:
    ----------
    opt_sta: bool
        地点データを読み込むかどうか（デフォルト：True）
    opt_lev: bool
        気圧面を指定するかどうか（デフォルト：False）
    opt_dset: bool
        GSMかMSMを指定するかどうか（デフォルト：False）
    Returns
    ----------
    parsed_args: argparse.ArgumentParse
        読み込んだオプションのparser
    ----------
    """
    parser = _construct_parser(opt_sta, opt_lev, opt_dset)
    parsed_args = parser.parse_args(args[1:])
    if parsed_args.input_dir is None:
        parsed_args.input_dir = input_dir_default
    if parsed_args.fcst_time is None:
        parsed_args.fcst_time = fcst_time_default
    if opt_lev:
        if parsed_args.level is None:
            parsed_args.level = 850
    if opt_dset:
        if parsed_args.dset is None:
            parsed_args.dset = "GSM"
    return parsed_args
