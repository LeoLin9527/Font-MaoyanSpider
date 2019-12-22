import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.neighbors import KNeighborsClassifier

from util.get_train_font import get_font_data


class Classify:
    def __init__(self):
        self.len = None
        self.knn = self.get_knn()

    def process_data(self, data):
        """
        fit(): Method calculates the parameters μ and σ and saves them as internal objects.
        解释：简单来说，就是求得训练集X的均值，方差，最大值，最小值,这些训练集X固有的属性。

        transform(): Method using these calculated parameters apply the transformation to a particular dataset.
        解释：在fit的基础上，进行标准化，降维，归一化等操作（看具体用的是哪个工具，如PCA，StandardScaler等）。

        fit_transform(): joins the fit() and transform() method for transformation of dataset.
        解释：fit_transform是fit和transform的组合，既包括了训练又包含了转换。
        transform()和fit_transform()二者的功能都是对数据进行某种统一处理（比如标准化~N(0,1)，将数据缩放(映射)到某个固定区间，归一化，正则化等）

        :param data:
        :return:
        """
        imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
        return pd.DataFrame(imputer.fit_transform(pd.DataFrame(data)))

    def get_knn(self):
        data = self.process_data(get_font_data())

        x_train = data.drop([0], axis=1)  # 特征值 坐标
        y_train = data[0]  # target 0 - 9

        knn = KNeighborsClassifier(n_neighbors=1)
        knn.fit(x_train, y_train)

        self.len = x_train.shape[1]

        return knn

    def knn_predict(self, data):
        df = pd.DataFrame(data)

        data = pd.concat([df, pd.DataFrame(np.zeros(
            (df.shape[0], self.len - df.shape[1])), columns=range(df.shape[1], self.len))])

        data = self.process_data(data)

        y_predict = self.knn.predict(data)

        return y_predict


if __name__ == '__main__':
    obj = Classify()
