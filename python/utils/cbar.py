#
#  2021/06/11 Yamashita
#
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


class val2col():
    def __init__(self, tmin=0., tmax=1., tstep=0.2, cmap='jet'):
        self.tmin = tmin
        self.tmax = tmax
        self.tstep = tstep
        self.cmap = cmap
        self.cm = plt.get_cmap(self.cmap)

    def conv(self, temp):
        n = (temp - self.tmin) / (self.tmax - self.tmin) * self.cm.N
        n = max(min(n, self.cm.N), 0)
        return self.cm(int(n))

    def colorbar(self,
                 fig=None,
                 anchor=(0.35, 0.24),
                 size=(0.3, 0.02),
                 fmt="{f:.0f}",
                 label=True):
        if fig is None:
            raise Exception('fig is needed')
        ax = fig.add_axes(anchor + size)
        gradient = np.linspace(0, 1, self.cm.N)
        gradient_array = np.vstack((gradient, gradient))
        ticks = list()
        labels = list()
        ll = np.arange(self.tmin, self.tmax, self.tstep)
        for t in ll:
            ticks.append((t - self.tmin) / (self.tmax - self.tmin) * self.cm.N)
            if label:
                labels.append(fmt.format(f=t))
        # カラーバーを描く
        ax.imshow(gradient_array, aspect='auto', cmap=self.cm)
        ax.yaxis.set_major_locator(ticker.NullLocator())
        ax.yaxis.set_minor_locator(ticker.NullLocator())
        ax.set_xticks(ticks)
        if label:
            ax.set_xticklabels(labels)
        else:
            ax.xaxis.set_major_formatter(ticker.NullFormatter())
            ax.xaxis.set_minor_formatter(ticker.NullFormatter())
        #ax.set_axis_off()

    def clabel(self,
               fig=None,
               anchor=(0.34, 0.24),
               size=(0.1, 0.02),
               text=None,
               ha='right',
               va='bottom',
               fontsize=10):
        if fig is None:
            raise Exception('fig is needed')
        ax = fig.add_axes(anchor + size)
        ax.text(0.0, 0.0, text, ha=ha, va=va, fontsize=fontsize)
        ax.set_axis_off()
