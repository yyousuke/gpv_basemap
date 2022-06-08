#
#  2020/03/30 Yamashita: first ver.
#  2022/05/09 Yamashita: WriteNC class
#
import netCDF4
import numpy as np
from datetime import datetime, timedelta
import uuid
import array
import os
import sys


def _get_creation_date():
    """作成時刻を返す"""
    return datetime.utcnow().strftime('%Y-%m-%d-T%H:%M:%SZ')


def _get_uuid():
    """ランダムなUUIDを返す"""
    return str(uuid.uuid4())


def _get_data_range(d):
    """データの範囲を返す"""
    return np.min(d), np.max(d)


def _str2bool(s):
    """文字列からboolへの変換"""
    return s.lower() in ["true", "t", "yes", "1"]


def _dim2tuple(s):
    """次元表記からtupleへの変換"""
    return tuple(s.split(' '))


def _npconvert(v, dtype='double'):
    """データ型の変換"""
    if dtype == "char" or dtype == "int8" or dtype == "i1":
        return np.int8(v)
    elif dtype == "short" or dtype == "int16" or dtype == "i2":
        return np.int16(v)
    elif dtype == "int" or dtype == "int32" or dtype == "i4":
        return np.int32(v)
    elif dtype == "long" or dtype == "int64" or dtype == "i8":
        return np.int64(v)
    elif dtype == "uint8" or dtype == "u1":
        return np.uint8(v)
    elif dtype == "uint16" or dtype == "u2":
        return np.uint16(v)
    elif dtype == "uint32" or dtype == "u4":
        return np.uint32(v)
    elif dtype == "uint64" or dtype == "u8":
        return np.uint64(v)
    elif dtype == "float16" or dtype == "f2":
        return np.float16(v)
    elif dtype == "float" or dtype == "float32" or dtype == "f4":
        return np.float32(v)
    elif dtype == "double" or dtype == "float64" or dtype == "f8":
        return np.float64(v)
    elif dtype == "long double" or dtype == "float128" or dtype == "f16":
        return np.float128(v)
    elif dtype == "complex" or dtype == "complex64" or dtype == "c8":
        return np.complex64(v)
    elif dtype == "complex128" or dtype == "c16":
        return np.complex128(v)
    elif dtype == "complex256" or dtype == "c32":
        return np.complex256(v)
    elif dtype == "bool" or dtype == "?":
        return np.bool(v)
    elif dtype == "unicode" or dtype == "U":
        return np.unicode(v)
    else:
        return v


def count_dind(start_year=1860,
               start_month=1,
               start_day=1,
               end_year=2000,
               end_month=12,
               end_day=31):
    """日数-1を出力する（indexの開始は0）"""
    ds = datetime(start_year, start_month, start_day, 0, 0, 0)
    de = datetime(end_year, end_month, end_day, 0, 0, 0)
    return (de - ds).days


