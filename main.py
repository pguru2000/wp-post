import os
import json
from datetime import datetime
import pytz
import mysql.connector
import re
import urllib.parse

import pickle
from phpserialize import *
from io import StringIO
import unicodedata

from tqdm import tqdm

import config

local_tz = pytz.timezone("Europe/Paris")
utc_tz = pytz.timezone("Europe/London")

json_data = config.json_data
_fl_builder_enabled = config._fl_builder_enabled
_fl_builder_data_settings = config._fl_builder_data_settings

post_table = config.post_table
postmeta_table = config.postmeta_table

db_host = 'db_host'
db_user = 'db_user'
db_pwd = 'db_pwd'
db_name = 'db_name'
post_author = 7

replace_keys = [
    "settings",
    "data",
    "nonces",
    "sizes",
    "thumbnail",
    "medium",
    "full",
    "629dd847c77e0",
    "629dd847c77e2",
    "629dd847c77e3",
    "629dd847c77e4",
    "629dd847c77e5",
    "629dd847c77e6",
    "629dd847c77e7",
    "629dd847c77f4",
    "629dd847c77f5",
    "629dd847c77f6",
    "629dd847c77f7",
    "629dd847c77f8",
    "629dd847c77f9",
    "629dd847c77fa",
    "629dd847c77fb",
    "629dd847c77fd",
    "629dd9c977490",
    "629dda4a626c7",
    "629dda4a679e0",
    "629dda4a67a99",
    "629dda4a610c1",
    "62a9bd6cb6a9c",
    "62a9bd6cba884",
    "62a9bd6cba90e",
    "62a9bd8ab33e6",
    "62a9bdc0150c6",
    "62a9bdc015140",
    "62a9bdcca4191",
    "62a9c1c3d08c7",
    '62a9c21e971a3',
    '62a9c21e97212',
    '62a9c21e97213',
    '62a9c25410f8d',
    '62a9c25410ffc',
    '62a9c25410ffd',
    '62a9c74d90289',
    '62a9c7fa71000',
    '62a9c7fa76b03',
    '62a9c93a33683',
    '62a9c93a33728',
    '62a9c93a3372b',
    '62a9c93a3372c',
    '62a9ca32565c5',
    '62a9ca325dd5d',
    '62a9ca325ddf2',
    '62bd72712f85b',
    '62e9411244221',
    '62e941124433f',
    '62e9411244341',
    '62e9411244342',
    'u13i9yr6daxe',
    'yibeaju3c87n',
    'dhy0rbfwqn3u',
    'vya6htdiko05',
    'yc987z4l0xi5',
    'fervjciqtwso',
    'bcho42if0ts8',
    'qi1fpmxlc0rk',
    'yzxb5g9e3u1k',
    'bixv9qhurnjs',
    '7mcqhixtdv5l',
    'scmwi58f9aen',
    'ql0jeibs315h',
    'wmt9h04j7o5l'
]
print(" mysql connecting")
mydb = mysql.connector.connect(
  host=db_host,
  user=db_user,
  password=db_pwd,
  database=db_name,
  tls_versions=['TLSv1.1', 'TLSv1.2']
)


mycursor = mydb.cursor()
print(" mysql connected", mycursor)
# exit()


base_url =  "https://www.blabla.com/"


directory = 'sample-txt'

i = 0

old_ids = []
slug_list = []

