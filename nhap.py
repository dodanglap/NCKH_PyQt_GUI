from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtWidgets import QLabel, QPushButton, QGridLayout, QTableWidgetItem,QLineEdit, QApplication, QMainWindow, QMessageBox, QFileDialog, QDialog,QHeaderView
from PyQt6.QtGui import QBrush, QColor, QFont, QIcon, QPixmap, QImage
from gui_main import Ui_MainWindow
from datetime import datetime
import numpy as np
import cv2
import time, random
import emailPython
import dialog
import pandas as pd
# Khởi tạo firebase
from firebase import firebase
firebase = firebase.FirebaseApplication('https://fir-firebase-2eb50-default-rtdb.asia-southeast1.firebasedatabase.app', None)

urlUser = "/Users"
tt_Webcam = "Tắt"

urlSlTB = "/So_luong_thiet_bi"
urlSlMg = "/So_luong_may_giat"
urlSlMs = "/So_luong_may_say"
urlLichHoatDong = "/Lich_hoat_dong"
labels = ["Tài khoản", "Thiết bị", "Ngày"]
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self)
        
        # Lấy các cột của data đặt lịch:
        numberColumn = len(labels)
        dataFrame = danh_sach_lich_hoat_dong(urlLichHoatDong)
        numberRow = len(dataFrame)
        print("Data: ", dataFrame)
        
        # Thiết lập số hàng và cột cho bảng
        self.uic.tb_lich_hoat_dong.setRowCount(numberRow)
        self.uic.tb_lich_hoat_dong.setColumnCount(numberColumn)
        
        # data_lich_hoat = {"TK":, "Thiết bị":}
        self.uic.tb_lich_hoat_dong.setHorizontalHeaderLabels([str(lbl) for lbl in labels])
        # Điều chỉnh kích thước của cột index (cột tự động đánh số hàng)
        self.uic.tb_lich_hoat_dong.horizontalHeader().setDefaultSectionSize(100)  # Đặt chiều cao mặc định của hàng
        
        # Sử dụng QHeaderView.ResizeMode cho cột index
        self.uic.tb_lich_hoat_dong.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        # Điền dữ liệu vào bảng
        for row in range(numberRow):
            for col in range(numberColumn):
                
                data_index = dataFrame.iloc[row][col]
                print(data_index)
                item = QTableWidgetItem(str(data_index))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # Căn giữa
                self.uic.tb_lich_hoat_dong.setItem(row, col, item)
                self.uic.tb_lich_hoat_dong.setColumnWidth(col, 100)
        

        # Thiết lập chiều rộng của bảng dựa trên số cột
        total_width = numberColumn * 100
        self.uic.tb_lich_hoat_dong.setMaximumWidth(total_width+10)
    
        

# labels = ["Tài khoản", "Thiết bị", "Ngày", "Bắt đầu", "Kết thúc"]
def danh_sach_lich_hoat_dong(urlLichHoatDong):
    
    result = firebase.get(urlLichHoatDong, None)
    
    print(result)
    tkDatLich = []
    tbiDatLich = []
    ngayDatLich = []
    tgianBatDau = []
    tgianKetThuc = []
    trangthai = []
    if result != None:
        for i in range (len(result)):
            tkDatLich.append(result[i][0])
            tbiDatLich.append(result[i][1])
            ngayDatLich.append(result[i][2])
            tgianBatDau.append(result[i][3])
            tgianKetThuc.append(result[i][4])
            trangthai.append(result[i][5])
    dataFrame = pd.DataFrame({"Tài khoản": tkDatLich, "Thiết bị":tbiDatLich, "Ngày":ngayDatLich, 
                              "Bắt đầu":tgianBatDau, "Kết thúc":tgianKetThuc, "Trạng thái":trangthai})
    
    return dataFrame

def danh_sach_ban_dat_lich(urlTKDatlich):
    
    result = firebase.get(urlLichHoatDong, None)
    
    print(result)
    tkDatLich = []
    tbiDatLich = []
    ngayDatLich = []
    tgianBatDau = []
    tgianKetThuc = []
    
    if result != None:
        for i in range (len(result)):
            tkDatLich.append(result[i][0])
            tbiDatLich.append(result[i][1])
            ngayDatLich.append(result[i][2])
            tgianBatDau.append(result[i][3])
            tgianKetThuc.append(result[i][4])
            
    dataFrame = pd.DataFrame({"Tài khoản": tkDatLich, "Thiết bị":tbiDatLich, "Ngày":ngayDatLich, 
                              "Bắt đầu":tgianBatDau, "Kết thúc":tgianKetThuc})
    
    return dataFrame
        
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()