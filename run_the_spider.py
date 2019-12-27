"""
@file:run_the_spider.py
@time:2019/12/19-8:56
"""
from spider.knn_maoyan import KnnMaoYan

if __name__ == '__main__':
    obj = KnnMaoYan()
    detailsUrls = obj.outputUrls()
    infos = obj.run(detailsUrls[1])
    print(f"test:{infos}")
