import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class PlotConfigure:
    @staticmethod
    def convert_color(color, discrete=False):
        if discrete:
            default = ['red', 'blue', 'green', 'yellow', 'pink', 'orange', 'black', 'purple', 'brown', 'lime', 'cyan']
            return [default[int(c)] for c in color]
        return color

    @staticmethod
    def plot_3d(x, color, discrete=False):
        if color is not None:
            color = PlotConfigure.convert_color(color, discrete)
        fig = plt.figure(1, figsize=(8, 6))
        ax = Axes3D(fig, elev=-150, azim=110)
        ax.scatter(x[:, 0], x[:, 1], x[:, 2], edgecolor='k', s=40, c=color)
        ax.set_title("First three PCA directions")
        ax.set_xlabel("1st eigenvector")
        ax.w_xaxis.set_ticklabels([])
        ax.set_ylabel("2nd eigenvector")
        ax.w_yaxis.set_ticklabels([])
        ax.set_zlabel("3rd eigenvector")
        ax.w_zaxis.set_ticklabels([])
        plt.show()

    @staticmethod
    def plot_2d(x, color, annotate=False, discrete=False):
        if color is not None:
            color = PlotConfigure.convert_color(color, discrete)
        f, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5))
        ax1.scatter(x[:, 0], x[:, 1], edgecolor='k', s=40, c=color)
        ax1.set_xlabel("1st eigenvector")
        ax1.set_ylabel("2nd eigenvector")
        ax2.scatter(x[:, 0], x[:, 2], edgecolor='k', s=40, c=color)
        ax2.set_xlabel("1st eigenvector")
        ax2.set_ylabel("3nd eigenvector")
        ax3.scatter(x[:, 1], x[:, 2], edgecolor='k', s=40, c=color)
        ax3.set_xlabel("2st eigenvector")
        ax3.set_ylabel("3nd eigenvector")
        if annotate:
            for i in range(len(x)):
                ax1.annotate(i, (x[:, 0][i], x[:, 1][i]))
                ax2.annotate(i, (x[:, 0][i], x[:, 2][i]))
                ax3.annotate(i, (x[:, 1][i], x[:, 2][i]))
        plt.show()
