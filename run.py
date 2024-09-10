import sys
sys.path.append('/home/lapdo/NCKH/lib/python3.11/site-packages')


from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtWidgets import QTableWidgetItem,QLineEdit, QApplication, QMainWindow, QMessageBox, QFileDialog
from PyQt6.QtGui import QBrush, QColor, QFont, QIcon, QPixmap, QImage
from gui_main import Ui_MainWindow
from datetime import datetime
import numpy as np
import cv2
import cam_bien_van_tay as vt
import time

# Khởi tạo firebase
from firebase import firebase
firebase = firebase.FirebaseApplication('https://fir-firebase-2eb50-default-rtdb.asia-southeast1.firebasedatabase.app', None)

urlUser = "/Users"
tt_Webcam = "Tắt"

# Class Thread kiểm tra vân tay đăng nhập
class FingerPrintThread(QThread):
    # Tín hiệu gửi về khi vân tay đăng nhập hợp lệ
    signal_van_tay_dang_nhap_hop_le = pyqtSignal()
    signal_van_tay_that_bai = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super(FingerPrintThread, self).__init__(parent)
        self.running = True # Biến điều khiển Thread
        
    def run(self):
        global tt_Webcam
        while self.running:
            print("Thread van tay")
            
            stateFind_FingerPrint = self.get_fingerprint_id()
            
            # Lấy danh sách vân tay
            
            
            if stateFind_FingerPrint == True:
                # Nếu vân tay hợp lệ, phát tín hiệu để giao diện biết
                self.signal_van_tay_dang_nhap_hop_le.emit()
                # Chuyen trang chinh
                showMessageBox("Đăng nhập", "Đăng nhập Vân tay thành công")
                self.trang_chinh()
                
                
                break
            elif stateFind_FingerPrint == False:
                self.signal_van_tay_that_bai.emit("Đăng nhập", "Đăng nhập Vân tay Không thành công") # truyền tín hiệu tới
                
            time.sleep(1.5)
                    
            
        return
            
    def stop(self):
        self.running = False  # Đặt biến điều khiển để dừng luồng
        self.terminate()

    def get_fingerprint_id(self):
        try:
            ds_vanTay = get_all_info_database(urlUser, 2)
            # Viết hàm quét vân tay
            state_find = vt.find_van_tay(ds_vanTay)
            return state_find
        except:
            pass
        


