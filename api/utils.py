from pywinauto import Application, findwindows
import time
import pyautogui
from pywinauto.keyboard import send_keys
import os, sys
import pyperclip
# Load environment variables
# Bước 1: Mở Zalo Desktop
def find_to_zalo(sleeping_time, zalo_path):
    # zalo_path = rf"{zalo_path}"
    # zalo_path = os.getenv('ZALO_PATH')
    app = Application().start(zalo_path)
    time.sleep(sleeping_time)

    windows = findwindows.find_windows(title="Zalo", backend="win32")

    if not windows:
        print("Không tìm thấy cửa sổ Zalo!")
        exit()

    app = Application(backend="uia").connect(handle=windows[0])
    zalo_window = app.window(title="Zalo")
    print("Kết nối thành công với Zalo!")
    return zalo_window

def add_friend(zalo_window, phone_number, sleeping_time, waiting_for_add_friend_time, default_delta_y_search=0):
    print("đã vào add friend")
    search_box = zalo_window.child_window(auto_id="contact-search-input", control_type="Edit")
    print(search_box)
    search_box.click_input()
    print("đã vào search box")
    time.sleep(sleeping_time)

    zalo_window.type_keys(phone_number, with_spaces=True)  
    time.sleep(1.5)
    found = False

    for child in zalo_window.descendants():
        if "Số điện thoại:" in child.window_text():
            screen_width, screen_height = pyautogui.size()

            x_ratio = 299 / 1920  # Giả sử màn hình gốc là 1920x1080
            y_ratio = 247 / 1080

            # Áp dụng tọa độ trên màn hình mới
            new_x = int(screen_width * x_ratio)
            new_y = int(screen_height * y_ratio)

            pyautogui.click(new_x, new_y - default_delta_y_search)
            found = True
            break

    if not found:
        print("Không tìm thấy người này!")
        search_box.set_edit_text("")  # Xóa nội dung ô tìm kiếm
        return False

    time.sleep(1)
    try:
        friend_btn = zalo_window.child_window(title="Gửi kết bạn", control_type="Text")
        if friend_btn:
            friend_btn.click_input()
            time.sleep(sleeping_time)
            friend_btn = zalo_window.child_window(title="Kết bạn", control_type="Text")
            friend_btn.click_input()
            print("Đã gửi lời mời kết bạn thành công!",friend_btn)
            time.sleep(waiting_for_add_friend_time)
            return True
    except:
        print("Đã gửi lời mời đến người này rồi!")
        return True
def send_message(zalo_window,default_delta_y=0, is_have_image=False,full_message=None,send_type="winv",wait_image_loading_time=3):
    print("Thời gina cừ",wait_image_loading_time)
    for child in zalo_window.descendants():
        if "Nhập @, tin nhắn tới" in child.window_text():
            print("Tìm thấy ô chat!")
            pyperclip.copy(full_message)

            # Click vào ô chat
            screen_width, screen_height = pyautogui.size()
            x_ratio = 733 / 1920
            y_ratio = 984 / 1080
            new_x = int(screen_width * x_ratio)
            new_y = int(screen_height * y_ratio - default_delta_y)
            pyautogui.click(new_x, new_y)
            if send_type == "winv":
                pyautogui.hotkey("win", "v")
                time.sleep(0.5)
                send_keys("{ENTER}")  # Mũi tên xuống để chọn phần tử tiếp theo
                if is_have_image:
                    time.sleep(0.25)
                    pyautogui.hotkey("win", "v")
                    time.sleep(0.5)
                    send_keys("{DOWN}")  
                    send_keys("{ENTER}") 
                    time.sleep(wait_image_loading_time)

                send_keys("{ENTER}")
                break
            elif send_type == "ctrlv":
                send_keys("^v")
                time.sleep(0.5)  # Chờ thêm cho đến khi ảnh load
                send_keys("{ENTER}")
                time.sleep(0.2)
                break

def resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối đến file trong bản đóng gói"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def refresh_zalo_window():
    """
    Kết nối lại với cửa sổ Zalo đã mở (không khởi động lại Zalo).
    """
    try:
        windows = findwindows.find_windows(title="Zalo", backend="win32")
        if not windows:
            print("Không tìm thấy cửa sổ Zalo để làm mới!")
            return None

        app = Application(backend="uia").connect(handle=windows[0])
        zalo_window = app.window(title="Zalo")
        return zalo_window
    except Exception as e:
        print(f"Lỗi khi làm mới cửa sổ Zalo: {e}")
        return None


