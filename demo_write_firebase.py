# Đẩy dữ liệu lên firebase (Cap nhat du lieu)
from firebase import firebase
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



# urlUser = "/Users"
# user1 = "/User 1"
# infoLogin = ["Đỗ Đăng Lập", "aaaaaaaaaaaaa", 1, 1]

# firebase.delete(urlUser, None)
# result = firebase.put(urlUser, user1, infoLogin) 
urlSlTB = "/So_luong_thiet_bi"
urlSlMg = "/So_luong_may_giat"
slMg = 2

urlSlMs = "/So_luong_may_say"
slMs = 2

# firebase.put(urlSlTB, urlSlMg, slMg)
# firebase.put(urlSlTB, urlSlMs, slMs)
result = firebase.get(urlSlTB, None)
print(sum(result.values()))
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




