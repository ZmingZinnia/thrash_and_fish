# -*- coding: utf-8 -*-
import requests
import json
import re
import os
from urllib.parse import urlencode, urlunparse, urlparse, parse_qsl
from typing import List, Union
from datetime import datetime

from model import CategoryModel, InfoLevel, InfoModel, ThreadModel, PostModel
import config

COOKIE_FILE = os.path.join(os.path.split(__file__)[0], '_cookie')
TOP_CATEGORIES = config.nga_config.get('top_categories', [])
FAKE_CATEGORIES = config.nga_config.get('fake_categories', [])
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G9650 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.110 Mobile Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-USER-AGENT': 'Nga_Official/90013(samsung SM-G9650;Android 10)',
    'Host': 'ngabbs.com',
    'If-Modified-Since': 'Wed, 25 Aug 2021 07:40:11 GMT',
}
if os.path.exists(COOKIE_FILE):
    with open(COOKIE_FILE) as f:
        cookie = json.load(f)
        HEADERS.update(cookie)

def timestamp_to_datetime(ts):
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def re_sub_add_page_sign(matchobj):
    return matchobj.group(0) + '\n'


def get_all_category_by_map(data_map):
    categirey_model_list = []
    for item in data_map['result']:
        for forums in item['groups']:
            for category in forums['forums']:
                if 'name' in category and 'fid' in category:
                    categirey_model_list.append(CategoryModel(id=category['fid'], name=category['name']))
    # let some category forward
    top_categories = []
    top_ids = []
    for top_name in TOP_CATEGORIES:
        for idx, category_model in enumerate(categirey_model_list):
            if top_name in category_model.name:
                top_ids.append(idx)
    for top_id in top_ids:
        obj = categirey_model_list[top_id]
        top_categories.append(obj)
    for removed_top_id in sorted(top_ids)[::-1]:
        categirey_model_list.pop(removed_top_id)
    fake_categories = [CategoryModel(id=item['fid'], name=item['name']) for item in FAKE_CATEGORIES]
    return top_categories + fake_categories + categirey_model_list


def add_query_string(url, query_data):
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    query.update(query_data)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


class NGA:
    name = 'NGA'
    api_url = 'https://ngabbs.com/app_api.php'
    post_page = 0
    thread_page = 0
    max_post_page = 0
    categories = []
    current_thread = None
    current_category = None
    history_threads = []

    def get_categories(self):
        url = add_query_string(self.api_url, {'__lib': 'home', '__act': 'category'})
        category_data = requests.post(url, headers=HEADERS).json()
        categories = get_all_category_by_map(category_data)[:100]
        self.categories = categories

    def reset_progress_info(self):
        self.post_page = 0
        self.thread_page = 0

    def get_thread_model_by_json(self, json_data):
        thread_models = []
        data_list = json_data['result']['data']
        for data in data_list:
            if self.current_category.name and data.get('forumname') and data['forumname'] != self.current_category.name:
                continue
            if data['tid'] not in self.history_threads:
                thread_models.append(ThreadModel(id=data['tid'], author_id=data['authorid'], author=data['author'],
                                                 create_time=timestamp_to_datetime(data['postdate']),
                                                 content=data['subject'], title=''))
                self.history_threads.append(data['tid'])
        return thread_models

    def change_category(self, category_index):
        if not str(category_index).isdigit() or int(category_index) >= len(self.categories):
            return InfoModel(level=InfoLevel.ERROR, text='invlaid category index')
        category_index = int(category_index)
        self.current_category = self.categories[category_index]
        self.post_page = 0
        self.thread_page = 0
        self.history_threads = []
        return InfoModel(level=InfoLevel.INFO, text='category changed')

    def change_category_by_id(self, category_id):
        self.current_category = CategoryModel(id=category_id, name='')
        self.post_page = 0
        self.thread_page = 0
        self.history_threads = []
        return InfoModel(level=InfoLevel.INFO, text='category changed')


    def change_thread(self, thread_index):
        if not str(thread_index).isdigit() or int(thread_index) >= len(self.thread_models):
            return InfoModel(level=InfoLevel.ERROR, text='invlaid thread index')
        thread_index = int(thread_index)
        self.current_thread = self.thread_models[thread_index]
        self.post_page = 0
        self.thread_page = 0
        return InfoModel(level=InfoLevel.INFO, text='thread changed')

    def change_thread_by_id(self, thread_id):
        self.current_thread = ThreadModel(id=thread_id, author_id=0, author=0, create_time=0, content='', title='')
        self.post_page = 0
        self.thread_page = 0
        return InfoModel(level=InfoLevel.INFO, text='thread changed')


    def get_next_page_threads(self) -> Union[List[ThreadModel], InfoModel]:
        if not self.current_category:
            return InfoModel(level=InfoLevel.ERROR, text='please select category first')

        url = add_query_string(self.api_url, {'__lib': 'subject', '__act': 'list'})
        self.thread_page += 1
        rj = requests.post(url, headers=HEADERS, data={'page': self.thread_page, 'fid': self.current_category.id}).json()
        if rj['code'] != 0:
            return InfoModel(level=InfoLevel.ERROR, text=rj['msg'])

        self.thread_models = self.get_thread_model_by_json(rj)
        return self.thread_models

    def get_real_content(self, content: str):
        return self.optimize_html_display(content.split('[/quote]')[-1])

    def optimize_html_display(self, text: str):
        text.replace('<br/>', '\n')
        return re.sub('https://.*?\.(png|webp|gif|jpg)', re_sub_add_page_sign, text)

    def get_post_model_by_json(self, json_data):
        posts = []
        if not json_data['result']:
            return posts
        for item in json_data['result']:
            posts.append(PostModel(post_id=item['pid'], title=item['subject'], content=self.get_real_content(item['content']),
                                   author_id=item['author']['uid'], author=item['author']['username'],
                                   create_time=timestamp_to_datetime(item['postdatetimestamp'])))
        return posts

    def change_post_page(self, idx):
        if str(idx).isdigit():
            idx = int(idx)
        if not str(idx).isdigit() or (idx > self.max_post_page and idx != 1) or idx < 0:
            return InfoModel(level=InfoLevel.ERROR, text=f"invalid index number: {idx}")

        self.post_page = idx - 1 if idx > 0 else 0

    def get_next_post(self):
        if not self.current_thread:
            return InfoModel(level=InfoLevel.ERROR, text="please select thread first")
        self.post_page += 1
        if self.post_page > self.max_post_page and self.post_page != 1:
            return InfoModel(level=InfoLevel.ERROR, text="no more post")
        url = add_query_string(self.api_url, {'__lib': 'post', '__act': 'list'})
        data = {'page': self.post_page, 'tid': self.current_thread.id}
        r = requests.post(url, headers=HEADERS, data=data)
        try:
            rj = r.json()
        except:
            replaced_content = r.content.strip(b'\n?>')
            rj = json.loads(replaced_content)

        if rj['code'] != 0:
            return InfoModel(level=InfoLevel.ERROR, text=rj['msg'])
        self.max_post_page = rj['totalPage']
        models = self.get_post_model_by_json(rj)
        return models

    def post_content(self, text: str):
        if not self.current_thread:
            return InfoModel(level=InfoLevel.ERROR, text="please select thread first")
        url = add_query_string(self.api_url, {'__lib': 'post', '__act': 'reply'})
        rj = requests.post(url, headers=HEADERS, data={'tid': self.current_thread.id, 'content': text}).json()
        if rj['code'] != 0:
            return InfoModel(level=InfoLevel.ERROR, text=rj['msg'])
