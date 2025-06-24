from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os

# Path ke ChromeDriver
PATH = r"C:\Program Files (x86)\chromedriver.exe"
service = Service(PATH)

# Setup WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=service, options=options)

# URL tseries dan MrBeast di socialcounts.org
url_tseries = "https://socialcounts.org/youtube-live-subscriber-count/UCq-Fj5jknLsUf-MWSy4_brA"
url_mrbeast = "https://socialcounts.org/youtube-live-subscriber-count/UCX6OQ3DkcsbYNE6H8uQQuVA"

# Path CSV
csv_file = r"C:\Users\naufa\Downloads\BIGDATA2.csv"

# Fungsi ambil angka dari odometer dengan pengecekan hingga angka valid
def get_odometer_number(container, timeout=10):
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            inside = container.find_element(By.CLASS_NAME, "odometer-inside")
            digits = inside.find_elements(By.CLASS_NAME, "odometer-value")
            number = ''.join([digit.text for digit in digits])
            if number.isdigit():  # Cek valid
                return number
        except:
            pass
        time.sleep(0.5)  # Tunggu sebelum coba lagi
    return "Tidak ditemukan"

# Fungsi ambil data dari halaman socialcounts
def get_data_from_url(url):
    driver.get(url)
    time.sleep(10)  # Tunggu halaman dan animasi selesai

    # Ambil subscriber count
    try:
        subs_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "mainOdometer"))
        )
        subs_count = get_odometer_number(subs_element)
    except:
        subs_count = "Tidak ditemukan"

    # Ambil total views dan videos
    try:
        odometers = driver.find_elements(By.CLASS_NAME, "odometer-auto-theme")
        total_views = get_odometer_number(odometers[1]) if len(odometers) > 1 else "Tidak ditemukan"
        total_videos = get_odometer_number(odometers[2]) if len(odometers) > 2 else "Tidak ditemukan"
    except Exception as e:
        print("Gagal ambil views/videos:", e)
        total_views = "Tidak ditemukan"
        total_videos = "Tidak ditemukan"

    # Format angka
    subs_count = "{:,}".format(int(subs_count)) if subs_count != "Tidak ditemukan" else subs_count
    total_views = "{:,}".format(int(total_views)) if total_views != "Tidak ditemukan" else total_views
    total_videos = "{:,}".format(int(total_videos)) if total_videos != "Tidak ditemukan" else total_videos

    return subs_count, total_views, total_videos

# Ambil data tseries
subs_tseries, views_tseries, videos_tseries = get_data_from_url(url_tseries)

# Ambil data MrBeast
subs_mrbeast, views_mrbeast, videos_mrbeast = get_data_from_url(url_mrbeast)

# Tutup driver
driver.quit()

# Simpan ke CSV
timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
data = [
    [timestamp, "tseries", subs_tseries, views_tseries, videos_tseries],
    [timestamp, "MrBeast", subs_mrbeast, views_mrbeast, videos_mrbeast]
]
df = pd.DataFrame(data, columns=["Timestamp", "Channel", "Subscribers", "Total Views", "Total Videos"])
df.to_csv(csv_file, mode='a', sep=';', index=False, header=not os.path.exists(csv_file), encoding="utf-8-sig")

# Print ke layar
print(f"Data berhasil disimpan:\nTimestamp     : {timestamp}\ntseries:\n  Subscribers   : {subs_tseries}\n  Total Views   : {views_tseries}\n  Total Videos  : {videos_tseries}")
print(f"MrBeast:\n  Subscribers   : {subs_mrbeast}\n  Total Views   : {views_mrbeast}\n  Total Videos  : {videos_mrbeast}")
