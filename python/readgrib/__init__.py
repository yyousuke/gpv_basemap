#
#  2020/03/30 Yamashita
#
import sys
import os
import subprocess
import urllib.request
import netCDF4
import numpy as np

# 入力する気象庁GPVデータのファイルを置いたディレクトリ
sys_file_dir = os.environ.get('DATADIR_GPV', '/data')

# URL
url = "http://database.rish.kyoto-u.ac.jp/arch/jmadata/data/gpv/original"

### utils ###

# gribファイル
def ret_grib(tsel, file_name_g2, file_name_nc, force=False):
    # files for search
    file_dir_names = [
      file_name_nc,
      file_name_g2,
      sys_file_dir + "/" + file_name_nc,
      sys_file_dir + "/" + file_name_g2
    ]
    file_dir_convs = [ False, True, False, True ]
    opt_retrieve = True
    opt_convert = True
    if not force:
        for file_dir_name, file_dir_conv in zip(file_dir_names, file_dir_convs):
            if os.path.isfile(file_dir_name):
                opt_retrieve = False
                opt_convert = file_dir_conv
                break
    # retrieve
    if opt_retrieve:
        url_dir_file = url + "/" + tsel[0:4] + "/" + tsel[4:6] + "/" + tsel[6:8] + "/" + file_name_g2
        urllib.request.urlretrieve(url_dir_file, file_name_g2)
        file_dir_name = file_name_g2
        if not os.path.isfile(file_name_g2):
            print("Download failed...") ; quit()
    #
    # convert
    if opt_convert:
        res = subprocess.run(["wgrib2", file_dir_name, "-netcdf", file_name_nc], stdout=subprocess.PIPE, stderr = subprocess.PIPE)
        print(res.stdout.decode("utf-8"))
        file_dir_name = file_name_nc
        if not os.path.isfile(file_name_nc):
            print("Convert failed...") ; quit()
    return file_dir_name
#  dir="${yyyy}/${mm}/${dd}"
#  file="Z__C_RJTD_${yyyy}${mm}${dd}${hh}0000_MSM_GPV_Rjp_${flag}_grib2.bin"
#  nc="Z__C_RJTD_${yyyy}${mm}${dd}${hh}0000_MSM_GPV_Rjp_${flag}_grib2.nc"
#  ${WGET} ${URL}/${dir}/${file} >> ${log} 2>&1 || exit 1
#  ${WGRIB2} ${file} -netcdf ${nc} >> ${log} 2>&1 || exit 1
#
# netCDFファイルを読み込む(surf)
def readnetcdf_msm_surf(msm_dir, fcst_time, tsel):
    if fcst_time <= 15:
        fcst_flag="00-15"
        rec_num = fcst_time
    elif fcst_time <= 33:
        fcst_flag="16-33"
        rec_num = fcst_time - 16
    else:
        fcst_flag="34-39"
        rec_num = fcst_time - 34
    # ファイル名
    file_name_g2 = "Z__C_RJTD_"+str(tsel)+"_MSM_GPV_Rjp_Lsurf_FH"+str(fcst_flag)+"_grib2.bin"
    file_name_nc = "Z__C_RJTD_"+str(tsel)+"_MSM_GPV_Rjp_Lsurf_FH"+str(fcst_flag)+"_grib2.nc"
    #
    if msm_dir == "retrieve":
        file_dir_name = ret_grib(tsel, file_name_g2, file_name_nc, force=False)
    elif msm_dir == "force_retrieve":
        file_dir_name = ret_grib(tsel, file_name_g2, file_name_nc, force=True)
        msm_dir = "retrieve"
    else:
        file_dir_name = msm_dir + "/" + file_name_nc
    return rec_num, file_dir_name
#
# netCDFファイルを読み込む(pres)
def readnetcdf_msm_plev(msm_dir, fcst_time, tsel):
    if fcst_time <= 15:
        fcst_flag="00-15"
        rec_num = fcst_time // 3
    elif fcst_time <= 33:
        fcst_flag="18-33"
        rec_num = (fcst_time - 18) // 3
    else:
        fcst_flag="36-39"
        rec_num = (fcst_time - 36) // 3
    # ファイル名
    file_name_g2 = "Z__C_RJTD_"+str(tsel)+"_MSM_GPV_Rjp_L-pall_FH"+str(fcst_flag)+"_grib2.bin"
    file_name_nc = "Z__C_RJTD_"+str(tsel)+"_MSM_GPV_Rjp_L-pall_FH"+str(fcst_flag)+"_grib2.nc"
    #
    if msm_dir == "retrieve":
        file_dir_name = ret_grib(tsel, file_name_g2, file_name_nc, force=False)
    elif msm_dir == "force_retrieve":
        file_dir_name = ret_grib(tsel, file_name_g2, file_name_nc, force=True)
        msm_dir = "retrieve"
    else:
        file_dir_name = msm_dir + "/" + file_name_nc
    return rec_num, file_dir_name

