def check_dang_ky_tai_khoan(tkDki, mkDki, mkDkiLai):
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
                        return f"Đăng ký thành công {thong_tin_dki}"
                else:
                    return "Mật khẩu lớn hơn 8 ký tự"
        else:
            
            return "Sai định dạng gmail tài khoản"
        
