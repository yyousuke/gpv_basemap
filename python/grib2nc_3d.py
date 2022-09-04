#!/opt/local/bin/python3
import pandas as pd
import numpy as np
import json
import sys
from datetime import timedelta
from readgrib import ReadGSM, ReadMSM
from writenc import WriteNC
from writenc import count_dind
from utils import parse_command

# pressure levels
plevs = [
    1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 250, 200, 150,
    100
]

# for debug
verbose = True
# verbose = False


def readnc(tsel, dset, file_dir, fcst_str, fcst_end, fcst_step):
    """ NetCDFファイルを読み込みデータを返却

    Parameters:
    ----------
    tsel: str
        取得する予報時刻（形式：20210819120000）
    dset: str
        GSMかMSMを指定する
    fcst_str: int
        取得開始時刻を予報時刻からの時間（h）で与える
    fcst_end: int
        取得終了時刻を予報時刻からの時間（h）で与える
    fcst_step: int
        取得間隔を時間（h）で与える
    Returns
    ----------
    dict of keys and ndarray value
        取り出した3次元データを辞書形式で返却する
    ----------
    """
    if dset == "GSM":
        # ReadGSM初期化
        gpv = ReadGSM(tsel, file_dir, "plev")
    elif dset == "MSM":
        # ReadMSM初期化
        gpv = ReadMSM(tsel, file_dir, "plev")
    else:
        raise ValueError("GSM or MSM")
    #
    # fcst_timeを変えてplotmapを実行
    tind = []
    tmp = []
    rh = []
    uwnd = []
    vwnd = []
    omg = []
    hgt = []
    for fcst_time in np.arange(fcst_str, fcst_end + 1, fcst_step):
        # fcst_timeを設定
        gpv.set_fcst_time(fcst_time)
        # 時刻情報を設定
        tinfo_fcst = tinfo + timedelta(hours=int(fcst_time))
        days = count_dind(start_year=1970,
                          start_month=1,
                          start_day=1,
                          end_year=tinfo_fcst.year,
                          end_month=tinfo_fcst.month,
                          end_day=tinfo_fcst.day)
        # 時刻(seconds from 1970-01-01)
        tind.append(days * 86400 + tinfo_fcst.hour * 3600)
        # NetCDFデータ読み込み
        lons_1d, lats_1d, lons, lats = gpv.readnetcdf()
        # 変数取り出し
        # 気温を3次元のndarrayで取り出す
        tmp.append(gpv.ret_var_3d("TMP", plevs))  # (K)
        # 相対湿度データを3次元のndarrayで取り出す ()
        rh_i = np.zeros((len(plevs), len(lats_1d), len(lons_1d)))
        rh_i[0:12, :, :] = gpv.ret_var_3d("RH", plevs[0:12])
        rh.append(rh_i)  # (%)
        # 東西風、南北風を3次元のndarrayで取り出す
        uwnd.append(gpv.ret_var_3d("UGRD", plevs))  # (m/s)
        vwnd.append(gpv.ret_var_3d("VGRD", plevs))  # (m/s)
        # 鉛直速度を3次元のndarrayで取り出す
        omg.append(gpv.ret_var_3d("VVEL", plevs))  # (Pa/s)
        # ジオポテンシャル高度を3次元のndarrayで取り出す
        hgt.append(gpv.ret_var_3d("HGT", plevs))  # (m)
        # ファイルを閉じる
        gpv.close_netcdf()
        #
    # 4次元配列に変換
    tmp = np.array(tmp)
    rh = np.array(rh)
    uwnd = np.array(uwnd)
    vwnd = np.array(vwnd)
    omg = np.array(omg)
    hgt = np.array(hgt)
    # データを返却
    return {
        "longitude": lons_1d,
        "latitude": lats_1d,
        "level": plevs,
        "time": tind,
        "tmp": tmp,
        "rh": rh,
        "uwnd": uwnd,
        "vwnd": vwnd,
        "omg": omg,
        "hgt": hgt
    }


def writenc(d, info_json_path="output.json", output_nc_path="test.nc"):
    # JSONデータ読み込み
    with open(info_json_path, 'rt') as fin:
        data = fin.read()
    # NetCDFデータ作成
    nc = WriteNC(output_nc_path, force=True)
    # ヘッダ情報を辞書に格納
    header = dict(json.loads(data)["Header"])
    # ヘッダ情報をNetCDFファイルに追加
    nc.set_gattr(**header)
    # 複数の軸情報をDataFrameにする
    df = pd.DataFrame(json.loads(data)["axis_entry"]).fillna("NaN")
    for k in df.columns:  # DataFrameの列をキーに
        # 読み込んだCFSRデータから軸のデータを取り出す
        dat = np.array(d[k])
        # DataFrameから軸に対応する辞書を取り出し
        # 軸情報をNetCDFファイルに追加
        nc.create_axis(dat, **df.loc[:, k])
        if verbose:
            print("write: ", k, dat.shape)

    # 変数の情報をDataFrameにする
    df = pd.DataFrame(json.loads(data)["variable_entry"])
    for k in df.columns:  # DataFrameの列をキーに
        # 読み込んだCFSRデータから軸のデータを取り出す
        dat = np.array(d[k])
        # DataFrameから変数に対応する辞書を取り出し
        # 変数情報をNetCDFファイルに追加
        nc.create_var(dat, **df.loc[:, k])
        if verbose:
            print("write: ", k, dat.shape)
    # ファイルを閉じる
    nc.close_netcdf()


if __name__ == '__main__':
    # オプションの読み込み
    args = parse_command(sys.argv, opt_sta=False, opt_dset=True)
    # 予報時刻の指定
    fcst_date = args.fcst_date
    file_dir = args.input_dir
    # GSM/MSMの指定
    dset = args.dset
    # 予報時刻からの経過時間（3時間毎に指定可能）
    fcst_end = args.fcst_time
    fcst_str = 0  # 開始時刻
    fcst_step = 3  # 作図する間隔
    # datetimeに変換
    tinfo = pd.to_datetime(fcst_date)
    tsel = tinfo.strftime("%Y%m%d%H%M%S")
    #
    # NetCDFデータ読み込み(変数名をキーとした辞書型で格納)
    d = readnc(tsel, dset, file_dir, fcst_str, fcst_end, fcst_step)

    # NetCDFデータ書き出し
    output_filename = "Z__C_RJTD_" + tsel + "_" + dset + "_GPV_Rjp_L-pall.nc"
    writenc(d, info_json_path="output.json", output_nc_path=output_filename)
