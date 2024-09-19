# Đẩy dữ liệu lên firebase (Cap nhat du lieu)
from firebase import firebase
import pandas as pd
firebase = firebase.FirebaseApplication('https://fir-firebase-2eb50-default-rtdb.asia-southeast1.firebasedatabase.app', None)
pK = '/Phong_khach'
# led01 = '/LED01'
# stateLed01 = 'OFF'

# led02 = '/LED02'
# stateLed02 = 'OFF'
# /Phong_khach/Led 1/OFF

# result = firebase.put(pK, led01, stateLed01) 
# result = firebase.put(pK, led02, stateLed02) 
# print("Đẩy dữ liệu thành công")

# Doc du lieu ve dung get
# Doc tat ca du lieu tu /Phong_khach
# result_get = firebase.get(pK, None)
# print("Du lieu tu Phong_khach: ", result_get) #{'LED01': 'OFF', 'LED02': 'OFF'}

# # Doc du lieu trang thai cua LED01 (Doc theo key)
# result2 = firebase.get(pK, led01)
# print("Du lieu Phong_khach/LED01: ", result2)

# # Xoa du lieu



urlUser = "/Users"
user1 = "/User 1"
infoLogin = ["lapdodang@gmail.com", "12345678", "None", 1]
firebase.put(urlUser, "User 0", infoLogin)

# firebase.delete(urlUser, None)
# result = firebase.put(urlUser, user1, infoLogin) 
urlSlTB = "/So_luong_thiet_bi"
urlSlMg = "/So_luong_may_giat"
slMg = 2

urlSlMs = "/So_luong_may_say"
slMs = 2

urlLichHoatDong = "/Lich_hoat_dong"

# firebase.put(urlLichHoatDong, "0", ["Tài khoản", "Thiết bị", "Ngày", "Bắt đầu", "Kết thúc"])
# firebase.put(urlLichHoatDong, "1", ["Tài khoản", "Thiết bị", "Ngày", "Bắt đầu", "Kết thúc"])


# def danh_sach_lich_hoat_dong(urlLichHoatDong):
    
#     result = firebase.get(urlLichHoatDong, None)
    
#     print(result)
#     tkDatLich = []
#     tbiDatLich = []
#     ngayDatLich = []
#     tgianBatDau = []
#     tgianKetThuc = []
#     if result != None:
#         for i in range (len(result)):
#             tkDatLich.append(result[i][0])
#             tbiDatLich.append(result[i][1])
#             ngayDatLich.append(result[i][2])
#             tgianBatDau.append(result[i][3])
#             tgianKetThuc.append(result[i][4])
    
#     dataFrame = pd.DataFrame({"Tài khoản": tkDatLich, "Thiết bị":tbiDatLich, "Ngày":ngayDatLich, 
#                               "Bắt đầu":tgianBatDau, "Kết thúc":tgianKetThuc})
#     return dataFrame

# print(danh_sach_lich_hoat_dong(urlLichHoatDong))
# result_get = firebase.get(urlSlMg, None)

# print(result_get == None)

# def get_all_info_database(url, index_info):
#     # Danh sach key
#     danh_sach_kq = []
#     result_get = firebase.get(urlUser, None)
#     list_key = result_get.keys()
    
#     for key in list_key:
#         danh_sach_kq.append(result_get[key][index_info])
        
#     return danh_sach_kq