for filename in os.listdir(directory):
#for filename in tqdm( os.listdir(directory) ):
    if filename.endswith('.txt'):

        # if filename != "12-tirage42.txt" and filename != "14-tirage16.txt":
        #     continue

        f = os.path.join(directory, filename)
        sfp = open(f, "r", encoding='utf-8')
        # sfp = open(f, encoding='ISO-8859-1')
        origtext = sfp.read()

        origtext = origtext.replace('a href="/', 'a href="')
        origtext = origtext.replace('a href="', "a href='" + base_url).replace('">', "'>")
        origtext = origtext.replace('<strong>"', '<strong>').replace('"</strong>', '</strong>')

        origtext = origtext.replace('"', '')

        meta_title = meta_desc = ''
        image1_url = image2_url = ''
        image1_alt = image2_alt = ''
        image1_filename = image2_filename = ''
        
        h1_title = ''
        section1_title = section1_content = ''
        section2_title = section2_content = ''
        section3_title = section3_content = ''
        section4_title = section4_content = ''
        section5_title = section5_content = ''
        conclusion_title = conclusion_content = ''

        image_list = []
        image_alt_list = []
        section_list = []
        

        items = re.findall('#start-[^*]*?#end-', origtext)

        for item in items:
            para_id = item.split('#')[1].replace('start-', '')
            para_content = item.split('#start-' + para_id + '#')[1].replace('#end-', '').strip()
            if para_content.strip() == '':
                continue;

            if para_id == 'meta_title':
                meta_title = para_content

            elif para_id == 'meta_description':
                meta_desc = para_content

            elif para_id in ['image1', 'image2', 'image3', 'image4', 'image5']:                
                image1_url = para_content.strip().split('\n')[0].strip()
                image_list.append(image1_url)
                image1_filename = image1_url.split('/')[-1]

            elif para_id in ['alt-image1', 'alt-image2', 'alt-image3', 'alt-image4', 'alt-image5']:                
                image1_alt = para_content.strip().split('\n')[0].strip()
                image_alt_list.append(image1_alt)            

            elif para_id == 'url':
                slug = para_content.strip().replace('/', '').strip()
                slug = slug.replace(" ", "-")

            elif para_id == 'h1':
                h1_title = para_content

            elif para_id in ['section1', 'section2', 'section3', 'section4', 'section5', 'conclusion']:
                section_title = section_content = ''
                titles = re.findall('<title>[^*]*?</title>', para_content)
                if len(titles) == 1:
                    section_title = titles[0].replace('<title>', '').replace('</title>', '')
                    section_content = para_content.replace(titles[0], '').strip()
                    section_content = section_content.replace('\n', '</p><p>')
                    section_content = '<p>' + section_content + '</p>'
                    if para_id != 'conclusion':
                        section_list.append({
                            'title': section_title,
                            'section_content': section_content
                            })
                else:
                    section_content = para_content.strip().replace('\n', '</p><p>')
                    if section_content != "":
                        section_content = '<p>' + section_content + '</p>'

                        if para_id != 'conclusion':
                            section_list.append({
                                'title': '',
                                'section_content': section_content
                                })

                if para_id == 'conclusion':
                    conclusion_title = section_title
                    conclusion_content = section_content
        try:
            slug = unicode(slug, 'utf-8')
        except (TypeError, NameError): # unicode is a default on python 3 
            pass
        slug = unicodedata.normalize('NFD', slug)
        slug = slug.encode('ascii', 'ignore')
        slug = slug.decode("utf-8")
        slug = str(slug)

        

        # if slug not in slug_list:
        #     print(base_url + slug)
        #     slug_list.append(slug)
            

        if len(section_list) > 1:
            # image1_url = image_list[0]
            image1_url = "https://piscine-64.fr/wp-content/uploads/sites/4/2022/08/ppb02.jpg"
            image1_filename = image1_url.split('/')[-1]
            # image2_url = image_list[1]
            image2_url = "https://piscine-64.fr/wp-content/uploads/sites/4/2022/08/ppb01.jpg"
            image2_filename = image2_url.split('/')[-1]

            image1_alt = '' #image_alt_list[0]
            image2_alt = '' #image_alt_list[1]
            
            section1_title = section_list[0]["title"]
            section2_title = section_list[1]["title"]

            section1_content = section_list[0]["section_content"]
            section2_content = section_list[1]["section_content"]            

            if slug != '' and meta_title != '' and  meta_desc != '' and   conclusion_content != '' and h1_title != '':
                # print('slug', slug)
                # print('meta_title', meta_title)
                # print('meta_desc', meta_desc)
                # print('conclusion_content', conclusion_content)
                # print('image1_url', image1_url)
                # print('image2_url', image2_url)
                # print('image1_alt', image1_alt)
                # print('image2_alt', image2_alt)
                # print('section1_title', section1_title)
                # print('section2_title', section2_title)
                # print('section1_content', section1_content)
                # print('section2_content', section2_content)
                _json_data = json_data
                _json_data = _json_data.replace("$h1_title", h1_title)
                _json_data = _json_data.replace("$h2_section1", section1_title)
                _json_data = _json_data.replace("$h2_section2", section2_title)
                
                _json_data = _json_data.replace("$h2_conclusion", conclusion_title)

                _json_data = _json_data.replace("$section1", section1_content)
                _json_data = _json_data.replace("$section2", section2_content)
                
                _json_data = _json_data.replace("$conclusion", conclusion_content)

                _json_data = _json_data.replace("$img_section1_url", image1_url)
                _json_data = _json_data.replace("$img_section2_url", image2_url)

                _json_data = _json_data.replace("$img_section1_filename", image1_filename)
                _json_data = _json_data.replace("$img_section2_filename", image2_filename)

                _json_data = _json_data.replace("$img_section1_title", image1_alt)
                _json_data = _json_data.replace("$img_section2_title", image2_alt)
                _json_data = _json_data.replace("$img_section1_alt", image1_alt)
                _json_data = _json_data.replace("$img_section2_alt", image2_alt)

                _json_data = _json_data.replace("<h2", "<h2 style='color: gray; text-align: center;' ")

                if 'une piscinier' not in _json_data and 'impérativerment' not in _json_data:
                    continue
                else:
                    _json_data = _json_data.replace("une piscinier", "un piscinier")
                    _json_data = _json_data.replace("impérativerment", "impérativement")
                # if section1_title == "":
                #     _json_data = _json_data.replace("$title_margin_top_section1", "0")
                #     _json_data = _json_data.replace("$title_margin_bottom_section1", "0")
                # else:
                #     _json_data = _json_data.replace("$title_margin_top_section1", "20")
                #     _json_data = _json_data.replace("$title_margin_bottom_section1", "20")

                # if section3_title == "":
                #     _json_data = _json_data.replace("$title_margin_top_section3", "0")
                #     _json_data = _json_data.replace("$title_margin_bottom_section3", "0")
                # else:
                #     _json_data = _json_data.replace("$title_margin_top_section1", "20")
                #     _json_data = _json_data.replace("$title_margin_bottom_section1", "20")

                # if section2_title == "":
                #     _json_data = _json_data.replace("$content_margin_bottom_section1", "0")
                #     _json_data = _json_data.replace("$title_margin_top_section2", "0")
                #     _json_data = _json_data.replace("$title_margin_bottom_section2", "0")
                #     _json_data = _json_data.replace("$content_margin_top_section2", "0")
                # else:
                #     _json_data = _json_data.replace("$content_margin_bottom_section1", "20")
                #     _json_data = _json_data.replace("$title_margin_top_section2", "20")
                #     _json_data = _json_data.replace("$title_margin_bottom_section2", "20")
                #     _json_data = _json_data.replace("$content_margin_top_section2", "20")
                # if section4_title == "":
                #     _json_data = _json_data.replace("$content_margin_bottom_section3", "0")
                #     _json_data = _json_data.replace("$title_margin_top_section4", "0")
                #     _json_data = _json_data.replace("$title_margin_bottom_section4", "0")
                #     _json_data = _json_data.replace("$content_margin_top_section4", "0")
                # else:
                #     _json_data = _json_data.replace("$content_margin_bottom_section3", "20")
                #     _json_data = _json_data.replace("$title_margin_top_section4", "20")
                #     _json_data = _json_data.replace("$title_margin_bottom_section4", "20")
                #     _json_data = _json_data.replace("$content_margin_top_section4", "20")
                # print(_json_data)
                # exit()
                try:
                    _json_data = json.loads(_json_data)                
                except:
                    print('=======================    error   =======================', filename)
                    print(_json_data)
                    exit()
                    continue

                serialize_str = dumps(_json_data)
                serialize_str = serialize_str.decode("utf-8")
                for replace_key in replace_keys:
                    old_str = '"' + replace_key + '"' + ';a:'
                    new_str = '"' + replace_key + '"' + ';O:8:"stdClass":'
                    serialize_str = serialize_str.replace(old_str, new_str)

                local_cur_time = datetime.now(local_tz)
                utc_cur_time = datetime.now(utc_tz)

                post_title = meta_title
                post_status = 'publish'
                comment_status = 'closed'
                ping_status = 'closed'
                post_name = slug
                post_parent = 0
                post_type = 'page'
                
                mycursor.execute(
                    f"SELECT ID, post_name FROM {post_table} WHERE post_name = '{post_name}'"
                )
                query_result = mycursor.fetchone()
               
                # gets the number of rows affected by the command executed
                row_count = mycursor.rowcount           

                if row_count > 0:
                    dupId = query_result[0]
                    sql = f"DELETE FROM {post_table} WHERE ID = {dupId}"
                    mycursor.execute(sql)
                    mydb.commit()

                    sql = f"DELETE FROM {postmeta_table} WHERE post_id = {dupId}"
                    mycursor.execute(sql)
                    mydb.commit()  

                sql = f"INSERT INTO {post_table} (post_author, post_date, post_date_gmt, post_title, post_status, comment_status, ping_status, post_name, post_parent, post_type, post_content, post_excerpt, to_ping, pinged, post_content_filtered) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (post_author, local_cur_time, utc_cur_time, post_title, post_status, comment_status, ping_status, post_name, post_parent, post_type, '', '', '', '', '')
                mycursor.execute(sql, val)
                mydb.commit()

                post_id = mycursor.lastrowid

                sql = f"INSERT INTO {postmeta_table} (post_id, meta_key, meta_value) VALUES (%s, %s, %s)"
                val = [
                    (post_id, '_fl_builder_data', serialize_str),
                    (post_id, '_fl_builder_data_settings', _fl_builder_data_settings),
                    (post_id, '_fl_builder_enabled', _fl_builder_enabled),
                    (post_id, '_yoast_wpseo_title', meta_title),
                    (post_id, '_yoast_wpseo_metadesc', meta_desc),
                ]
                print(base_url + slug)

                mycursor.executemany(sql, val)
                mydb.commit()                
                    
                # else:
                #     old_ids.append(filename)

                #     print('=======================    already in db   =======================', filename)

            
            # i += 1
            # print("=======>", i)
            # if i == 2:
            #     break

print(old_ids)