#
# netCDFファイルを読み込む(gsm, surf)
def readnetcdf_gsm_surf(gsm_dir, fcst_time, tsel):
    if fcst_time <= 84:
        fcst_flag="0000-0312"
        rec_num = fcst_time
    elif fcst_time <= 192:
        fcst_flag="0315-0800"
        rec_num = fcst_time - 87
    else:
        fcst_flag="0803-1100"
        rec_num = fcst_time - 195
    # ファイル名
    file_name_g2 = "Z__C_RJTD_"+str(tsel)+"_GSM_GPV_Rjp_Lsurf_FD"+str(fcst_flag)+"_grib2.bin"
    file_name_nc = "Z__C_RJTD_"+str(tsel)+"_GSM_GPV_Rjp_Lsurf_FD"+str(fcst_flag)+"_grib2.nc"
    #
    if gsm_dir == "retrieve":
        file_dir_name = ret_grib(tsel, file_name_g2, file_name_nc, force=False)
    elif gsm_dir == "force_retrieve":
        file_dir_name = ret_grib(tsel, file_name_g2, file_name_nc, force=True)
        gsm_dir = "retrieve"
    else:
        file_dir_name = gsm_dir + "/" + file_name_nc
    return rec_num, file_dir_name
#
# netCDFファイルを読み込む(gsm, pres)
def readnetcdf_gsm_plev(gsm_dir, fcst_time, tsel):
    if fcst_time <= 84:
        fcst_flag="0000-0312"
        rec_num = fcst_time
    elif fcst_time <= 192:
        fcst_flag="0318-0800"
        rec_num = fcst_time - 90
    else:
        fcst_flag="0806-1100"
        rec_num = fcst_time - 198
    # ファイル名
    file_name_g2 = "Z__C_RJTD_"+str(tsel)+"_GSM_GPV_Rjp_L-pall_FD"+str(fcst_flag)+"_grib2.bin"
    file_name_nc = "Z__C_RJTD_"+str(tsel)+"_GSM_GPV_Rjp_L-pall_FD"+str(fcst_flag)+"_grib2.nc"
    #
    if gsm_dir == "retrieve":
        file_dir_name = ret_grib(tsel, file_name_g2, file_name_nc, force=False)
    elif gsm_dir == "force_retrieve":
        file_dir_name = ret_grib(tsel, file_name_g2, file_name_nc, force=True)
        gsm_dir = "retrieve"
    else:
        file_dir_name = gsm_dir + "/" + file_name_nc
    return rec_num, file_dir_name

### utils ###

##############################################################################

class ReadMSM():
    def __init__(self, tsel, msm_dir, msm_lev):
        self.tsel = tsel
        self.msm_dir = msm_dir
        self.msm_lev = msm_lev 
        self.fcst_time = -1
        self.rec_num = -1
        self.nc = None
        if msm_lev == "surf" or msm_lev == "plev":
            print("data lev =", msm_lev, ", fcst_time =", tsel)
        else:
            print("not supported: msm_lev =", msm_lev) ; quit()
    # fcst_timeの設定
    def set_fcst_time(self, fcst_time):
        self.fcst_time = fcst_time
    # fcst_timeの取得
    def get_fcst_time(self):
        return self.fcst_time
    # 
    # netCDFファイルを読み込む
    def readnetcdf(self):
        tsel = self.tsel
        msm_dir = self.msm_dir
        msm_lev = self.msm_lev
        fcst_time = self.fcst_time
        # fcst_timeに対応した表面(surf)か気圧面(plev)データ名取得
        # 必要ならgribからNetcdfへの変換を行う
        if msm_lev == "surf":
            rec_num, file_dir_name = readnetcdf_msm_surf(msm_dir, fcst_time, tsel)
        elif msm_lev == "plev":
            rec_num, file_dir_name = readnetcdf_msm_plev(msm_dir, fcst_time, tsel)
        self.rec_num = rec_num
        #
        # NetCDFデータの読み込み
        nc = netCDF4.Dataset(file_dir_name, 'r')
        self.nc = nc 
        # データサイズの取得
        idim = len(nc.dimensions['longitude'])
        jdim = len(nc.dimensions['latitude'])
        num_rec = len(nc.dimensions['time'])
        print("num_lon =", idim, ", num_lat =", jdim, ", num_time =", num_rec)
        # 変数の読み込み(一次元)
        lons_1d = nc.variables["longitude"][:]
        lats_1d = nc.variables["latitude"][:]
        time = nc.variables["time"][:]
        # lons, lats: 二次元配列に変換
        lons, lats = np.meshgrid(lons_1d, lats_1d)
        print("lon:", lons.shape)
        print("lat:", lats.shape)
        return lons_1d, lats_1d, lons, lats
    #
    # 中に含まれているデータを二次元のndarrayで取り出す
    def ret_var(self, var_name, fact=1.0, offset=0.0):
        fcst_time = self.fcst_time
        rec_num = self.rec_num
        nc = self.nc
        # 降水量の場合 (mm/h)
        if var_name == "APCP_surface":
            # データを取り出し、factを掛けoffsetを足す
            if fcst_time == 0:
                # データがないため、+0hのみ後１時間降水量(kg/m2) (1000mm->1000kg/m2)
                #d = nc.variables[var_name][1] * fact + offset
                # データがないため、+0hのみ0 (kg/m2) (1000mm->1000kg/m2)
                d = nc.variables[var_name][1] * 0.0
            else:
                # 前１時間降水量(kg/m2) (1000mm->1000kg/m2)
                d = nc.variables[var_name][rec_num] * fact + offset
        # 他のデータの場合
        else:
            # データを取り出し、factを掛けoffsetを足す
            d = nc.variables[var_name][rec_num] * fact + offset
        #
        print(var_name, d.shape)
        return d
    #
    # Netcdfファイルを閉じる
    def close_netcdf(self):
        nc = self.nc
        nc.close()


