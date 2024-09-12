import sys
sys.path.append('/home/lapdo/NCKH/lib/python3.11/site-packages')


from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtWidgets import QLabel, QPushButton, QGridLayout, QTableWidgetItem,QLineEdit, QApplication, QMainWindow, QMessageBox, QFileDialog
from PyQt6.QtGui import QBrush, QColor, QFont, QIcon, QPixmap, QImage
from gui_main import Ui_MainWindow
from datetime import datetime
import numpy as np
import cv2
import cam_bien_van_tay as vt
import time, random
import emailPython

# Khởi tạo firebase
from firebase import firebase
firebase = firebase.FirebaseApplication('https://fir-firebase-2eb50-default-rtdb.asia-southeast1.firebasedatabase.app', None)

urlUser = "/Users"
tt_Webcam = "Tắt"

urlSlTB = "/So_luong_thiet_bi"
urlSlMg = "/So_luong_may_giat"
urlSlMs = "/So_luong_may_say"

idVt_thanh_cong = 0;
dang_xuat = 0

# Class Thread kiểm tra vân tay đăng nhập
class FingerPrintThread(QThread):
    # Tín hiệu gửi về khi vân tay đăng nhập hợp lệ
    signal_van_tay_dang_nhap_hop_le = pyqtSignal()
    signal_van_tay_that_bai = pyqtSignal(str, str)
    
    
    def __init__(self, parent=None):
        super(FingerPrintThread, self).__init__(parent)
        self.running = True # Biến điều khiển Thread
        
    def run(self):
        global tt_Webcam, idVt_thanh_cong, dang_xuat
        while self.running:
            print("Thread van tay")
            
            idVt_thanh_cong, stateFind_FingerPrint = self.get_fingerprint_id()
            
            # Lấy danh sách vân tay
            
            
            if stateFind_FingerPrint == True:
                # Nếu vân tay hợp lệ, phát tín hiệu để giao diện biết
                self.signal_van_tay_dang_nhap_hop_le.emit()
                
                break
            elif stateFind_FingerPrint == False:
                if dang_xuat == 0:
                    self.signal_van_tay_that_bai.emit("Đăng nhập", "Đăng nhập Vân tay Không thành công") # truyền tín hiệu tới
                else:
                    dang_xuat = 0
            time.sleep(1.5)
                    
            
            
    def stop(self):
        self.running = False  # Đặt biến điều khiển để dừng luồng
        self.terminate()

    def get_fingerprint_id(self):
        try:
            ds_vanTay = get_all_info_database(urlUser, 2)
            # Viết hàm quét vân tay
            idVt, state_find = vt.find_van_tay()
            return idVt, state_find
        except:
            return 0, False
        


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
        
        self.uic.cb_mk_dn.stateChanged.connect(lambda: self.hidden_show_text(self.uic.cb_mk_dn, self.uic.Edt_mk_dn))
        
        
    # Hàm đăng nhập
    # SHow mess đăng nhập VÂN TAY KHÔNG thành công
    def show_message(self, title, content):
        global tt_Webcam
        showMessageBox(title, content)
        
        
        
    def xac_nhan_dang_nhap(self):
        global tt_Webcam
        # Lấy danh sách người dùng
        self.dsTK = get_all_info_database(urlUser, 0)
        self.dsMk = get_all_info_database(urlUser, 1)
        
        # dsFace = get_all_info_database(urlUser, 3)
        
        # Lấy thông tin đăng nhập
        self.tkDn = self.uic.Edt_tk_dn.text()
        self.mkDn = self.uic.Edt_mk_dn.text()
        idVt = self.uic.lb_vt_dn.text()
        idFace = self.uic.lb_id_face_dn.text()
        
        if (self.tkDn == "" and self.mkDn == "" and idVt == ""):
            showMessageBox("Đăng nhập", "Đăng Nhập không thành công\nĐăng nhập bằng tài khoản/ Quét vân tay")
            
        # Trường họp đăng nhập bằng tk mk
        elif (self.tkDn != "" and self.mkDn != ""): 
            
            print("Đăng nhập bằng tài khoản")
            if self.tkDn not in self.dsTK:
                showMessageBox("Đăng Nhập", "Không tồn tại tài khoản")
            else:
                index_tkDn = self.dsTK.index(self.tkDn)
                if self.mkDn == self.dsMk[index_tkDn]:
                    
                    # Đăng nhập thành công
                    showMessageBox("Đăng Nhập", "Đăng Nhập bằng Tài khoản thành công")
                    
                    self.trang_chinh()
                else:
                    showMessageBox("Đăng Nhập", "Đăng Nhập không thành công\nSai mật khẩu/TK")
                    
        
            
    # Hàm xử lý khi vân tay được xác nhận
    def dang_nhap_van_tay_thanh_cong(self):
        global tt_Webcam
        print("Đăng Nhập", "Đăng Nhập bằng Vân tay thành công")
        
        time.sleep(1)
        self.trang_chinh()


    
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
            
        self.uic.cb_mkdki.stateChanged.connect(lambda: self.hidden_show_text(self.uic.cb_mkdki, self.uic.edt_mk_dk))
        self.uic.cb_mkl_dki.stateChanged.connect(lambda: self.hidden_show_text(self.uic.cb_mkl_dki, self.uic.edt_mkl_dk))
        
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
            state_tk_van_tay_dki = check_dang_ky_tai_khoan(self.tkDki, self.mkDki, self.mkDkiLai)
            if state_tk_van_tay_dki == True:
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
                            self.clear_trang_dang_ky()
                            showMessageBox("Đăng ký", "Bạn đăng ký TK và Vân tay thành công")
                except:
                    showMessageBox("Vân tay", "Lỗi cảm biến vân tay")
        

    
    def xac_nhan_dang_ky(self):
        # Lấy danh sách người dùng
        # Không trùng tk -> put dữ liệu lên
        # Trùng -> Thông báo lỗi
        
        # Lấy thông tin đăng ký
        self.tkDki = self.uic.edt_tk_dk.text()
        self.mkDki = self.uic.edt_mk_dk.text()
        self.mkDkiLai = self.uic.edt_mkl_dk.text()
        
        
        # Bắt buộc phải đăng ký tài khoản và mật khẩu
        # Vân tay và Face ID nếu có
        
        state_dang_ky_tk = check_dang_ky_tai_khoan(self.tkDki, self.mkDki, self.mkDkiLai)
        if state_dang_ky_tk == True:
            self.clear_trang_dang_ky()
            showMessageBox("Thông báo", "Đăng ký tài khoản thành công")
        else:
            showMessageBox("Thông báo", state_dang_ky_tk)
            
   
     ##################################### HÀM trang chính ################ 
    def trang_chinh(self):
        global idVt_thanh_cong, dang_xuat
        dang_xuat = 2
        self.clear_trang_dang_ky()
        self.clear_trang_dang_nhap()
        
        dict_slTB = dict(firebase.get(urlSlTB, None))
        slThietBi = sum(dict_slTB.values())
        print("So luong thiet bi: ", dict_slTB)
        slMG = dict_slTB["So_luong_may_giat"]
        slMS = dict_slTB["So_luong_may_say"]

        self.thread_van_tay.stop()
        if tt_Webcam == "Bật":
            self.thread_webcam_face.stop()
        self.uic.stackedWidget.setCurrentWidget(self.uic.trang_chinh)
        
        # Thiet lap cai dat cac nut
        if self.tin_hieu_trang_chinh == False:
            self.uic.btn_dx_user.clicked.connect(self.vao_trang_dang_nhap);
            
            
            # Lay so luong tung thiet bi
            gridLayoutTB = QGridLayout()
            for i in range (slThietBi):
                if i<= slMG-1:
                    name_tb = f"May giat {i+1}"
                    
                    styleSheet = """
                        background-color: rgb(255, 69, 112);
                        font-size: 15px;
                        """
                else:
                    name_tb = f"May say {i+1}"
                    
                    styleSheet = """
                        background-color: rgb(180, 227, 25);
                        font-size: 15px;
                        """
                
                lb_may = QLabel(name_tb)
                lb_may.setAlignment(Qt.AlignmentFlag.AlignCenter)
                gridLayoutTB.addWidget(lb_may, 0, i)
                
                btn_may = QPushButton(name_tb)
                gridLayoutTB.addWidget(btn_may, 1 , i)
                
                btn_may.setStyleSheet(styleSheet)
                
                
                # Trang thai hoat dong cua may
                tt_may = QLabel(f"Trang thai {name_tb}")
                tt_may.setAlignment(Qt.AlignmentFlag.AlignCenter)
                gridLayoutTB.addWidget(tt_may, 2, i)
                
                self.tin_hieu_trang_chinh = True
                
            # Áp dụng layout cho widget chính
            self.uic.fram_thiet_bi.setLayout(gridLayoutTB)

        
        
        #Truy xuất ra tk dang nhap bang van tay
        listIDVanTay = get_all_info_database(urlUser, 2)
        
        
        if idVt_thanh_cong != 0:
            index_tk = listIDVanTay.index(idVt_thanh_cong)
            tkDN = self.dsTK[index_tk]
            self.uic.lb_tk_dn.setText(tkDN)
        else:
            self.uic.lb_tk_dn.setText(self.tkDn)

        self.uic.lb_tk_dn.adjustSize()
        
    ################################ TRANG QUÊN MẬT KHẨU###########################
    def trang_quen_mat_khau(self):
        # He thong se gui mat khau moi ve email cua ban
        
        
        
        self.thread_van_tay.stop()
        if tt_Webcam == "Bật":
            self.thread_webcam_face.stop()
        self.uic.stackedWidget.setCurrentWidget(self.uic.trang_quen_mk)    
        
        
        if self.tin_hieu_trang_quen_mat_khau == False:
            self.uic.btn_dn_quen.clicked.connect(self.vao_trang_dang_nhap)
            self.uic.btn_xn_clmk.clicked.connect(self.cap_lai_mat_khau) 
            self.tin_hieu_trang_quen_mat_khau = True    
            # edt_tk_quenmk, btn_xn_clmk
            
        
    
    
    #################################### TRANG ĐỔI MẬT KHẨU ########################
    def trang_doi_mat_khau(self):
        global dang_xuat
        
        dang_xuat = 2
        self.thread_van_tay.stop()
        if tt_Webcam == "Bật":
            self.thread_webcam_face.stop()
        self.uic.stackedWidget.setCurrentWidget(self.uic.trang_doi_mk)
        
        if self.tin_hieu_trang_doi_mat_khau == False:
            self.uic.btn_xn_doi_mk.clicked.connect(self.xac_nhan_doi_mat_khau)
            self.uic.btn_ql_dn_doimk.clicked.connect(self.vao_trang_dang_nhap)
            self.tin_hieu_trang_doi_mat_khau = True
            
        self.uic.cb_mk_cu.stateChanged.connect(lambda: self.hidden_show_text(self.uic.cb_mk_cu, self.uic.edt_mkcu))
        self.uic.cb_mkmoi.stateChanged.connect(lambda: self.hidden_show_text(self.uic.cb_mkmoi, self.uic.edt_mk_moi))
        self.uic.cb_xnmk_moi.stateChanged.connect(lambda: self.hidden_show_text(self.uic.cb_xnmk_moi, self.uic.edt_xn_mkmoi))
    
    def xac_nhan_doi_mat_khau(self):
        tk = self.uic.edt_tk_doi_mk.text()
        mkcu = self.uic.edt_mkcu.text()
        mk_moi1 = self.uic.edt_mk_moi.text()
        mk_moi_xac_nhan = self.uic.edt_xn_mkmoi.text()
        
        dsTK = get_all_info_database(urlUser, 0)
        dsMK = get_all_info_database(urlUser, 1)
        dsVT = get_all_info_database(urlUser, 2)
        dsFace = get_all_info_database(urlUser, 3)   
        
        if len(tk) > 0 and len(mkcu) > 0 and len(mk_moi1) > 0 and len(mk_moi_xac_nhan) > 0:
            if tk in dsTK:
                index_user = dsTK.index(tk)
                name_user = f"User {index_user}"
                if mkcu == dsMK[index_user]:
                    if len(mk_moi1) >= 8:
                        if mk_moi1 != mkcu:
                            if mk_moi1 == mk_moi_xac_nhan:
                                replace_new_info = [tk, mk_moi1, dsVT[index_user], dsFace[index_user]]
                                firebase.put(urlUser, name_user, replace_new_info)
                                self.clear_trang_doi_mat_khau()
                                showMessageBox("Thông báo", "Đổi mật khẩu thành công")
                            else:
                                showMessageBox("Thông báo", "Xác nhận lại mật khẩu")
                        else:
                            showMessageBox("Thông báo", "Tùng mật khẩu cũ")
                    else:
                        showMessageBox("Thông báo", "Mật khẩu lớn hơn 8 ký tự")
                else:
                    showMessageBox("Thông báo", "Sai mật khẩu cũ")
            else:
                showMessageBox("Thông báo", "Tài khoản không tồn tại")
        else:
            showMessageBox("Thông báo", "Vui lòng nhập đầy đủ thông tin")
        
    
    
        
    def clear_trang_dang_ky(self):
        self.uic.edt_tk_dk.clear()
        self.uic.edt_mk_dk.clear()
        self.uic.edt_mkl_dk.clear()
    
    def clear_trang_dang_nhap(self):
        self.uic.Edt_tk_dn.clear()
        self.uic.Edt_mk_dn.clear()
        
    def clear_trang_quen_mat_khau(self):
        self.uic.edt_tk_quenmk.clear()
        
    def clear_trang_doi_mat_khau(self):
        self.uic.edt_tk_doi_mk.clear()
        self.uic.edt_mkcu.clear()
        self.uic.edt_mk_moi.clear()
        self.uic.edt_xn_mkmoi.clear()
    
    def hidden_show_text(self, cb_edt, edt_text):
        
        if cb_edt.isChecked() == True:
            edt_text.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            edt_text.setEchoMode(QLineEdit.EchoMode.Password)
            
            
    def cap_lai_mat_khau(self):
        global dang_xuat
        dang_xuat = 2
        tkClMk = self.uic.edt_tk_quenmk.text()
        dsTK = get_all_info_database(urlUser, 0)
        
        dsVT = get_all_info_database(urlUser, 2)
        dsFace = get_all_info_database(urlUser, 3)
        
        index_tk = dsTK.index(tkClMk)
        name_user = f'User {index_tk}'
        
        
        if tkClMk not in dsTK:
            showMessageBox("Thông báo", "Tài khoản không tồn tại")
        else:
            rdNewMk = str(random.randint(10**6, 10**8))
            
            replace_info_user = [tkClMk, rdNewMk, dsVT[index_tk], dsFace[index_tk]]
            
            
            state_send = emailPython.sendEmail(email_sender = "lap2003dodang@gmail.com", email_password = "jgsa mvte plxs ilqg", email_receiver = tkClMk, subject = "Cấp lại mật khẩu", body = rdNewMk) 
            if state_send == True:
                showMessageBox("Thông báo", "Hệ thống đã gửi mật khẩu mới qua gmail của bạn")
                firebase.put(urlUser, name_user, replace_info_user)
                self.clear_trang_quen_mat_khau()
                self.vao_trang_dang_nhap()
                
            else:
                showMessageBox("Thông báo", "Lỗi hệ thống gửi gmail")
    
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
    
