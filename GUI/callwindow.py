import sys
import time

from PyQt5.QtCore import QFile, QTextStream, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PyQt5.QtMultimedia import QSound
from GUI.mainwindow import Ui_Form
from spider.knn_maoyan import KnnMaoYan


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.crawl_thread = CrawlThread()
        self.btn_init()
        self.crawl_init()

    def btn_init(self):
        """
        按钮初始化
        :return:
        """
        self.ui.pushButton_stop.setEnabled(False)
        self.ui.pushButton_start.clicked.connect(lambda: self.btn_slot(self.ui.pushButton_start))
        self.ui.pushButton_stop.clicked.connect(lambda: self.btn_slot(self.ui.pushButton_stop))
        self.ui.pushButton_save.clicked.connect(self.saveBtn_slot)

    def crawl_init(self):
        """
        通过connect连接信号与槽函数
        :return:
        """
        self.crawl_thread.finished_signal.connect(self.finish_slot)

        self.crawl_thread.log_signal.connect(self.set_log_slot)

        self.crawl_thread.result_signal.connect(self.set_table_slot)

    def set_log_slot(self, new_log):
        self.ui.textBrowser.append(new_log)

    def finish_slot(self):
        """
        槽函数 完成
        :return:
        """
        self.ui.pushButton_start.setEnabled(True)
        self.ui.pushButton_stop.setEnabled(False)
        self.ui.pushButton_save.setEnabled(True)

    def saveBtn_slot(self):
        """
        槽函数 另存为文件
        :param text:
        :return:
        """
        self.save_to_txt()

    def save_to_txt(self):
        content = ''
        for row in range(self.ui.tableWidget.rowCount()):
            name = '电影名称：{}\n'.format(self.ui.tableWidget.item(row, 0).text())
            score = '电影评分：{}\n'.format(self.ui.tableWidget.item(row, 1).text())
            boxoffice = '电影票房：{}\n'.format(self.ui.tableWidget.item(row, 2).text())
            content += name + score + boxoffice + '\n'

        with open('./热映口碑榜.txt', 'w', encoding='utf8') as f:
            f.write(content)

        QMessageBox.information(self, '保存到txt', '保存成功！', QMessageBox.Ok)

    def btn_slot(self, btn):
        # self.btn_sound.play()
        if btn == self.ui.pushButton_start:
            self.ui.textBrowser.clear()

            self.ui.textBrowser.append('<font color="red">开始爬取</font>')

            self.ui.tableWidget.clearContents()
            self.ui.tableWidget.setRowCount(0)

            self.ui.pushButton_start.setEnabled(False)
            self.ui.pushButton_stop.setEnabled(True)
            self.ui.pushButton_save.setEnabled(False)

            self.crawl_thread.start()
        else:
            self.ui.textBrowser.append('<font color="red">停止爬取</font>')

            self.ui.pushButton_start.setEnabled(False)
            self.ui.pushButton_stop.setEnabled(True)
            self.ui.pushButton_save.setEnabled(True)

            self.crawl_thread.terminate()

    def set_table_slot(self, name, score, boxoffice):
        """

        :param name:
        :param score:
        :param boxoffice:
        :return:
        """
        row = self.ui.tableWidget.rowCount()

        self.ui.tableWidget.insertRow(row)

        self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(name))
        self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(score))
        self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(boxoffice))

        self.ui.progressBar.setValue((row + 1) * 10)

        if self.ui.progressBar.value() == 100:
            print("完成提示音")
            # self.finish_sound.play()

    def closeEvent(self, QCloseEvent):
        """
        closeEvent()重写，添加关闭窗口触发的事件
        :param QCloseEvent:
        :return:
        """
        pass


class CrawlThread(QThread):
    finished_signal = pyqtSignal()
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str, str, str)

    def __init__(self):
        super(CrawlThread, self).__init__()

    def run(self):
        obj = KnnMaoYan()
        detail_urls = obj.outputUrls()
        
        for url in detail_urls:
            name, score, boxunit = obj.run(url)

            print(name, score, boxunit)
            self.result_signal.emit(name, score, boxunit)
            time.sleep(1)

        self.log_signal.emit('<font color="red">全部爬取完毕！</font>')
        # 完成信号发射
        self.finished_signal.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
