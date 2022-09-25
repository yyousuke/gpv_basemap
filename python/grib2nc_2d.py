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
        取り出した2次元データを辞書形式で返却する
    ----------
    """
    if dset == "GSM":
        # ReadGSM初期化
        gpv = ReadGSM(tsel, file_dir, "surf")
    elif dset == "MSM":
        # ReadMSM初期化
        gpv = ReadMSM(tsel, file_dir, "surf")
    else:
        raise ValueError("GSM or MSM")
    #
    # fcst_timeを変えてデータを取り出す
    tind = []
    mslp = []
    rain = []
    tmp = []
    rh = []
    uwnd = []
    vwnd = []
    cfrl = []
    cfrm = []
    cfrh = []
    cfrt = []
    dsrf = []
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
        # 海面更生気圧を二次元のndarrayで取り出す
        mslp.append(gpv.ret_var("PRMSL_meansealevel", fact=0.01))  # (hPa)
        # 降水量を二次元のndarrayで取り出す
        rain.append(gpv.ret_var("APCP_surface"))  # (mm/h)
        if dset == "GSM":
            # GSMの気温を二次元のndarrayで取り出す (K->℃)
            tmp.append(gpv.ret_var("TMP_2maboveground", offset=-273.15))  # (℃)
            # GSMの相対湿度を二次元のndarrayで取り出す
            rh.append(gpv.ret_var("RH_2maboveground"))  # (%)
        elif dset == "MSM":
            # MSMの気温を二次元のndarrayで取り出す (K->℃)
            tmp.append(gpv.ret_var("TMP_1D5maboveground",
                                   offset=-273.15))  # (℃)
            # MSMの相対湿度を二次元のndarrayで取り出す
            rh.append(gpv.ret_var("RH_1D5maboveground"))  # (%)
        # 東西風を二次元のndarrayで取り出す
        uwnd.append(gpv.ret_var("UGRD_10maboveground"))  # (m/s)
        # 南北風を二次元のndarrayで取り出す
        vwnd.append(gpv.ret_var("VGRD_10maboveground"))  # (m/s)
        # 下層雲量を二次元のndarrayで取り出す
        cfrl.append(gpv.ret_var("LCDC_surface"))  # (%)
        # 中層雲量を二次元のndarrayで取り出す
        cfrm.append(gpv.ret_var("MCDC_surface"))  # (%)
        # 上層雲量を二次元のndarrayで取り出す
        cfrh.append(gpv.ret_var("HCDC_surface"))  # %()
        # 全雲量を二次元のndarrayで取り出す
        cfrt.append(gpv.ret_var("TCDC_surface"))  # (%)
        # 下向き短波放射フラックスを二次元のndarrayで取り出す
        dsrf.append(gpv.ret_var("DSWRF_surface"))  # (W/m2)
        # ファイルを閉じる
        gpv.close_netcdf()
        #
    # 3次元配列に変換
    mslp = np.array(mslp)
    rain = np.array(rain)
    tmp = np.array(tmp)
    rh = np.array(rh)
    uwnd = np.array(uwnd)
    vwnd = np.array(vwnd)
    cfrl = np.array(cfrl)
    cfrm = np.array(cfrm)
    cfrh = np.array(cfrh)
    cfrt = np.array(cfrt)
    dsrf = np.array(dsrf)
    # データを返却
    return {
        "longitude": lons_1d,
        "latitude": lats_1d,
        "level": np.ones(1) * 1000.0,
        "time": tind,
        "mslp": mslp,
        "rain": rain,
        "tmp": tmp,
        "rh": rh,
        "uwnd": uwnd,
        "vwnd": vwnd,
        "cfrh": cfrh,
        "cfrm": cfrm,
        "cfrl": cfrl,
        "cfrt": cfrt,
        "dsrf": dsrf,
    }


def writenc(d, info_json_path="output.json", output_nc_path="test.nc"):
    """ NetCDFファイルとして書き出す

    Parameters:
    ----------
    d: dict of keys and ndarray value
        書き出すデータを変数名をキー、ndarrayを値とした辞書で与える
    info_json_path: str
        書き出すデータの情報を記述したJSONファイルのパス
    output_nc_path: str
        書き出すNetCDFファイルのパス
    ----------
    """
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
        # 読み込んだGPVデータから軸のデータを取り出す
        dat = np.array(d[k])
        # DataFrameから軸に対応する辞書を取り出し
        # 軸情報をNetCDFファイルに追加
        nc.create_axis(dat, **df.loc[:, k])
        if verbose:
            print("write: ", k, dat.shape)

    # 変数の情報をDataFrameにする
    df = pd.DataFrame(json.loads(data)["variable_entry"])
    for k in df.columns:  # DataFrameの列をキーに
        # 読み込んだGPVデータから軸のデータを取り出す
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
    # 予報時刻からの経過時間（1時間毎に指定可能）
    fcst_end = args.fcst_time
    fcst_str = 0  # 開始時刻
    fcst_step = 1  # 作図する間隔
    # datetimeに変換
    tinfo = pd.to_datetime(fcst_date)
    tsel = tinfo.strftime("%Y%m%d%H%M%S")
    #
    # NetCDFデータ読み込み(変数名をキーとした辞書型で格納)
    d = readnc(tsel, dset, file_dir, fcst_str, fcst_end, fcst_step)

    # NetCDFデータ書き出し
    output_filename = "Z__C_RJTD_" + tsel + "_" + dset + "_GPV_Rjp_Lsurf.nc"
    writenc(d,
            info_json_path="output_sur.json",
            output_nc_path=output_filename)