def check_tk_gmail(tk_input):
    '''
    gmail: abcd@gmail.com
    '''
    if tk_input[0] != "@":
        if tk_input.split("@")[-1] == "gmail.com":
            return True
        else:
            return False
    else:
        return False    
        
        
def check_dang_ky_tai_khoan(tkDki, mkDki, mkDkiLai):
    dsTK = get_all_info_database(urlUser, 0)
    if (tkDki == "" or mkDki == "" or mkDkiLai == ""):
                return "Bạn phải điền tài khoản, mật khẩu"
    else:
        if check_tk_gmail(tkDki):
            if (tkDki in dsTK):
                return "Tài khoản đã tồn tại"
            else:
                if len(mkDki) >= 8:
                    if (mkDki != mkDkiLai):
                        return "Xác nhận mật khẩu Sai"
                    else:
                        
                        print(tkDki, mkDki, mkDkiLai)
                        thong_tin_dki = [tkDki, mkDki]
                        
                        idNewUsers = f'User {len(dsTK) + 1}'
                        listNewInfoUser = [tkDki, mkDki, 'None', 'None'] # tk mk vantay face
                        firebase.put(urlUser, idNewUsers, listNewInfoUser)
                        
                        print("Thông tin đăng ký: ", thong_tin_dki)
                        return True
                else:
                    return "Mật khẩu lớn hơn 8 ký tự"
        else:
            
            return "Sai định dạng gmail tài khoản"
            

if __name__ == '__main__':
    app = QApplication([])
    main_win = MainWindow()
    main_win.show()
    app.exec()

