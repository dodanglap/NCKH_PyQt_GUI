import sys
sys.path.append('/home/lapdo/NCKH/lib/python3.11/site-packages')

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QDialog, QPushButton, QLabel, QDateTimeEdit, QVBoxLayout

formatDateTime = "dd/MM/yyyy HH:mm:ss"
class CustomDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Đặt lịch")
        self.setGeometry(400, 300, 300, 200)
        
        # Thêm các nút
        self.vLayout = QVBoxLayout()
        self.lb_thoi_gian = QLabel("Bắt đầu")
        self.vLayout.addWidget(self.lb_thoi_gian)
        self.date_time_start = QDateTimeEdit(self)
        self.date_time_start.setCalendarPopup(True)
        self.date_time_start.setDateTime(self.date_time_start.dateTime().currentDateTime())
        self.date_time_start.setDisplayFormat(formatDateTime)
        self.vLayout.addWidget(self.date_time_start)
        
        self.lb_thoi_gian = QLabel("Kết thúc")
        self.vLayout.addWidget(self.lb_thoi_gian)
        
        self.date_time_end = QDateTimeEdit(self)
        self.date_time_end.setCalendarPopup(True)
        self.date_time_end.setDateTime(self.date_time_end.dateTime().currentDateTime())
        self.date_time_end.setDisplayFormat(formatDateTime)
        self.vLayout.addWidget(self.date_time_end)
        
        self.btn_ok = QPushButton("OK", self)
        self.vLayout.addWidget(self.btn_ok)
        self.btn_ok.clicked.connect(self.accept) # chấp nhận đặt lịch
        
        self.btn_cancel = QPushButton("Cancel", self)
        self.vLayout.addWidget(self.btn_cancel)
        self.btn_cancel.clicked.connect(self.reject)
        
        self.setLayout(self.vLayout)
        


        



