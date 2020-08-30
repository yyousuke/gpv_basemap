#!/opt/local/bin/python3
import sys
import subprocess

fcst_date = "20200830000000" # UTC

stations = ["Japan", "Tokyo"]
#progs = ["python/readgrib_gsm_mslp_reg.py"]
progs = ["python/readgrib_gsm_mslp_reg.py", "python/readgrib_msm_ept_reg.py", "python/readgrib_msm_mslp_reg.py", "python/readgrib_gsm_rain_sum_reg.py", "python/readgrib_msm_rain_sum_reg.py", "python/readgrib_msm_stemp_reg.py", "python/readgrib_msm_temp_reg.py"]
progs_tvar = ["python/readgrib_msm_tvar_reg.py", "python/readgrib_gsm_tvar_reg.py"]

if __name__ == '__main__':
    for sta in stations:
        for prog in progs:
            res = subprocess.run([prog, "--fcst_date", fcst_date, "--sta", sta], stdout=subprocess.PIPE, stderr = subprocess.PIPE)
            print(res.stdout.decode("utf-8"))

    sta = "Tokyo"
    for prog in progs_tvar:
            res = subprocess.run([prog, "--fcst_date", fcst_date, "--sta", sta], stdout=subprocess.PIPE, stderr = subprocess.PIPE)
            print(res.stdout.decode("utf-8"))