class WriteNC():
    """ NetCDFファイルを書き出す"""

    def __init__(self, output_filedir="test.nc", force=False):
        """ NetCDFファイルの作成

        Parameters:
        ----------
        output_filedir: str
            出力ファイルへのパス
        force: bool
           ファイルが存在している場合に削除するかどうか
        """
        # ファイルが存在している場合に削除する
        if os.path.isfile(output_filedir):
            if force:
                os.remove(output_filedir)
        # NetCDFファイルを作成
        nc = netCDF4.Dataset(output_filedir, 'w', format='NETCDF3_CLASSIC')
        self.output_filedir = output_filedir
        self.nc = nc

    def create_axis(self,
                    dat,
                    axis='none',
                    standard_name='N/A',
                    long_name='N/A',
                    dimensions='',
                    units='',
                    out_name='var',
                    valid_min='NaN',
                    valid_max='NaN',
                    dtype='double',
                    positive="NaN",
                    calendar="NaN",
                    actual_range='f',
                    **kwargs):
        """軸情報を書き出す
    
        Parameters:
        ----------
        dat: ndarray
            変数の配列
        axis: str
            軸の名前
        standard_name: str
            変数のstandard name
        long_name: str
            変数のlong name
        dimensions: str
            変数の次元
        units: str
            変数の単位
        out_name: str
            出力変数の名前
        valid_min: str or float
            想定される最小値
        valid_max: str or float
            想定される最大値
        dtype: str
            出力変数のデータ型
        positive: str
            正の方向が定義される場合（鉛直のみ）
        calendar: str
            カレンダーの種類（時刻のみ）
        actual_range: str
            実際のデータ範囲を出力する場合はtrue
        \**kwards: dict
            追加のキー、値（エラー抑止のためのダミー）
        """
        nc = self.nc
        # 次元の設定
        nc.createDimension(out_name, len(dat))
        # 変数の設定
        if dtype == "float":  # np defalut: float64
            dtype = "float32"
        var = nc.createVariable(out_name,
                                np.dtype(dtype).char, _dim2tuple(dimensions))
        var.axis = axis
        var.standard_name = standard_name
        var.long_name = long_name
        var.units = units
        if valid_min != "NaN":
            var.valid_min = _npconvert(valid_min, dtype=dtype)
        if valid_max != "NaN":
            var.valid_max = _npconvert(valid_max, dtype=dtype)
        if positive != "NaN":
            var.positive = positive
        if calendar != "NaN":
            var.calendar = calendar
        if _str2bool(actual_range):
            var.actual_range = _get_data_range(dat)
        # 変数の書き出し
        var[:] = dat

    def create_var(self,
                   dat,
                   standard_name='N/A',
                   long_name='N/A',
                   dimensions='',
                   description='',
                   units='',
                   out_name='var',
                   valid_min='NaN',
                   valid_max='NaN',
                   scale_factor=1.0,
                   add_offset=0.0,
                   missing_value=1e20,
                   missing_input=1e20,
                   dtype='double',
                   actual_range='f',
                   **kwargs):
        """軸情報を書き出す
    
        Parameters:
        ----------
        dat: ndarray
            変数の配列
        standard_name: str
            変数のstandard name
        long_name: str
            変数のlong name
        dimensions: str
            変数の次元
        description: str
            変数の説明
        units: str
            変数の単位
        out_name: str
            出力変数の名前
        valid_min: str or float
            想定される最小値
        valid_max: str or float
            想定される最大値
        scale_factor: str or float
            格納するデータのスケールファクター
        add_offset: str or float
            格納するデータのオフセット値
        missing_value: float
            格納するデータの欠損値
        missing_input: float
            入力するデータの欠損値
        dtype: str
            出力変数のデータ型
        actual_range: str
            実際のデータ範囲を出力する場合はtrue
        \**kwards: dict
            追加のキー、値（エラー抑止のためのダミー）
        """
        nc = self.nc
        if dtype == "float":  # np defalut: float64
            dtype = "float32"
        var = nc.createVariable(out_name,
                                np.dtype(dtype).char,
                                _dim2tuple(dimensions),
                                fill_value=_npconvert(missing_value,
                                                      dtype=dtype))
        var.scale_factor = _npconvert(scale_factor)
        var.add_offset = _npconvert(add_offset)
        var.standard_name = standard_name
        var.long_name = long_name
        var.description = description
        var.units = units
        var.valid_min = _npconvert(valid_min, dtype=dtype)
        var.valid_max = _npconvert(valid_max, dtype=dtype)
        var.missing_value = _npconvert(missing_value, dtype=dtype)
        if _str2bool(actual_range):
            var.actual_range = _get_data_range(dat)
        # 欠損処理
        dat[dat == missing_input] = np.nan
        # 変数の書き出し
        if len(_dim2tuple(dimensions)) == 4:
            var[:, :, :, :] = _npconvert(dat, dtype=dtype)
        elif len(_dim2tuple(dimensions)) == 3:
            var[:, :, :] = _npconvert(dat, dtype=dtype)
        elif len(_dim2tuple(dimensions)) == 2:
            var[:, :] = _npconvert(dat, dtype=dtype)
        elif len(_dim2tuple(dimensions)) == 1:
            var[:] = _npconvert(dat, dtype=dtype)

    def set_gattr(self,
                  data_specs_version='',
                  product='output',
                  tracking_id='true',
                  comment='',
                  contact='',
                  references='',
                  Conventions='',
                  dataset='',
                  source='',
                  history='',
                  creation_date='true',
                  created='N/A',
                  **kwargs):
        """Global Attributesを書き出す
    
        Parameters:
        ----------
        data_specs_version: str
            出力データのバージョン
        product: str
            出力変数の種類
        tracking_id: str
            UUIDを追加する場合はtrue
        comment: str
            コメント
        contact: str
            データ作成者の連絡先
        references: str
            規約に関連するreference
        Conventions: str
            NetCDFファイルが準拠する規約
        dataset_name: str
            データセットの名前
        source: str
            データを記述した文献
        history: str
            データの作成、変更履歴の冒頭コメント
        creation_date: str
            データの作成日時を追加する場合はtrue
        created: str
            最初に作成したプログラム名と作成者、更新日、バージョンなど
        \**kwards: dict
            追加のキー、値（エラー抑止のためのダミー）
        """
        nc = self.nc
        # Global Attributes
        nc.data_specs_version = data_specs_version
        nc.product = product
        if _str2bool(tracking_id):
            nc.tracking_id = _get_uuid()
        nc.comment = comment
        nc.contact = contact
        nc.references = references
        nc.Conventions = Conventions
        nc.dataset = dataset
        nc.source = source
        nc.history = history
        if _str2bool(creation_date):
            nc.creation_date = _get_creation_date()
        nc.created = created

    def close_netcdf(self):
        """NetCDFファイルを閉じる"""
        nc = self.nc
        nc.close()
