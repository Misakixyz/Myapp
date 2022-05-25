import datetime
import os
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
from ui_type import Ui_MainWindow
import socket
import time
import _thread
import platform
import psutil
import sys

global live_ip
global glo_pid
lock1 = threading.Lock()
lock2 = threading.Lock()
lock3 = threading.Lock()

socket.setdefaulttimeout(3)  # 设置默认超时时间


# 进程循环
def psutil_loop(tabelWidget):
    while 1:
        call_my_psutil(tabelWidget)
        time.sleep(60)


# 内存使用率循环
def memory_use(label):
    while 1:
        mem = psutil.virtual_memory()
        pp = float(mem.used / mem.total) * 100  # 总内存使用率
        item = '内存使用率：' + str(round(pp, 2)) + '%'
        label.setText(item)
        time.sleep(1)


# cpu使用率循环
def cpu_use(label_3):
    while 1:
        item = 'cpu使用率：' + str(round(psutil.cpu_percent(), 2)) + '%'
        label_3.setText(item)
        time.sleep(1)


# 获取本机ip
def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


# 采用scoket搜寻端口
def socket_port(ip, port, listWidget):
    """
    输入IP和端口号，扫描判断端口是否占用
    """
    try:
        if port >= 65535:
            print(u'端口扫描结束')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex((ip, port))
        if result == 0:
            item = str(port) + "端口已占用"
            listWidget.addItem(item)
    except:
        print(u'端口扫描异常')
        listWidget.addItem('端口扫描异常')


# 搜索给定ip的端口
def ip_scan(ip, listWidget):
    """
        输入IP，扫描IP的0-65534端口情况
            """
    try:
        listWidget.addItem("开始扫描")
        for i in range(0, 65536):
            # 立即创建线程，线程自行执行
            _thread.start_new_thread(socket_port, (ip, int(i), listWidget,))
            app.processEvents()
        # 刷新
        app.processEvents()
    except:
        print(u'扫描ip出错')
        listWidget.addItem('扫描ip出错')


###################################################################################

def my_os():  # 1、获取本机操作系统名称
    return platform.system()


def ping_ip(ip, listWidget):  # 2、ping指定IP判断主机是否存活
    try:
        # os = platform.system()
        if my_os() == 'Windows':
            p_w = 'n'
        elif my_os() == 'Linux':
            p_w = 'c'
        else:
            print('不支持此操作系统')
            sys.exit()
        global live_ip
        cmd = ['ping -' + str(p_w) + ' 1 ' + str(ip)]
        output = os.popen(" ".join(cmd)).readlines()
        for w in output:
            if str(w).upper().find('TTL') >= 0:
                print(ip, 'ok')
                listWidget.addItem(ip)
                lock2.acquire()  # 锁进程
                live_ip += 1
                lock2.release()
    except:
        print('ping_ip_error')
        listWidget.addItem('error')


# 开启线程，调用ping_ip
def ping_all(ip, listWidget):  # 3、ping所有IP获取所有存活主机
    try:
        pre_ip = (ip.split('.')[:-1])
        for i in range(1, 256):
            add = str('.'.join(pre_ip)) + '.' + str(i)
            _thread.start_new_thread(ping_ip, (add, listWidget,))
            app.processEvents()
            time.sleep(0.1)
        print('ping_end')
    except:
        print('ping_all_error')


###################################################################################
# psutil 进程模块，将进程信息放入表格
def my_psutil(pid, tableWidget):
    try:
        row_cnt = tableWidget.rowCount()  # 返回当前行数（尾部）
        tableWidget.insertRow(row_cnt)  # 尾部插入一行新行表格
        p = psutil.Process(pid)
        process_name = p.name()
        item_in = str(round(p.memory_info().rss / 1024 / 1024, 2)) + 'MB'  # 内存使用量
        item_tn = str(p.num_threads())  # cpu使用率
        p_exe = str(p.exe())
        p_createtime = datetime.datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H: %M: %S")
        p_mp = str(round(p.memory_percent(), 2)) + '%'
        tableWidget.setItem(row_cnt, 0, QtWidgets.QTableWidgetItem(process_name))  # 1进程名
        tableWidget.setItem(row_cnt, 1, QtWidgets.QTableWidgetItem(str(pid)))  # 2PID
        tableWidget.setItem(row_cnt, 2, QtWidgets.QTableWidgetItem(p_mp))  # 3内存使用率
        tableWidget.setItem(row_cnt, 3, QtWidgets.QTableWidgetItem(item_in))  # 4内存使用量
        tableWidget.setItem(row_cnt, 4, QtWidgets.QTableWidgetItem(item_tn))  # 5进程数
        tableWidget.setItem(row_cnt, 5, QtWidgets.QTableWidgetItem(p_createtime))  # 6创建时间
        tableWidget.setItem(row_cnt, 6, QtWidgets.QTableWidgetItem(p_exe))  # 7路径
    except:
        print('psutil_error')


