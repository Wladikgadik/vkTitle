
import vk_api
import pyowm
import json
from urllib.request import Request, urlopen
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont,ImageOps
import requests
import json
import urllib
import io
import time
import api_keys
import datetime
vk_session = vk_api.VkApi(token=api_keys.API_VK)
vk = vk_session.get_api()

folder='~/vk/'

def add_corners(im, size_sq):
    size = (size_sq, size_sq)
    mask = Image.new('L', (223,223), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + (220,220), fill=255)
    output = ImageOps.fit(im, size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output

def draw_new_users():
    username = ImageFont.truetype(folder + 'IntroCondLightFree2.ttf', 20)
    userlist = vk.groups.getMembers(group_id='158516227', sort="time_desc")
    user_name = vk.users.get(user_ids=str(userlist['items']), fields="photo_200, has_photo")
    count = 1;
    MAX_W, MAX_H = 1590, 400
    im = Image.open(folder + 'Bar_Podpisota.jpg')
    ring = Image.open(folder + 'ring.png')
    user = user_name[0]
    draw = ImageDraw.Draw(im)
    print(((MAX_W - 400) + 100 * count))
    #cir=draw.multiline_textsize(user['first_name'] + "\n" + user['last_name'], font=username)
    #draw.multiline_text((((MAX_W - 130-cir[0]/2)), MAX_H - 50), user['first_name'] + "\n" + user['last_name'], font=username, fill="#724738", align="center")
    fi = urllib.request.urlopen(user['photo_200']).read()
    image_file = io.BytesIO(fi)
    uimg = add_corners(Image.open(image_file), 223)
    uimg.paste(ring, (0, 0), mask=ring)
    #im.paste(uimg, (((MAX_W - 239)), 161), mask=uimg)
    im.paste(uimg, (((MAX_W - 249)), 151), mask=uimg)
    return im
def att_date(ATT_LIST):
    ATT_DATE_DELTA = []
    TODAY_DATA = datetime.date.strftime(datetime.date.today(), '%j')
    for ATT in ATT_LIST:
        ATT_DATE = datetime.date.strftime(datetime.datetime.strptime(ATT, "%d-%m"), '%j')
        date_delta = int(ATT_DATE) - int(TODAY_DATA)
        if date_delta>=0:
            ATT_DATE_DELTA.append(date_delta)
    return ATT_DATE_DELTA[0]

def day_true_write(day):
    if (day%100)//10 == 1:
        word = 'дней'
    elif day%10 == 0 | day % 10 >= 5:
        word = 'дней'
    elif day % 10 == 2 or 3 or 4:
        word = 'дня'
    else:
        word = 'день'

    result = str(day)+' '+word
    return result

def draw_text(im):
    weather = ImageFont.truetype(folder + 'Roboto-Light.ttf', 40)
    #weather_ext_sym = ImageFont.truetype(folder + 'IntroCondensedLight.ttf', 40)
    owm = pyowm.OWM(API_key=api_keys.API_OWM)
    owm.set_language('ru')
    obs = owm.weather_at_id(548408)
    w=obs.get_weather()
    temp = w.get_temperature('celsius')
    MAX_W, MAX_H = 1590, 400
    ATT_LIST = ["12-03","23-04"]

    draw = ImageDraw.Draw(im)
    draw.multiline_text((((MAX_W - 950)), MAX_H - 375),
                        'В РАЙОНЕ\n1 КОРПУСА ВЯТГУ\n' + w._detailed_status.title().upper() + ', ' + str(
                            round(temp["temp"])) + chr(730) + 'C',
                        font=weather, fill="white", align="right")
    draw.multiline_text((((MAX_W - 550)), MAX_H - 375),
                        'АТТЕСТАЦИЯ\nУЖЕ ЧЕРЕЗ\n'+day_true_write(att_date(ATT_LIST)).upper(),
                        font=weather, fill="white", align="left")
    #draw.multiline_text((((MAX_W - 825)), MAX_H - 155), w._detailed_status.title() +', '+ str(round(temp["temp"]))+chr(176)+'C',
    #                    font=weather, fill="white", align="left")
    #draw.multiline_text((((MAX_W - 800)), MAX_H - 110), 'Ветер '+str(round(w._wind["speed"]))+' м/с',
     #                   font=weather_lite, fill="#724738", align="left")
    #btc_rate = requests.get('https://blockchain.info/ru/ticker').text
    #parsed_json = json.loads(btc_rate)
    #btc_usd = parsed_json["USD"]["last"]
    #draw.multiline_text((((MAX_W - 750)), MAX_H - 40), '1 ВТС = '+str(btc_usd)+' USD',
     #                   font=weather, fill="#724738", align="left")
    im.save(folder + 'result.png', "PNG")


while(True):

    image = draw_new_users()
    draw_text(image)
    upload_url=vk.photos.getOwnerCoverPhotoUploadServer(group_id='158516227',crop_x2=1590,crop_y2=400)['upload_url']
    imgs = {'photo': ('photo.png', open(folder+'result.png', 'rb') )}
    response = requests.post(upload_url, files=imgs)
    result = json.loads(response.text)
    try:
        ex=vk.photos.saveOwnerCoverPhoto(hash=result['hash'],photo=result['photo'])
    except vk_api.ApiError as error_msg:
        print(error_msg)
    print("Pause\n")
    time.sleep(50)