# Khai báo biến toàn cục ngoài hàm (nếu chưa có)
has_reached_bottom_once = False
last_still_exists = False
index_click = 0
def scroll_and_click(zalo_window, delta_scroll=300,element_rect=None,item_spacing=95,target_text="",index=0):
    """
    Cuộn xuống danh sách chat một đoạn và click vào vị trí phía dưới phần tử "Tất cả".
    Nếu phần tử `last_username` vẫn còn sau khi scroll, thì coi như không thể scroll thêm nữa.
    """
    global has_reached_bottom_once
    global last_still_exists
    global index_click
    # Bước 1: Lấy group chat
    conversation_group = zalo_window.child_window(title="grid", auto_id="conversationListId", control_type="Group").wrapper_object()
    group_rect = conversation_group.rectangle()
    print("Group rectangle:", group_rect)

    center_x = int(group_rect.mid_point().x)
    center_y = int(group_rect.mid_point().y)
    pyautogui.moveTo(center_x, center_y)

    delta_scroll = int(delta_scroll - index * 0.45)
    pyautogui.scroll(-delta_scroll)

    # Lấy lại danh sách các phần tử sau khi scroll
    conversation_group = zalo_window.child_window(title="grid", auto_id="conversationListId", control_type="Group").wrapper_object()
    child_texts = [child.window_text() for child in conversation_group.children()]
    
    print("Danh sách chat sau scroll:", child_texts)

    click_x = int(element_rect.mid_point().x)


    # Kiểm tra xem last_username còn tồn tại không
    if last_still_exists == False:
        is_end_scroll = check_is_end_scroll(zalo_window, target_text)
        if is_end_scroll:
            last_still_exists = True
            print("last_still_exists", last_still_exists)
    
    if last_still_exists:
        print("index", index_click)
        index_click += 1
        click_y = int(element_rect.bottom + item_spacing * index_click)
            

    else:
        click_y = int(element_rect.bottom + 50)

    print("Click coordinates:", click_x, click_y)
    pyautogui.moveTo(click_x, click_y)
    pyautogui.click()


from PIL import Image
from io import BytesIO
import win32clipboard
import win32con
from PIL import ImageGrab
def send_image_to_clipboard(image_path, retry=5, delay=0.5):
    print(f"Đang xử lý ảnh: {image_path}")
    image = None

    # Thử mở ảnh nhiều lần nếu chưa sẵn sàng
    for i in range(retry):
        try:
            image = Image.open(image_path)
            image.load()  # Đảm bảo ảnh được load vào RAM
            break
        except Exception as e:
            print(f"Lần {i+1}: Chưa mở được ảnh - {e}")
            time.sleep(delay)
    else:
        print("Không thể mở ảnh sau nhiều lần thử.")
        return

    # Chuyển ảnh sang dạng DIB
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]  # Bỏ header BMP
    output.close()

    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_DIB, data)
        win32clipboard.CloseClipboard()
        print("✅ Ảnh đã được copy vào clipboard.")
    except Exception as e:
        print(f"❌ Lỗi khi sao chép ảnh vào clipboard: {e}")
def send_image_file(zalo_window, file_path,default_delta_y = 0,wait_image_loading_time=3):

    send_image_to_clipboard(file_path)
    send_keys("^v")
    time.sleep(wait_image_loading_time)  # Chờ thêm cho đến khi ảnh load
    send_keys("{ENTER}")
    print("Đã gửi ảnh từ clipboard.")
import re

import unicodedata
def normalize_text(text):
    # Loại bỏ các ký tự không phải chữ cái, số, hoặc khoảng trắng (giữ cả tiếng Việt có dấu)
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r"[^\w\sÀ-Ỹà-ỹ]", "", text)  # loại bỏ ký tự đặc biệt
    text = " ".join(text.split())  # chuẩn hóa khoảng trắng (xóa khoảng trắng thừa)
    return text.lower()

def check_is_end_scroll(zalo_window, text_to_find):
    try:
        group_element = zalo_window.child_window(auto_id="chatViewContainer", control_type="Group").wrapper_object()
        raw_text = group_element.window_text()
        print("Raw group element text:", raw_text)
    except Exception as e:
        print(f"Lỗi khi tìm kiếm phần tử group: {e}")
        return False

    cleaned_text = normalize_text(raw_text)
    target_text = normalize_text(text_to_find)

    print("Normalized text in group:", cleaned_text)
    print("Target to find:", target_text)

    if target_text in cleaned_text:
        print(f"✅ Đã tìm thấy văn bản '{text_to_find}' trong group.")
        return True
    else:
        print(f"❌ Chưa tìm thấy văn bản '{text_to_find}' trong group.")
        return False



