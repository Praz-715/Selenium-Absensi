#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import requests
import aiohttp
import asyncio
import random
import base64
import json
import time
import os


# In[2]:


# Setup Chrome options
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")

# Path ke driver Chrome
service = webdriver.ChromeService()
# service = Service("C:\Program Files\Google\Chrome\Application\chrome.exe")  # Ganti dengan path driver

# Inisialisasi WebDriver
driver = webdriver.Chrome(service=service, options=options)


# In[3]:


# Geolocation
def set_geolocation(driver, latitude, longitude):
    params = {"latitude": latitude, "longitude": longitude, "accuracy": 100}
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)

# Login ke situs
def login(driver, username, password):
    driver.get("https://www.vankasystem.net/absensi/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))

    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)

    form = driver.find_element(By.TAG_NAME, "form")
    form.submit()

# Fungsi untuk mengunggah gambar
async def upload_pic(image_name, cookie_string):
    url = "https://www.vankasystem.net/absensi/ajax/selfi"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "images/Fikri", image_name)
    # file_path = os.path.abspath(os.path.join("images", image_name))
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")
    
    headers = {
        "Cookie": cookie_string,  # Jika perlu mengirimkan cookie
    }
    
    # Membuka file secara async untuk membaca sebagai binary
    async with aiohttp.ClientSession() as session:
        with open(file_path, "rb") as f:
            # Menggunakan multipart/form-data untuk file upload
            form_data = aiohttp.FormData()
            form_data.add_field('webcam', f, filename=image_name)
            
            async with session.post(url, headers=headers, data=form_data) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(f"Upload gagal dengan status {response.status}: {await response.text()}")


# # Fungsi absensi
async def absensi(image, cookie_string):
    url = "https://www.vankasystem.net/absensi/ajax/absenajaxnew"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": cookie_string,
    }
    data = {
        "maps_absen": "-6.1749577,106.7874385",
        "base64image": image,
    }
    
    # Membuat session untuk melakukan POST request
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            if response.status == 200:
                # Cek content type dan tangani berdasarkan jenis konten yang diterima
                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return await response.json()  # Parse JSON jika jenis konten adalah JSON
                else:
                    # Cetak respons HTML untuk debugging
                    html = await response.text()
                    print("HTML response:", html)
                    return {"error": "Unexpected content type", "html": html}
            else:
                return {"error": f"Request failed with status: {response.status}"}



# In[4]:


import asyncio  # Tambahkan modul asyncio jika belum

async def main():
    try:
        # Set geolocation
        set_geolocation(driver, -6.1745003, 106.7896633)
        
        # Login
        login(driver, "Fikri", "P@ssw0rd")
        # login(driver, "rinaldo", "12345678")
        
        # Ambil cookies
        cookies = driver.get_cookies()
        cookie_string = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        
        print('cookie_string', cookie_string)

        # Menentukan direktori tempat gambar berada
        script_dir = os.path.dirname(os.path.abspath(__file__))
        direktori_gambar = os.path.join(script_dir, "images/Fikri")
        # direktori_gambar = 'images/Fikri'

        # Membaca semua file di direktori
        semua_file = os.listdir(direktori_gambar)

        # Memilih file yang berextensi .jpg
        mypictures = [file for file in semua_file if file.endswith('.jpg')]

        # Memilih gambar secara acak dari gambar .jpg
        selected_image = random.choice(mypictures)

        # Panggil fungsi async untuk upload gambar
        upload_response = await upload_pic(selected_image, cookie_string)
        print(upload_response)
        
        # Proses absensi
        base64_image = upload_response
        result = await absensi(base64_image, cookie_string)
        print("Result:", result)
        
        # Screenshot (opsional)
        driver.save_screenshot("screenshot.png")

    except Exception as e:
        print("An error occurred:", str(e))

    finally:
        #time.sleep(5)
        driver.quit()

# Jalankan fungsi async
minute = [x for x in range(3, 13)]
chosen_minute = random.choice(minute)
time.sleep(chosen_minute * 60)
asyncio.run(main())

