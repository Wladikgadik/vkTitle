
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
vk_session = vk_api.VkApi(token=api_keys.API_VK)
vk = vk_session.get_api()

folder='/home/vladislav/vk/'

def add_corners(im):
    size = (110, 110)
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output

def draw_new_users():
    username = ImageFont.truetype(folder + 'Roboto-MediumItalic.ttf', 20)
    userlist = vk.groups.getMembers(group_id='158516227', sort="time_desc")
    user_name = vk.users.get(user_ids=str(userlist['items'][0]), fields="photo_200")
    count = 1;
    MAX_W, MAX_H = 1590, 400
    im = Image.open(folder + 'vk.png')
    for user in user_name:
        draw = ImageDraw.Draw(im)
        print(((MAX_W - 400) + 100 * count))
        cir=draw.multiline_textsize(user['first_name'] + "\n" + user['last_name'], font=username)
        draw.multiline_text((((MAX_W - 130-cir[0]/2)), MAX_H - 50), user['first_name'] + "\n" + user['last_name'], font=username, fill="#724738", align="center")
        fi = urllib.request.urlopen(user['photo_200']).read()
        image_file = io.BytesIO(fi)
        uimg = add_corners(Image.open(image_file))
        im.paste(uimg, (((MAX_W - 182)), 226), mask=uimg)
        count += 1
        return im

def draw_weather(im):
    weather = ImageFont.truetype(folder + 'Roboto-MediumItalic.ttf', 30)
    weather_lite = ImageFont.truetype(folder + 'Roboto-MediumItalic.ttf', 25)
    owm = pyowm.OWM(API_key=api_keys.API_OWM)
    owm.set_language('ru')
    obs = owm.weather_at_id(548408)
    w=obs.get_weather()
    temp = w.get_temperature('celsius')
    MAX_W, MAX_H = 1590, 400
    draw = ImageDraw.Draw(im)
    draw.multiline_text((((MAX_W - 850)), MAX_H - 200), 'Сейчас в Кирове:',
                        font=weather, fill="#724738", align="left")
    draw.multiline_text((((MAX_W - 825)), MAX_H - 155), w._detailed_status.title() +', '+ str(round(temp["temp"]))+chr(176)+'C',
                        font=weather_lite, fill="#724738", align="left")
    draw.multiline_text((((MAX_W - 800)), MAX_H - 110), 'Ветер '+str(round(w._wind["speed"]))+' м/с',
                        font=weather_lite, fill="#724738", align="left")
    btc_rate = requests.get('https://blockchain.info/ru/ticker').text
    parsed_json = json.loads(btc_rate)
    btc_usd = parsed_json["USD"]["last"]
    draw.multiline_text((((MAX_W - 750)), MAX_H - 40), '1 ВТС = '+str(btc_usd)+' USD',
                        font=weather, fill="#724738", align="left")
    im.save(folder + 'result.png', "PNG")


while(True):

    image = draw_new_users()
    draw_weather(image)
    upload_url=vk.photos.getOwnerCoverPhotoUploadServer(group_id='158516227',crop_x2=1590,crop_y2=400)['upload_url']
    imgs = {'photo': ('photo.png', open(folder+'result.png', 'rb') )}
    response = requests.post(upload_url, files=imgs)
    result = json.loads(response.text)
    try:
        ex=vk.photos.saveOwnerCoverPhoto(hash=result['hash'],photo=result['photo'])
    except vk_api.ApiError as error_msg:
        print(error_msg)
    print("Pause\n")
    time.sleep(60)