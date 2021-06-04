import matplotlib.pyplot as plt

class Draw_line_chart:
    def __init__(self, x, y, title, label, x_label, y_label, points_num, out_path, is_show):

        self.x = x
        self.y = y
        self.title = title
        self.label = label
        self.x_label = x_label
        self.y_label = y_label
        self.points_num = points_num
        self.out_path = out_path
        self.is_show = is_show

        if not self.check_legal():
            print("input data not legal!")
            exit(0)

    def check_legal(self):
        return len(self.x) == len(self.y)

    def draw_pci(self):
        plt.figure(figsize=(20, 8), dpi=80)
        plt.plot(self.x, self.y, label=self.label, color="r", linewidth=1, alpha=0.5)
        step = max(int(len(self.x) / self.points_num), 1)
        x = [self.x[i] for i in range(0, len(self.x), step)]
        x_ticks = ["{}".format(i) for i in x]
        plt.xticks(x, x_ticks, rotation=0)
        plt.legend(loc="upper left")
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        plt.title(self.title + str(x))
        plt.savefig(self.out_path + "/{}.jpg".format(self.title))
        if self.is_show:
            plt.show()
        plt.close()

class Draw_multi_line_chart:
    def __init__(self, xs, ys, title, labels, x_label, y_label, points_num, out_path, is_show):

        self.color = ['black', 'darkorange', 'lightgreen', 'cornflowerblue', 'lightcoral', 'gold', 'blue', 'darkviolet',
                      'mediumturquoise']
        self.xs = xs
        self.ys = ys
        self.title = title
        self.labels = labels
        self.x_labels = x_label
        self.y_labels = y_label
        self.points_num = points_num
        self.out_path = out_path
        self.is_show = is_show

        if not self.check_legal():
            print("input data not legal!")
            exit(0)

    def check_legal(self):
        if len(self.xs) == len(self.ys):
            return False
        for i in range(len(self.xs)):
            if len(self.xs[i] != len(self.ys[i])):
                return False
        return True

    def draw_pci(self):
        plt.figure(figsize=(20, 8), dpi=80)

        x_min = min(min(self.xs))
        x_max = max(max(self.xs))
        for i in range(len(self.xs)):
            x = []
            y = []
            for j in range(len(self.xs[i])):
                x.append(self.xs[i][j])
                y.append(self.ys[i][j])
            plt.plot(x, y, label=self.labels[i], color=self.color[i % len(self.color)], linewidth=1, alpha=1)
        step = max(((x_max - x_min) / self.points_num), 1)
        x = [i for i in range(x_min, x_max, step)]
        x_ticks = ["{}".format(i) for i in x]
        plt.xticks(x, x_ticks, rotation=0)
        plt.legend(loc="upper left")
        plt.xlabel(self.x_labels)
        plt.ylabel(self.y_labels)
        plt.title(self.title + str(x))
        plt.savefig(self.out_path + "/{}.jpg".format(self.title))
        if self.is_show:
            plt.show()
        plt.close()

class DrawBar:
    def __init__(self, x, ys, labels):
        self.bar_width = 0.03
        self.x = x
        self.ys = ys
        self.labels = labels

    def draw(self):
        temp_x = []
        for i in range(len(self.ys)):
            temp_x = [j + self.bar_width * i for j in range(len(self.x))]
            plt.bar(temp_x, self.ys[i], width=self.bar_width)
        plt.xticks(temp_x, self.x)
        plt.legend()
        plt.show()

def draw_matric(matric):
    plt.matshow(matric, cmap=plt.get_cmap("Greens"), alpha=0.5)
    plt.show()


