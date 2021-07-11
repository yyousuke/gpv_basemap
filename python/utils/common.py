#
#  2021/06/03 Yamashita
#
import matplotlib
import matplotlib.pyplot as plt
import warnings
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

warnings.filterwarnings('ignore',
                        category=matplotlib.MatplotlibDeprecationWarning)
matplotlib.rcParams['figure.max_open_warning'] = 0
#plt.rcParams['font.size'] = 14  # 文字サイズ
#

