# -*- coding=utf-8 -*-
from PyQt5.Qt import *
import sys
import socket
import threading
import os
import struct
import time


def receive(worker):
    # 接收文件
    def sending_file(connection, address):
        try:
            file_info_size = struct.calcsize('128sl')
            buf = connection.recv(file_info_size)
            if buf:
                file_name, file_size = struct.unpack('128sl', buf)
                file_name = file_name.decode().strip('\00')
                file_new_dir = os.path.join('upload')
                if not os.path.exists(file_new_dir):
                    os.makedirs(file_new_dir)
                file_new_name = os.path.join(file_new_dir, file_name)
                received_size = 0
                if os.path.exists(file_new_name):
                    received_size = os.path.getsize(file_new_name)
                connection.send(str(received_size).encode())
                w_file = open(file_new_name, 'ab')
                start_time = time.strftime('%Y-%m-%d %H:%M:%S')
                worker.write(f"开始接收文件: {file_name}\n当前时间 {start_time}\n")
                while not received_size == file_size:
                    r_data = connection.recv(10240)
                    received_size += len(r_data)
                    w_file.write(r_data)
                w_file.close()
                end_time = time.strftime('%Y-%m-%d %H:%M:%S')
                upload_ok = "upload ok:" + str(end_time)
                worker.write(f"接收完成!当前时间\n{end_time}\n")
                connection.sendto(r'上传成功'.encode(), (address[0], address[1]))
            else:
                pass
            connection.close()
        except Exception as e:
            worker.write(e)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 5590))
    sock.listen(5)
    while True:
        connection, address = sock.accept()
        worker.write(f"客户端连接成功\n{address}\n")
        thread = threading.Thread(target=sending_file, args=(connection, address,))
        thread.start()


# 主体窗口
app = QApplication(sys.argv)
app.setStyle(QStyleFactory.create("Fusion"))
win = QMainWindow()
widget = QWidget()
widget.layout = QHBoxLayout()
widget.setWindowFlags(Qt.WindowStaysOnTopHint)
widget.setWindowTitle("File-Receive")
widget.setFixedSize(300, 200)
widget.layout = QHBoxLayout()


class Worker(QObject):
    messageChanged = pyqtSignal(str)

    def start(self, fn):
        threading.Thread(target=self._execute, args=(fn,), daemon=True).start()

    def _execute(self, fn):
        fn(self)

    def write(self, message):
        self.messageChanged.emit(message)


Input = QLineEdit(socket.gethostbyname(socket.gethostname()), widget)
Input.setGeometry(80, 20, 160, 40)
Input.setAlignment(Qt.AlignCenter)
Input.setReadOnly(True)
Input.setStyleSheet(
    "border-radius:8px"
)
Input.setFont(QFont("Arial", 18))
status = QLabel("服务已启动", widget)
status.setGeometry(110, 70, 80, 40)
Status = QLabel("", widget)
Status.setAlignment(Qt.AlignCenter)
Status.setGeometry(180, 85, 10, 10)
Status.setStyleSheet(
    "background-color:#377D22;"
    "border-radius:5px;"
    "color:#ECECEC"
)
Info = QTextEdit("", widget)
Info.setGeometry(60, 110, 180, 70)
Info.setReadOnly(True)
Info.setStyleSheet(
    "border:1px solid gray"
)
Info.setAlignment(Qt.AlignCenter)
worker = Worker()
worker.messageChanged.connect(Info.append)
worker.start(receive)


widget.show()
sys.exit(app.exec_())