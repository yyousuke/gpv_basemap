#
#  2021/07/10 Yamashita
#
#  Basemapのcmを用いる
from mpl_toolkits.basemap import cm

# ColUtils: カラーユーティリティ
class ColUtils():
    def __init__(self, cmap_name=None):
        if cmap_name == "s3pcpn_l":
            self.cmap = cm.s3pcpn_l
        elif cmap_name == "wysiwyg" or cmap_name == "GMT_wysiwyg":
            self.cmap = cm.GMT_wysiwyg
        elif cmap_name == "haxby" or cmap_name == "GMT_haxby":
            self.cmap = cm.GMT_haxby
        elif cmap_name == "drywet" or cmap_name == "GMT_drywet":
            self.cmap = cm.GMT_drywet
        elif cmap_name == "no_green" or cmap_name == "GMT_no_green":
            self.cmap = cm.cmap_name
        else:
            try:
                self.cmap = cm.cmap_name
            except:
                raise Exception("invalid cmap_name")

    def get_ctable(self, under=None, over=None):
        # カラーマップ作成
        cmap = self.cmap
        if under is not None:
            cmap.set_under(under)  # 下限を下回った場合の色を指定
        if over is not None:
            cmap.set_over(over)  # 上限を超えた場合の色を指定
        return cmap