##############################################################################

class ReadGSM():
    def __init__(self, tsel, gsm_dir, gsm_lev):
        self.tsel = tsel
        self.gsm_dir = gsm_dir
        self.gsm_lev = gsm_lev 
        self.fcst_time = -1
        self.rec_num = -1
        self.nc = None
        if gsm_lev == "surf" or gsm_lev == "plev":
            print("data lev =", gsm_lev, ", fcst_time =", tsel)
        else:
            print("not supported: gsm_lev =", gsm_lev) ; quit()
    # fcst_timeの設定
    def set_fcst_time(self, fcst_time):
        self.fcst_time = fcst_time
    # fcst_timeの取得
    def get_fcst_time(self):
        return self.fcst_time
    # 
    # netCDFファイルを読み込む
    def readnetcdf(self):
        tsel = self.tsel
        gsm_dir = self.gsm_dir
        gsm_lev = self.gsm_lev
        fcst_time = self.fcst_time
        # fcst_timeに対応した表面(surf)か気圧面(plev)データ名取得
        # 必要ならgribからNetcdfへの変換を行う
        if gsm_lev == "surf":
            rec_num, file_dir_name = readnetcdf_gsm_surf(gsm_dir, fcst_time, tsel)
        elif gsm_lev == "plev":
            rec_num, file_dir_name = readnetcdf_gsm_plev(gsm_dir, fcst_time, tsel)
        self.rec_num = rec_num
        #
        # NetCDFデータの読み込み
        nc = netCDF4.Dataset(file_dir_name, 'r')
        self.nc = nc 
        # データサイズの取得
        idim = len(nc.dimensions['longitude'])
        jdim = len(nc.dimensions['latitude'])
        num_rec = len(nc.dimensions['time'])
        print("num_lon =", idim, ", num_lat =", jdim, ", num_time =", num_rec)
        # 変数の読み込み(一次元)
        lons_1d = nc.variables["longitude"][:]
        lats_1d = nc.variables["latitude"][:]
        time = nc.variables["time"][:]
        # lons, lats: 二次元配列に変換
        lons, lats = np.meshgrid(lons_1d, lats_1d)
        print("lon:", lons.shape)
        print("lat:", lats.shape)
        return lons_1d, lats_1d, lons, lats
    #
    # 中に含まれているデータを二次元のndarrayで取り出す
    def ret_var(self, var_name, fact=1.0, offset=0.0, cum_rain=False):
        fcst_time = self.fcst_time
        rec_num = self.rec_num
        nc = self.nc
        # 降水量の場合 (mm/h)
        if var_name == "APCP_surface":
            # データを取り出し、factを掛けoffsetを足す
            if fcst_time == 0:
                # データがないため、+0hのみ後１時間降水量(kg/m2) (1000mm->1000kg/m2)
                #d = nc.variables[var_name][1] * fact + offset
                # データがないため、+0hのみ0 (kg/m2) (1000mm->1000kg/m2)
                d = nc.variables[var_name][1] * 0.0
            elif fcst_time == 1:
                # 前１時間降水量(kg/m2) (1000mm->1000kg/m2)
                d = nc.variables[var_name][rec_num] * fact + offset
            else:
                if cum_rain: # 累積降水量
                    # 累積降水量(kg/m2) (1000mm->1000kg/m2)
                    d = nc.variables[var_name][rec_num] * fact + offset
                else: # 前１時間降水量
                    # d0、d1には累積降水量(kg/m2)が入っている
                    d0 = nc.variables[var_name][rec_num-1] * fact + offset
                    d1 = nc.variables[var_name][rec_num] * fact + offset
                    # 前１時間降水量(kg/m2) (1000mm->1000kg/m2)
                    d = d1 - d0
        #
        # 他のデータの場合
        else:
            # データを取り出し、factを掛けoffsetを足す
            d = nc.variables[var_name][rec_num] * fact + offset
        #
        print(var_name, d.shape)
        return d
    #
    # Netcdfファイルを閉じる
    def close_netcdf(self):
        nc = self.nc
        nc.close()