def send_message_to_all(zalo_window, list_messages, file_path, num_convos, delta_scroll, default_delta_y=0, item_spacing=95, target_text="", is_real=False,send_type="winv", wait_image_loading_time=3):
    """
    Gửi tin nhắn đến một số cuộc chat bằng cách:
      - Click vào vị trí cố định trong khu vực chat_list để chọn cuộc chat hiện tại.
      - Gửi tin nhắn.
      - Sau đó kéo thanh cuộn một đoạn nhỏ và click tại vị trí đó để chọn cuộc chat tiếp theo.
    """
    print(target_text, 'target_text')
    print("Thời gian chờ load ảnh", wait_image_loading_time)
    zalo_window.set_focus()
    global index_click
    # Lấy tọa độ phần tử "Tất cả"
    try:
        all_element = zalo_window.child_window(title="Ưu tiên", control_type="Text").wrapper_object()
    except:
        all_element = zalo_window.child_window(title="Tất cả", control_type="Text").wrapper_object()

    element_rect = all_element.rectangle()
    click_x = int(element_rect.mid_point().x)
    click_y = int(element_rect.bottom + 35)
    if isinstance(list_messages, list):
        full_message = "\n".join(list_messages)
    else:
        full_message = list_messages.strip()
    if send_type == "winv":
        send_image_to_clipboard(file_path)
    # Copy vào clipboard
    for i in range(num_convos):
        try:
            time.sleep(1)

            # Tính delta_scroll_input chính xác cho từng vòng
            delta_scroll_input = delta_scroll if i == 0 else delta_scroll + (i - 1) * delta_scroll

            print(f"➡️ Vòng lặp {i + 1}: delta_scroll_input = {delta_scroll_input}")

            # Xử lý cuộn và click
            if i > 0:
                scroll_and_click(zalo_window, delta_scroll_input, element_rect, item_spacing, target_text, i)
            else:
                pyautogui.click(click_x, click_y)
            # Gửi tin nhắn nếu is_real
            if is_real:

                # # Gửi file nếu có
                if file_path:
                    send_message(zalo_window, default_delta_y, is_have_image=True,full_message=full_message,send_type=send_type,wait_image_loading_time=wait_image_loading_time)
                    if send_type == "ctrlv":
                        send_image_file(zalo_window, file_path, default_delta_y, wait_image_loading_time)
                else:
                    send_message(zalo_window, default_delta_y, is_have_image=False,full_message=full_message,send_type=send_type,wait_image_loading_time=wait_image_loading_time)
                
                #     print("📁 Gửi file:", file_path)
                #     send_image_file(zalo_window, file_path, default_delta_y)
            else:
                time.sleep(1)  # Chỉ chờ sau khi gửi tin nhắn giả
                pyautogui.scroll(1000)  # Cuộn sau khi gửi tin nhắn giả
            if index_click > 9:
                break
        except Exception as e:
            print(f"❌ Lỗi khi xử lý vòng {i + 1}: {e}")
            continue
        
def send_message_by_list(zalo_window, list_messages, default_delta_y=0):
    for child in zalo_window.descendants():
        if "Nhập @, tin nhắn tới" in child.window_text():
            print("Tìm thấy ô chat!")

            if isinstance(list_messages, list):
                full_message = "\n".join(list_messages)
            else:
                full_message = list_messages.strip()

            # Copy vào clipboard
            pyperclip.copy(full_message)

            # Click vào ô chat
            screen_width, screen_height = pyautogui.size()
            x_ratio = 733 / 1920
            y_ratio = 984 / 1080
            new_x = int(screen_width * x_ratio)
            new_y = int(screen_height * y_ratio - default_delta_y)
            pyautogui.click(new_x, new_y)

            send_keys("^v")
            time.sleep(0.5)  # Chờ thêm cho đến khi ảnh load
            send_keys("{ENTER}")
            time.sleep(0.2)
            break

def crawler_data(zalo_file_path,phone_number, messages,default_delta_y_search=0, image_path_from_client="",wait_image_loading_time=3):
    
    driver = find_to_zalo(0.5, zalo_file_path)

    print(image_path_from_client, "image_path_from_client")
    try:
        print(f"Đang gửi tin nhắn cho {phone_number}...")
        if isinstance(messages, list):
            full_message = "\n".join(messages)
        else:
            full_message = messages.strip()
            
        # Gửi lời mời kết bạn
        is_finded_user = add_friend(driver, phone_number, 0.25, 5, default_delta_y_search)
        # Gửi tin nhắn
        send_message_by_list(driver, full_message,0)
        if image_path_from_client:
            send_image_file(driver, image_path_from_client,0,wait_image_loading_time)

    except Exception as e:
        print(f"Lỗi khi gửi cho {phone_number}: {e}")

