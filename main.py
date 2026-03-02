import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog, PhotoImage
import os
import hashlib
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
from PIL import Image, ImageTk

attempts = 0  # Biến đếm số lần nhập sai
countdown_active = False  # Biến kiểm soát bộ đếm ngược
countdown_time = 180  # Thời gian đếm ngược 180 giây

def encrypt_email(email):
    encrypted_email = hashlib.sha256(email.encode()).hexdigest()
    return encrypted_email

def encrypt_password(password):
    encrypted_password = hashlib.sha256(password.encode()).hexdigest()
    return encrypted_password

def generate_otp():
    otp = random.randint(100000, 999999)
    return str(otp)

def encrypt_transaction(transaction, password_key):
    key = hashlib.sha256(password_key.encode()).digest()
    print(f"Khóa AES: {key.hex()}")
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(transaction.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    encrypted_transaction = iv + ct
    return encrypted_transaction

def encrypt_otp(otp, password_key, crypto_output_label):
    key = hashlib.sha256(password_key.encode()).digest()
    print(f"Khóa AES: {key.hex()}")
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(otp.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    encrypted_otp = iv + ct
    return encrypted_otp

def decrypt_transaction(encrypted_transaction, password_key):
    try:
        key = hashlib.sha256(password_key.encode()).digest()
        iv = base64.b64decode(encrypted_transaction[:24])
        ct = base64.b64decode(encrypted_transaction[24:])
        cipher = AES.new(key, AES.MODE_CBC, iv)
        transaction = unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')
        return transaction
    except (ValueError, KeyError):
        messagebox.showerror("Lỗi", "Số tiền không hợp lệ.")
        return None

def decrypt_otp(encrypted_otp, password_key, crypto_output_label):
    try:
        key = hashlib.sha256(password_key.encode()).digest()
        iv = base64.b64decode(encrypted_otp[:24])
        ct = base64.b64decode(encrypted_otp[24:])
        cipher = AES.new(key, AES.MODE_CBC, iv)
        otp = unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')
        return otp
    except (ValueError, KeyError):
        messagebox.showerror("Lỗi", "Mã OTP không hợp lệ.")
        return None


def create_account(email, password):
    # Kiểm tra độ dài mật khẩu và loại bỏ mật khẩu chứa dấu cách
    if len(password) < 8 or ' ' in password:
        messagebox.showerror("Lỗi", "Mật khẩu phải có ít nhất 8 ký tự và không chứa khoảng trắng. Vui lòng thử lại!")
        return False
    
    encrypted_email = encrypt_email(email)
    encrypted_password = encrypt_password(password)
    
    # Kiểm tra xem file đã tồn tại chưa
    if os.path.exists(encrypted_email + '.data'):
        messagebox.showerror("Lỗi", "Tài khoản đã tồn tại!")
        return False
    
    with open(encrypted_email + '.data', 'w') as data_file:
        data_file.write(encrypted_email + '\n')
        data_file.write(encrypted_password)
    crypto_output_label.config(text="Email, Mật khẩu đã được mã hóa và lưu trữ trên hệ thống")  # Cập nhật label
    messagebox.showinfo("Thông báo", "Đăng ký tài khoản thành công!")
    
def send_email(receiver_email, encrypted_otp):
    try:
        # Thông tin cấu hình email
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        
        # Tạo message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Mã xác thực OTP cho giao dịch điện tử"
        
        # Nội dung email
        body = f"""
        Xin chào,
        
        Đây là mã OTP đã được mã hóa cho giao dịch điện tử của bạn:
        
        {encrypted_otp}
        
        Vui lòng sao chép mã này và dán vào ứng dụng để xác thực giao dịch.
        Mã OTP sẽ hết hạn sau 3 phút.
        Tuyệt đối không chia sẻ mã OTP này với bất kỳ ai bằng bất kỳ hình thức nào
        
        Trân trọng,
        Hệ thống giao dịch điện tử
        """
        
        message.attach(MIMEText(body, "plain"))
        
        # Gửi email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        
        return True
    except Exception as e:
        print(f"Lỗi gửi email: {e}")
        return False
    
def start_countdown():
    global countdown_active
    countdown_active = True
    countdown(180)  # Bắt đầu từ 180 giây

def countdown(time_left):
    if not countdown_active:
        return  # Dừng đếm ngược nếu giải mã thành công
    
    if time_left >= 0:
        crypto_output_label.config(text=f"Thời gian còn lại để nhập mã OTP: {time_left} giây")
        root.after(1000, countdown, time_left - 1)  # Gọi lại sau 1 giây
    else:
        messagebox.showerror("Hết thời gian", "Giao dịch bị hủy do quá thời gian xác thực OTP!")
        root.destroy()  # Đóng ứng dụng khi hết thời gian

def login(email, password, transaction, crypto_output_label):
    global encrypted_otp, otp_generate, encrypted_transaction, attempts, root, encrypted_transaction

    if not email or not password or not transaction:
        crypto_output_label.config(text="Đăng nhập không thành công. Vui lòng thử lại!")
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ Email, Mật khẩu và Số tiền!")
        return
    
    encrypted_email = encrypt_email(email)
    encrypted_password = encrypt_password(password)
    
    if os.path.exists(encrypted_email + '.data'):
        with open(encrypted_email + '.data', 'r') as data_file:
            stored_email = data_file.readline().rstrip('\n')
            stored_password = data_file.readline()
        
        if encrypted_email == stored_email and encrypted_password == stored_password:
            attempts = 0  # Reset số lần nhập sai nếu đúng
            otp = generate_otp()
            otp_generate = otp  

            encrypted_otp = encrypt_otp(otp, password, crypto_output_label)
            encrypted_transaction = encrypt_transaction(transaction, password)
           
            
            # Gửi OTP đã mã hóa qua email
            email_sent = send_email(email, encrypted_otp)
            
            if email_sent:
                crypto_output_label.config(text=f"Số tiền chuyển khoản đã được mã hóa (AES): {encrypted_transaction}\n"
                 f"Mã OTP đã được mã hóa (AES) và gửi đến email của bạn"
        )
                messagebox.showinfo("Xác minh OTP", "Vui lòng kiểm tra email của bạn để nhận mã OTP")
                start_countdown()  # Bắt đầu đếm ngược 180 giây
                otp_entry.config(state='normal')  
                submit_otp_button.config(state='normal')
            else:
                messagebox.showerror("Lỗi", "Không thể gửi email. Vui lòng kiểm tra lại địa chỉ email và kết nối mạng.")
        else:
            attempts += 1  # Tăng số lần nhập sai
            if attempts >= 3:
                messagebox.showerror("Cảnh báo", "Bạn đã nhập sai quá 3 lần. Giao dịch bị hủy.")
                root.destroy()  # Đóng cửa sổ giao diện
            else:
                crypto_output_label.config(text="Đăng nhập không thành công. Vui lòng thử lại!")
                messagebox.showerror("Lỗi", f"Email hoặc mật khẩu không chính xác. Bạn còn {3 - attempts} lần thử.")
    else:
        crypto_output_label.config(text="Đăng nhập không thành công. Vui lòng thử lại!")
        messagebox.showerror("Lỗi", "Tài khoản không tồn tại. Vui lòng đăng ký tài khoản.")
                
    
def verify_otp():
    entered_otp = otp_entry.get()
    password_key = password_entry.get()
    decrypted_otp = decrypt_otp(encrypted_otp, password_key, crypto_output_label)  

    messagebox.showinfo("Thông báo", "Hệ thống giao dịch điện tử đang xác thực...")
    
    print(f'Entered OTP: {entered_otp}')
    print(f'Decrypted OTP: {decrypted_otp}')
    print(f'Original OTP: {otp_generate}')
    

    if (decrypted_otp == otp_generate) and (entered_otp == encrypted_otp):
        global countdown_active
        countdown_active = False  # Dừng bộ đếm ngược
        crypto_output_label.config(text=f"Mã OTP đã được xác thực thành công: {decrypted_otp}")
        messagebox.showinfo("Thông báo", "Giao dịch thành công!")
        otp_entry.delete(0, 'end')  # Clear the OTP entry after successful login
    else:
        messagebox.showerror("Lỗi", "Mã OTP không chính xác")


def main():
    global otp_entry, submit_otp_button, encrypted_otp, password_entry, crypto_output_label, root, encrypted_transaction
    root = tk.Tk()

    def create_account_ui():
        email = email_entry.get()
        password = password_entry.get()

        create_account(email, password)

        # Reset lại ô nhập sau khi đăng ký thành công
        email_entry.delete(0, 'end')
        password_entry.delete(0, 'end')
        transaction_entry.delete(0, 'end')

    def login_ui():
        email = email_entry.get()
        password = password_entry.get()
        transaction = transaction_entry.get()
    
        crypto_output_label.config(text="Đăng nhập thành công! Vui lòng chờ trong giây lát...")
        root.update_idletasks()  # Cập nhật giao diện ngay lập tức

        login(email, password, transaction, crypto_output_label)
        
    def validate_email(email):
        import re
        # Kiểm tra định dạng email 
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if re.match(pattern, email):
            return True
        return False
    
    def validate_email_input(event):
        email = email_entry.get()
        if email and not validate_email(email):
            messagebox.showerror("Lỗi", "Định dạng email không hợp lệ!")
            
    def validate_transaction(event):
        transaction = transaction_entry.get()
        if not transaction.isdigit():
            messagebox.showerror("Lỗi", "Số tiền không hợp lệ!")
            transaction_entry.delete(0, 'end')  
     

    
    root.title("Ứng dụng mã hóa AES và xác thực hai lớp")
    root.geometry("600x800")
    root.config(bg="#f8c8d0")
    
    btn_color = "#3498db"
    input_color = "#ffffff"
    
     # Tạo Notebook và các tab
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Tạo frame cho từng tab
    sender_tab = tk.Frame(notebook, bg="#f8c8d0")
    receiver_tab = tk.Frame(notebook, bg="#f8c8d0")
    notebook.add(sender_tab, text="Người gửi")
    notebook.add(receiver_tab, text="Người nhận")
    
    # Load hình ảnh từ đường dẫn trong máy
    image_path = "C:/Users/AnhNP/Documents/ĐỀ TÀI ANTT_NHÓM 5/image_antt.png"  
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError  # Nếu không có file, kích hoạt ngoại lệ
        
        image = Image.open(image_path)
        image = image.resize((100, 100))  
        photo = ImageTk.PhotoImage(image)

        #   Hiển thị ảnh trong giao diện
        image_label = tk.Label(receiver_tab, image=photo, bg="#FFF9C4")
        image_label.image = photo  
        image_label.pack(pady=10, padx=10, anchor="nw", side="top")
        
    except FileNotFoundError:
        # Nếu không tìm thấy hình ảnh
        pass
    
    user_frame = tk.LabelFrame(sender_tab, text="Người Gửi", padx=10, pady=20, bg="#FFF9C4", fg="#2c3e50", font=("Helvetica", 16))
    user_frame.pack(pady=10, fill="x", padx=70)

    register_frame = tk.Frame(user_frame, bg="#FFF9C4")
    register_frame.pack(pady=5, fill="x")

    tk.Label(register_frame, text="Email:", font=("Helvetica", 14), bg="#FFF9C4", fg="#2c3e50").pack(anchor="center")
    email_entry = tk.Entry(register_frame, font=("Helvetica", 14), bg=input_color, fg="#2c3e50", relief="solid", bd=2)
    email_entry.pack(anchor="center", pady=5, ipadx=10, ipady=5)
    email_entry.bind("<FocusOut>", validate_email_input)

    tk.Label(register_frame, text="Mật khẩu:", font=("Helvetica", 14), bg="#FFF9C4", fg="#2c3e50").pack(anchor="center")
    password_entry = tk.Entry(register_frame, show="*", font=("Helvetica", 14), bg=input_color, fg="#2c3e50", relief="solid", bd=2)
    password_entry.pack(anchor="center", pady=5, ipadx=10, ipady=5)

    tk.Label(register_frame, text="Số tiền (VNĐ):", font=("Helvetica", 14), bg="#FFF9C4", fg="#2c3e50").pack(anchor="center")
    transaction_entry = tk.Entry(register_frame, show="*", font=("Helvetica", 14), bg=input_color, fg="#2c3e50", relief="solid", bd=2)
    transaction_entry.pack(anchor="center", pady=5, ipadx=10, ipady=5)
    transaction_entry.bind("<KeyRelease>", validate_transaction)
    
    # Nút "Create Account" xếp bên trái và Nút "Login" xếp bên phải
    tk.Button(register_frame, text="Đăng ký", command=create_account_ui, font=("Helvetica", 12, "bold"), bg=btn_color, fg="#ffffff", relief="solid", width=15).pack(side="left", padx=10, pady=2)
    tk.Button(register_frame, text="Đăng nhập và\nChuyển khoản", command=login_ui, font=("Helvetica", 12, "bold"), bg=btn_color, fg="#ffffff", relief="solid", width=15).pack(side="right", padx=10, pady=2)

    # Label "Enter Encrypted OTP:" 
    tk.Label(sender_tab, text="Nhập mã OTP đã mã hóa:", font=("Helvetica", 12, "bold"), fg="#2c3e50").pack(pady=2, padx=10, anchor="center")

    # Ô nhập OTP 
    otp_entry = tk.Entry(sender_tab, font=("Helvetica", 14), bg=input_color, fg="#2c3e50", relief="solid", bd=2)
    otp_entry.pack(anchor="center", pady=5, ipadx=40, ipady=5)  # Tăng ipadx và ipady để ô rộng hơn

    # Nút "Decrypt OTP and Submit" 
    submit_otp_button = tk.Button(sender_tab, width=22, text="Giải mã và xác thực OTP", command=verify_otp, font=("Helvetica", 12, "bold"), bg="white", fg="black", relief="solid")
    submit_otp_button.pack(pady=10)

    # Ban đầu vô hiệu hóa nút submit OTP
    submit_otp_button.config(state='disabled')
    crypto_frame = tk.LabelFrame(sender_tab, text="Hệ thống giao dịch điện tử", padx=30, pady=30, bg="#FFF9C4", fg="#2c3e50", font=("Helvetica", 16))
    crypto_frame.pack(pady=30, fill="x", padx=30)

    crypto_output_label = tk.Label(crypto_frame, text="Hệ thống giao dịch điện tử đang chờ dữ liệu...", font=("Helvetica", 12), fg="#2c3e50", bg="#FFF9C4", wraplength=500)
    crypto_output_label.pack(pady=10)
    
    #Tab người nhận
    # Khung chứa ô nhập và nút giải mã
    receiver_frame = tk.LabelFrame(receiver_tab, text="Người nhận", padx=10, pady=10, bg="#FFF9C4", fg="#2c3e50", font=("Helvetica", 16))
    receiver_frame.pack(pady=10, fill="x", padx=30)

    # Ô nhập để hiển thị số tiền nhận được
    tk.Label(receiver_frame, text="Số tiền nhận được (VNĐ):", font=("Helvetica", 14), bg="#FFF9C4", fg="#2c3e50").pack(anchor="center", padx=10)
    received_amount_entry = tk.Entry(receiver_frame, font=("Helvetica", 14), bg=input_color, fg="#2c3e50", relief="solid", bd=2, state='readonly')
    received_amount_entry.pack(anchor="center", pady=5, padx=10, ipadx=10, ipady=5)

      # Hàm giải mã và hiển thị số tiền
    def decode_amount():
        password_key = password_entry.get()
        decrypted_transaction = decrypt_transaction(encrypted_transaction, password_key)
        if decrypted_transaction:
            received_amount_entry.config(state='normal')  
            received_amount_entry.delete(0, 'end')  
            received_amount_entry.insert(0, decrypted_transaction)  # Hiển thị số tiền giải mã
            received_amount_entry.config(state='readonly')  # Khóa lại ô nhập
            messagebox.showinfo("Thông báo", f"Số tiền được giải mã thành công! Bạn đã được chuyển khoản {decrypted_transaction} VNĐ!")
        else:
            messagebox.showerror("Lỗi", "Không thể giải mã số tiền.")

    # Nút để giải mã số tiền
    decode_button = tk.Button(receiver_frame, text="Giải mã", command=decode_amount, font=("Helvetica", 12, "bold"), bg=btn_color, fg="#ffffff", relief="solid")
    decode_button.pack(pady=5, padx=10, anchor="center")

    progress_bar = ttk.Progressbar(receiver_tab, orient="horizontal", length=200, mode="indeterminate")
    progress_bar.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()