# 开启线程，调用my_psutil
def call_my_psutil(tableWidget):
    try:
        tableWidget.setRowCount(0)
        print('call_psutil_running')
        pids = psutil.pids()
        for pid in pids:
            _thread.start_new_thread(my_psutil, (pid, tableWidget,))
            app.processEvents()
        print('call_psutil_end')
    except:
        print('call_psutil_error')


#####################################################################
# 停止进程
def call_kill_process(pid):
    if os.name == 'nt':
        # Windows系统
        cmd = 'taskkill /pid ' + str(pid) + ' /f'
        try:
            os.system(cmd)
            print(pid, 'killed')
        except Exception as e:
            print(e)
    elif os.name == 'posix':
        # Linux系统
        cmd = 'kill ' + str(pid)
        try:
            os.system(cmd)
            print(pid, 'killed')
        except Exception as e:
            print(e)
    else:
        print('Undefined os.name')


# 继承自ui文件
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.list_usingport)  #
        self.pushButton_2.clicked.connect(self.list_ip_scan)
        self.pushButton_3.clicked.connect(self.list_ip_port_scan)
        self.pushButton_4.clicked.connect(self.table_psutil)
        self.pushButton_5.clicked.connect(self.psutil_kill)

        _thread.start_new_thread(memory_use, (self.label,))  # 定时获取内存使用率
        _thread.start_new_thread(cpu_use, (self.label_3,))  # 定时获取cpu使用率
        _thread.start_new_thread(psutil_loop, (self.tableWidget,))  # 定时获取本机进程

    ##########################################################
    ###################################################
    # 端口查询
    def list_usingport(self):
        print('list_usingport:running')
        self.listWidget.clear()
        self.listWidget.addItem("port_scan")
        ip = get_host_ip()
        self.listWidget.addItem(ip)
        app.processEvents()
        start_time = time.time()
        ip_scan(ip, self.listWidget)
        timeu = time.time() - start_time
        item = '扫描端口完成，总共用时：' + str(round(timeu, 2)) + '秒'
        self.listWidget.addItem(item)
        self.listWidget.addItem('端口扫描结束')

    ##########################################################################################
    # ip查询
    def list_ip_scan(self):
        global live_ip
        live_ip = 0
        ip = get_host_ip()
        print('list_tp_scan_running')
        self.listWidget_2.clear()
        item = '本机ip: ' + str(ip)
        self.listWidget_2.addItem(item)
        item = '开始扫描时间' + str(time.ctime())
        self.listWidget_2.addItem(item)
        app.processEvents()

        ping_all(ip, self.listWidget_2)
        app.processEvents()

        item = '扫描结束时间' + str(time.ctime())
        self.listWidget_2.addItem(item)
        item = '本次扫描共检测到本网络存在' + str(live_ip) + '台设备'
        self.listWidget_2.addItem(item)
        app.processEvents()

    ################################################################
    # 给定ip端口查询
    def list_ip_port_scan(self):
        print('ip_port_scan_running')
        this_ip = self.lineEdit_2.text()
        self.listWidget_3.clear()
        item = 'ip: ' + str(this_ip) + ' port_scan'
        print(item)
        self.listWidget_3.addItem(item)
        app.processEvents()
        start_time = time.time()
        ip_scan(this_ip, self.listWidget_3)
        timeu = time.time() - start_time
        item = '扫描端口完成，总共用时：' + str(round(timeu, 2)) + '秒'
        self.listWidget_3.addItem(item)
        print('ip_port_scan_end')

    # 查询本机进程
    def table_psutil(self):
        call_my_psutil(self.tableWidget)

    # 杀死进程
    def psutil_kill(self):
        # global glo_pid
        this_pid = self.lineEdit_3.text()
        # this_pid = glo_pid
        call_kill_process(int(this_pid))
        print('psutil_end')
        # glo_pid = 0

        # def get_pid(self, index):
        # print('table_clicked')
        # row_index = self.tableWidget.currentIndex().row()  # 获取当前行Index
        # current_row_name = self.tableWidget.item(row_index, 0).text()  # item(行,列), 获取当前行
    #    try:
    #        table_row = index.row()
    #        global glo_pid
    #        glo_pid = self.tableWidget.item(table_row, 1)
    # glo_pid = int(self.tableWidget.item(current_row_name, 1))
    #    except:
    #        print('table_click_error')


###################################################################################
if __name__ == "__main__":
    app = 0
    # 适配2k等高分辨率屏幕
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()  # 注意窗口类型
    mainWindow.show()
    sys.exit(app.exec_())