# Class Webcam
class CaptureVideo(QThread):
    
    signal_captureVideo = pyqtSignal(np.ndarray)
    def __init__(self, parent = None):
        super(CaptureVideo, self).__init__(parent)
        global tt_Webcam
        self._running = True
        

    def run(self):
        global tt_Webcam
        tt_Webcam = "Bật"
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Không thể mở camera")
            tt_Webcam = "Tắt"
            return
        
        while self._running and tt_Webcam == "Bật":
            ret, cv_img = cap.read()
            if ret:
                tt_Webcam = "Bật"
                self.signal_captureVideo.emit(cv_img)
            else:
                tt_Webcam = "Tắt"
                break
            
        cap.release()
        print("đã tắt cam")
        return
                
    def stop(self):
        global tt_Webcam
        self._running = False
        tt_Webcam = "Tắt"
        print(tt_Webcam)
        
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self)
        self.tin_hieu_dang_ky = False
        self.tin_hieu_dang_nhap = False
        self.tin_hieu_trang_chinh = False
        self.tin_hieu_trang_doi_mat_khau = False
        self.tin_hieu_trang_quen_mat_khau = False
        
        # Setup trang đăng nhập đầu tiên
        self.vao_trang_dang_nhap()
        
   
    # ================================================= Trang đăng nhập ================================================ 
    def vao_trang_dang_nhap(self):
        self.uic.stackedWidget.setCurrentWidget(self.uic.trang_dang_nhap)
        # Khởi tạo thread kiểm tra vân tay
        self.thread_van_tay = FingerPrintThread()
        self.thread_van_tay.signal_van_tay_dang_nhap_hop_le.connect(self.dang_nhap_van_tay_thanh_cong)
        self.thread_van_tay.signal_van_tay_that_bai.connect(self.show_message)

        
        self.thread_van_tay.start()
        print("TK: ", self.uic.Edt_mk_dn.text())
        self.uic.btn_face_dn.setEnabled(True)
        if self.tin_hieu_dang_nhap == False: 
            self.uic.btn_xn_dn.clicked.connect(self.xac_nhan_dang_nhap)
            self.uic.btn_dk_dn.clicked.connect(self.trang_dang_ky)  
            self.uic.btn_face_dn.clicked.connect(self.start_Face_ID_dang_nhap)
            self.uic.btn_quen_mk_dn.clicked.connect(self.trang_quen_mat_khau)
            self.uic.btn_doi_mk_dn.clicked.connect(self.trang_doi_mat_khau)
            self.tin_hieu_dang_nhap = True 
            
    # Hàm đăng nhập
    # SHow mess đăng nhập VÂN TAY KHÔNG thành công
    def show_message(self, title, content):
        global tt_Webcam
        showMessageBox(title, content)
        
        
        
    def xac_nhan_dang_nhap(self):
        global tt_Webcam
        # Lấy danh sách người dùng
        dsTK = get_all_info_database(urlUser, 0)
        dsMk = get_all_info_database(urlUser, 1)
        
        # dsFace = get_all_info_database(urlUser, 3)
        
        # Lấy thông tin đăng nhập
        tkDn = self.uic.Edt_tk_dn.text()
        mkDn = self.uic.Edt_mk_dn.text()
        idVt = self.uic.lb_vt_dn.text()
        idFace = self.uic.lb_id_face_dn.text()
        
        if (tkDn == "" and mkDn == "" and idVt == ""):
            showMessageBox("Đăng nhập", "Đăng Nhập không thành công\nĐăng nhập bằng tài khoản/ Quét vân tay")
            
        # Trường họp đăng nhập bằng tk mk
        elif (tkDn != "" and mkDn != ""): 
            
            print("Đăng nhập bằng tài khoản")
            if tkDn not in dsTK:
                showMessageBox("Đăng Nhập", "Không tồn tại tài khoản")
            else:
                index_tkDn = dsTK.index(tkDn)
                if mkDn == dsMk[index_tkDn]:
                    
                    # Đăng nhập thành công
                    showMessageBox("Đăng Nhập", "Đăng Nhập bằng Tài khoản thành công")
                    self.thread_van_tay.stop()
                    if tt_Webcam == "Bật":
                        self.thread_webcam_face.stop()
                    self.trang_chinh()
                else:
                    showMessageBox("Đăng Nhập", "Đăng Nhập không thành công\nSai mật khẩu/TK")
                    
        
            
    # Hàm xử lý khi vân tay được xác nhận
    def dang_nhap_van_tay_thanh_cong(self):
        global tt_Webcam
        showMessageBox("Đăng Nhập", "Đăng Nhập bằng Vân tay thành công")
        
        self.uic.stackedWidget.setCurrentWidget(self.uic.trang_chinh)


    
    def start_Face_ID_dang_nhap(self):
        global tt_Webcam
        
        self.uic.btn_face_dn.setEnabled(False)
        self.thread_webcam_face = CaptureVideo()
        self.thread_webcam_face.start()
        self.thread_webcam_face.signal_captureVideo.connect(self.show_webcam)
    
            
    def show_webcam(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.uic.lb_cam_dn.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        if cv_img is None:
            return QPixmap()
        
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Sử dụng hàm scaled cố định kích thước ảnh cho label
        p = convert_to_Qt_format.scaled(self.uic.lb_cam_dn.width(), self.uic.lb_cam_dn.height(), Qt.AspectRatioMode.KeepAspectRatio)
        return QPixmap.fromImage(p)



    
    # ==============================================Hàm trang đăng ký==================================================
    def trang_dang_ky(self):
        global tt_Webcam
        self.uic.stackedWidget.setCurrentWidget(self.uic.trang_dang_ky)
        self.thread_van_tay.stop()
        if tt_Webcam == "Bật":
            self.thread_webcam_face.stop()
        
        if self.tin_hieu_dang_ky == False:
            self.uic.btn_ql_dn.clicked.connect(self.vao_trang_dang_nhap)
            self.uic.btn_xn_dk.clicked.connect(self.xac_nhan_dang_ky)
            self.uic.btn_face_dk.clicked.connect(self.trang_dang_ki_face_id)
            self.uic.btn_vt_dki.clicked.connect(self.dang_ki_van_tay)
            self.tin_hieu_dang_ky = True
    
    def trang_dang_ki_face_id(self):
        pass
    
    def dang_ki_van_tay(self):
        
        # Lấy danh sách vân tay
       
        self.tkDki = self.uic.edt_tk_dk.text()
        self.mkDki = self.uic.edt_mk_dk.text()
        self.mkDkiLai = self.uic.edt_mkl_dk.text()
        
        if self.tkDki == "" or self.mkDki == "" or self.mkDkiLai == "":
            showMessageBox("Đăng ký", "Bạn phải nhập TK/MK")
        else:
            listIDVanTay = get_all_info_database(urlUser, 2)
            if 'None' in listIDVanTay:
                listIDVanTay.remove('None')
            
            listUser = get_all_info_database(urlUser, 0) # Lấy ra danh sách tài khoản
            self.idNewUsers = f'User {len(listUser) + 1}'
            if self.tkDki in listUser:
                
                showMessageBox("Đăng ký", "Lỗi tài khoản đã tồn tại")
            else:
                if self.mkDki != self.mkDkiLai:
                    showMessageBox("Đăng ký", "Xác nhận lại mật khẩu")
                else:
                    # Bắt đầu add
                    try:
                        stateAdd = vt.save_van_tay(list_van_tay= listIDVanTay)
                        print('tt ADD: ', stateAdd)
                        
                        if stateAdd == False:
                            showMessageBox("Đăng ký", "Đăng ký không thành công")
                        else:
                            # Hỏi người dùng có thêm face id không
                            # Có -> trở về tiếp tục đăng ký
                            # Không -> tiếp tụ xác nhận đăng ký -> put dữ liệu lên
                            self.idNewVanTay = len(listIDVanTay) + 1
                            
                            msg_box_ques = QMessageBox()
                            msg_box_ques.setIcon(QMessageBox.Icon.Question)
                            msg_box_ques.setWindowTitle("Xác nhận")
                            msg_box_ques.setText("Bạn có muốn thêm Face ID không?")
                            msg_box_ques.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                            return_choose = msg_box_ques.exec()
                            
                            if return_choose == QMessageBox.StandardButton.Yes:
                                showMessageBox("Đăng ký", "Mời bạn đăng ký Face ID")
                            else:
                                # Put dữ liệu
                                
                                
                                listNewInfoUser = [self.tkDki, self.mkDki, self.idNewVanTay, 'None'] # tk mk vantay face
                                firebase.put(urlUser, self.idNewUsers, listNewInfoUser)
                                showMessageBox("Đăng ký", "Bạn đăng ký TK và Vân tay thành công")
                    except:
                        showMessageBox("Vân tay", "Lỗi cảm biến vân tay")
        
        # Gọi hàm thêm vân tay
        
        
    
    def xac_nhan_dang_ky(self):
        # Lấy danh sách người dùng
        # Không trùng tk -> put dữ liệu lên
        # Trùng -> Thông báo lỗi
        dsTK = get_all_info_database(urlUser, 0)
        print("Danh sách TK: ", dsTK)
        
        # Lấy thông tin đăng ký
        self.tkDki = self.uic.edt_tk_dk.text()
        self.mkDki = self.uic.edt_mk_dk.text()
        self.mkDkiLai = self.uic.edt_mkl_dk.text()
        
        
        # Bắt buộc phải đăng ký tài khoản và mật khẩu
        # Vân tay và Face ID nếu có
        
        if (self.tkDki == "" or self.mkDki == "" or self.mkDkiLai == ""):
            showMessageBox("Đăng ký", "Bạn phải điền tài khoản, mật khẩu")
        else:
            
            if (self.tkDki in dsTK):
                showMessageBox("Đăng ký", "Tài khoản đã tồn tại")
            else:
                if (self.mkDki != self.mkDkiLai):
                    showMessageBox("Đăng ký", "Xác nhận mật khẩu Sai")
                else:
                    
                    print(self.tkDki, self.mkDki, self.mkDkiLai)
                    self.thong_tin_dki = [self.tkDki, self.mkDki]
                    
                    self.idNewUsers = f'User {len(dsTK) + 1}'
                    listNewInfoUser = [self.tkDki, self.mkDki, 'None', 'None'] # tk mk vantay face
                    firebase.put(urlUser, self.idNewUsers, listNewInfoUser)
                    
                    print("Thông tin đăng ký: ", self.thong_tin_dki)
                    showMessageBox("Đăng ký", f"Đăng ký thành công {self.thong_tin_dki}")
                                    
   
     ##################################### HÀM trang chính ################ 
    def trang_chinh(self):

        self.thread_van_tay.stop()
        if tt_Webcam == "Bật":
            self.thread_webcam_face.stop()
        self.uic.stackedWidget.setCurrentWidget(self.uic.trang_chinh)
        
        # Thiet lap cai dat cac nut
        if self.tin_hieu_trang_chinh == False:
            self.uic.btn_dx_user.clicked.connect(self.vao_trang_dang_nhap);
            self.tin_hieu_trang_chinh = True
            
        
    ################################ TRANG QUÊN MẬT KHẨU###########################
    def trang_quen_mat_khau(self):
        self.thread_van_tay.stop()
        if tt_Webcam == "Bật":
            self.thread_webcam_face.stop()
        self.uic.stackedWidget.setCurrentWidget(self.uic.trang_quen_mk)    
        if self.tin_hieu_trang_quen_mat_khau == False:
            self.uic.btn_dn_quen.clicked.connect(self.vao_trang_dang_nhap)
            
            self.tin_hieu_trang_quen_mat_khau = True    
    
    
    #################################### TRANG ĐỔI MẬT KHẨU ########################
    def trang_doi_mat_khau(self):
        self.thread_van_tay.stop()
        if tt_Webcam == "Bật":
            self.thread_webcam_face.stop()
        self.uic.stackedWidget.setCurrentWidget(self.uic.trang_doi_mk)  
def showMessageBox(title, content):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setText(content)
    msg.setWindowTitle(title)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()
    
def get_all_info_database(url, index_info):
    # Danh sach key
    danh_sach_kq = []
    result_get = firebase.get(urlUser, None)
    if result_get != None:
        list_key = result_get.keys()
    
        for key in list_key:
            danh_sach_kq.append(result_get[key][index_info])
        
    return danh_sach_kq
        
if __name__ == '__main__':
    app = QApplication([])
    main_win = MainWindow()
    main_win.show()
    app.exec()

