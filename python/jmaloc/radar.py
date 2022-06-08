#
#  2018/06/21 Yamashita
#  レーダー・ナウキャストの区分で作図範囲を返す
#
class MapRegion():
    """レーダー・ナウキャストの区分で作図範囲を返す"""

    def __init__(self, sta):
        """領域情報を設定

        Parameters:
        ----------
        sta: str
            作図する地域名
        ---------
        """
        self.sta = sta
        self.lon_step = None
        self.lon_min = None
        self.lon_max = None
        self.lat_step = None
        self.lat_min = None
        self.lat_max = None
        # 作図範囲の指定
        # 日本周辺
        if sta == "Japan":
            self.lon_step = 5
            self.lon_min = 120.0
            self.lon_max = 150.0
            self.lat_step = 5
            self.lat_min = 22.4
            self.lat_max = 47.5
        # 北海道（北西部）
        if sta == "Rumoi":
            self.lon_step = 1
            self.lon_min = 139.0
            self.lon_max = 146.0
            self.lat_step = 1
            self.lat_min = 41.0
            self.lat_max = 46.0
        # 北海道（東部）
        if sta == "Abashiri":
            self.lon_step = 1
            self.lon_min = 141.0
            self.lon_max = 148.0
            self.lat_step = 1
            self.lat_min = 41.0
            self.lat_max = 46.0
        # 北海道（南西部）
        if sta == "Sapporo":
            self.lon_step = 1
            self.lon_min = 138.0
            self.lon_max = 145.0
            self.lat_step = 1
            self.lat_min = 40.0
            self.lat_max = 45.0
        # 東北地方（北部）
        if sta == "Akita" or sta == "Morioka":
            self.lon_step = 1
            self.lon_min = 138.0
            self.lon_max = 145.0
            self.lat_step = 1
            self.lat_min = 37.0
            self.lat_max = 42.0
        # 東北地方（南部）
        if sta == "Sendai" or sta == "Fukushima" or sta == "Yamagata":
            self.lon_step = 1
            self.lon_min = 137.0
            self.lon_max = 144.0
            self.lat_step = 1
            self.lat_min = 35.0
            self.lat_max = 40.0
        # 関東地方
        if sta == "Tokyo" or sta == "Kanto":
            self.lon_step = 1
            self.lon_min = 136.0
            self.lon_max = 143.0
            self.lat_step = 1
            self.lat_min = 33.0
            self.lat_max = 38.0
        # 甲信地方
        if sta == "Kofu" or sta == "Kousin":
            self.lon_step = 1
            self.lon_min = 135.0
            self.lon_max = 142.0
            self.lat_step = 1
            self.lat_min = 34.0
            self.lat_max = 39.0
        # 北陸地方（東部）
        if sta == "Niigata":
            self.lon_step = 1
            self.lon_min = 135.0
            self.lon_max = 142.0
            self.lat_step = 1
            self.lat_min = 35.0
            self.lat_max = 40.0
        # 北陸地方（西部）
        if sta == "Kanazawa" or sta == "Fukui" or sta == "Toyama":
            self.lon_step = 1
            self.lon_min = 134.0
            self.lon_max = 141.0
            self.lat_step = 1
            self.lat_min = 34.0
            self.lat_max = 39.0
        # 東海地方
        if sta == "Nagoya" or sta == "Shizuoka" or sta == "Tokai":
            self.lon_step = 1
            self.lon_min = 135.0
            self.lon_max = 143.0
            self.lat_step = 1
            self.lat_min = 32.0
            self.lat_max = 37.0
        # 近畿地方
        if sta == "Osaka" or sta == "Kinki":
            self.lon_step = 1
            self.lon_min = 132.0
            self.lon_max = 139.0
            self.lat_step = 1
            self.lat_min = 32.0
            self.lat_max = 37.0
        # 中国地方
        if sta == "Okayama" or sta == "Hiroshima" or sta == "Tyugoku":
            self.lon_step = 1
            self.lon_min = 130.0
            self.lon_max = 137.0
            self.lat_step = 1
            self.lat_min = 33.0
            self.lat_max = 38.0
        # 四国地方
        if sta == "Kochi" or sta == "Shikoku":
            self.lon_step = 1
            self.lon_min = 130.0
            self.lon_max = 137.0
            self.lat_step = 1
            self.lat_min = 31.0
            self.lat_max = 36.0
        # 九州地方（北部）
        if sta == "Fukuoka":
            self.lon_step = 1
            self.lon_min = 127.0
            self.lon_max = 134.0
            self.lat_step = 1
            self.lat_min = 31.0
            self.lat_max = 36.0
        # 九州地方（南部）
        if sta == "Kagoshima":
            self.lon_step = 1
            self.lon_min = 127.0
            self.lon_max = 134.0
            self.lat_step = 1
            self.lat_min = 29.0
            self.lat_max = 34.0
        # 奄美地方
        if sta == "Naze" or sta == "Amami":
            self.lon_step = 1
            self.lon_min = 126.0
            self.lon_max = 133.0
            self.lat_step = 1
            self.lat_min = 26.0
            self.lat_max = 31.0
        # 沖縄本島地方
        if sta == "Naha" or sta == "Okinawa":
            self.lon_step = 1
            self.lon_min = 124.0
            self.lon_max = 131.0
            self.lat_step = 1
            self.lat_min = 24.0
            self.lat_max = 29.0
        #  大東島地方
        if sta == "Daitojima":
            self.lon_step = 1
            self.lon_min = 126.0
            self.lon_max = 133.0
            self.lat_step = 1
            self.lat_min = 24.0
            self.lat_max = 29.0
        # 宮古・八重山地方
        if sta == "Miyakojima":
            self.lon_step = 1
            self.lon_min = 121.0
            self.lon_max = 128.0
            self.lat_step = 1
            self.lat_min = 22.0
            self.lat_max = 27.0
