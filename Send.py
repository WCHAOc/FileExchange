# -*- coding=utf-8 -*-
from PyQt5.Qt import *
import sys
import socket
import threading
import struct
import os
import platform
OS = platform.system().lower()


def send():
    # 发送文件
    file = s.text()
    ip = Input.text()
    # 设置按钮不可点击
    OK.setEnabled(False)
    OK.setText("文件发送中...")
    OK.setStyleSheet(
        # 鼠标点击
        "QPushButton{background-color:#D8D8D8;color:#ECECEC}"
        "QPushButton{border:1px solid gray}"
        "QPushButton{border-radius:10px;}"
    )
    # 此处是功能代码， 创建一个子线程发送文件

    def se():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, 5590))
            try:
                head = ''
                if OS == 'windows':
                    head = '128sq'
                else:
                    head = '128sl'
                file_head = struct.pack(head, os.path.basename(file).encode(), os.stat(file).st_size)
                sock.send(file_head)
                received_size = int(sock.recv(2014).decode())
                read_file = open(file, "rb")
                read_file.seek(received_size)
                while True:
                    file_data = read_file.read(10240)
                    if not file_data:
                        break
                    sock.send(file_data)
                read_file.close()
                res = sock.recv(1024).decode()
                sock.close()
            except FileNotFoundError:
                exit("文件已被移动")
        except ConnectionRefusedError:
            Status.setText("0")
            Status.setStyleSheet(
                "background-color:red;"
                "border-radius:10px;"
                "color:#ECECEC"
            )
    t = threading.Thread(target=se)
    t.start()
    t.join()
    # 线程结束后恢复发送按钮并给出提示
    # 设置按钮可以点击
    OK.setText("发送")
    OK.setEnabled(True)
    OK.setStyleSheet(
        # 鼠标点击
        "QPushButton:pressed{background-color:#D8D8D8;color:#ECECEC}"
        "QPushButton{border:1px solid gray}"
        "QPushButton{border-radius:10px;}"
    )


# 主体窗口
app = QApplication(sys.argv)
app.setStyle(QStyleFactory.create("Fusion"))
widget = QWidget()
widget.setWindowFlags(Qt.WindowStaysOnTopHint)
widget.setWindowTitle("File-Send")
widget.setFixedSize(400, 300)
Input = QLineEdit(widget)
Input.setPlaceholderText("接收文件IP")
Input.setGeometry(120, 20, 130, 30)
Input.setStyleSheet(
    "padding-left:10px;"
    "border-radius:8px"
)
# Input.setInputMask("000.000.000.000")


def getstatus():
    def s():
        ip = Input.text()
        # 判断是否可以连接
        test.setEnabled(False)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, 5590))
            Status.setStyleSheet(
                "background-color:#377D22;"
                "border-radius:10px;"
                "color:#ECECEC"
            )
            Status.setText("1")
            test.setEnabled(True)
        except OSError as e:
            Status.setText("0")
            Status.setStyleSheet(
                "background-color:red;"
                "border-radius:10px;"
                "color:#ECECEC"
            )
            test.setEnabled(True)
    threading.Thread(target=s).start()


# 测试按钮
test = QPushButton(widget)
test.setText("测试")
test.setGeometry(255, 25, 40, 20)
test.clicked.connect(lambda: getstatus())
status = QLabel("连接状态:", widget)
status.setGeometry(120, 65, 65, 30)
# 状态
Status = QLabel("0", widget)
Status.setAlignment(Qt.AlignCenter)
Status.setGeometry(185, 70, 20, 20)
Status.setStyleSheet(
    "background-color:red;"
    "border-radius:10px;"
    "color:#ECECEC"
)


# 点击选择文件事件
def getfile():
    file = QFileDialog().getOpenFileName()
    if file[0]:
        s.setText(file[0])
        OK.setEnabled(True)
        OK.setStyleSheet(
            # 鼠标点击
            "QPushButton:pressed{background-color:#D8D8D8;color:#ECECEC}"
            "QPushButton{border:1px solid gray}"
            "QPushButton{border-radius:10px;}"
        )


# 文件选择框
File = QLabel("", widget)
s = QPushButton("拖动文件到此处或选择文件", File)
s.setStyleSheet(
    "border:none;"
)
s.clicked.connect(lambda: getfile())

s.setGeometry(0, 0, 220, 120)
File.setGeometry(90, 110, 220, 120)
File.setAlignment(Qt.AlignCenter)
File.setStyleSheet(
    "border:1px solid gray;"
    "border-radius:12px;"
)
# 确定按钮
OK = QPushButton("发送", widget)
OK.setGeometry(160, 248, 80, 40)
OK.setFont(QFont("Arial", 20))
OK.setEnabled(False)
OK.setStyleSheet(
    # 鼠标点击
    "QPushButton{background-color:#D8D8D8;color:#ECECEC}"
    "QPushButton{border:1px solid gray}"
    "QPushButton{border-radius:10px;}"
)
OK.clicked.connect(lambda: send())
widget.show()
sys.exit(app.exec_())
