#!/opt/local/bin/python3
import sys
import subprocess
from datetime import datetime, timedelta

fcst_date = "20210710120000"  # UTC

# 水平分布
stations = ["Japan", "Tokyo"]
# GSM
progs_gsm = [
    "python/readgrib_gsm_mslp_reg.py", "python/readgrib_gsm_rain_sum_reg.py",
    "python/readgrib_msm_temp_reg.py",
    "python/readgrib_gsm_ccover_reg.py"
]
# MSM
progs_msm = [
    "python/readgrib_msm_mslp_reg.py", "python/readgrib_msm_rain_sum_reg.py",
    "python/readgrib_msm_temp_reg.py",
    "python/readgrib_msm_ccover_reg.py", "python/readgrib_msm_ept_reg.py",
    "python/readgrib_msm_stemp_reg.py", "python/readgrib_msm_temp_reg.py"
]

# 時系列図（アメダス地点名）
stations_tvar = ["Tokyo"]
progs_tvar = [
    "python/readgrib_msm_tvar_reg.py", "python/readgrib_gsm_tvar_reg.py"
]
times_tvar = ["36", "72"]

if __name__ == '__main__':
    # 5時間前に設定
    time = datetime.utcnow() - timedelta(hours=5)
    fcst_date = time.strftime("%Y%m%d%H") + "0000"
    print(fcst_date)
    hh = time.strftime("%H")
    opt_gsm = False
    if hh == "00" or hh == "06" or hh == "12" or hh == "18":
        opt_gsm = True  # GSMも作図する場合（00, 06, 12, 18UTCのみ）
    #
    progs = progs_msm
    if opt_gsm:
        progs.extend(progs_gsm)
    for sta in stations:
        for p in progs:
            res = subprocess.run([p, "--fcst_date", fcst_date, "--sta", sta],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            print(res.stdout.decode("utf-8"))
            print(res.stderr.decode("utf-8"))

    for sta in stations_tvar:
        for p, t in zip(progs_tvar, times_tvar):
            res = subprocess.run(
                [p, "--fcst_date", fcst_date, "--sta", sta, "--fcst_time", t],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            print(res.stdout.decode("utf-8"))
            print(res.stderr.decode("utf-8"))
