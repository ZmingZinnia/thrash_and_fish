# -*- coding: utf-8 -*-
import re
import urllib
import requests
import urllib.parse
from typing import List, Optional, Union
from bs4 import BeautifulSoup

from adnmb.model import ThreadModel, CategoryModel, PostModel, InfoLevel, InfoModel


def get_html_soup_by_url(url):
    resp = requests.get(url)
    return BeautifulSoup(resp.text, 'html.parser')


class Adnmb:
    name = 'ADNMB'
    current_category = None
    current_thread = None
    has_next_thread = True
    has_next_post = True
    thread_page = 0
    post_page = 0
    homepage_url = 'https://adnmb3.com/Forum'
    category_prefix_url = 'https://adnmb3.com'
    category_models = []
    thread_models = []

    def get_thread_model_by_soup(self, soup):
        threads_info = soup.find_all('div', {'class': 'h-threads-item-main'})
        attr_map = {
            'id': ('a', {'class': 'h-threads-info-id'}),
            'title': ('span', {'class': 'h-threads-info-title'}),
            'content': ('div', {'class': 'h-threads-content'}),
            'author_id': ('div', {'class': 'h-threads-info-uid'}),
            'author_email': ('span', {'class': 'h-threads-info-email'}),
            'create_time': ('span', {'class': 'h-threads-info-createdat'}),
        }
        models = []
        for thread_info in threads_info:
            content_map = {}
            for k, attr_item in attr_map.items():
                _item = thread_info.find(*attr_item)
                if k == 'id':
                    content = _item.text[3:]
                else:
                    content =  _item.text if _item else ''
                content_map[k] = content
            content_map['url'] = thread_info.find_all('a', {'href': re.compile('^/t/\d*?$')})[0].attrs['href']
            models.append(ThreadModel(**content_map))
        return models

    def get_category_model_by_soup(self, soup):
        models = []
        links = soup.find_all(href=re.compile('/f/.*?'))
        for link_element in links:
            url = link_element.attrs['href']
            content = link_element.text.strip()
            models.append(CategoryModel(content=content, url=url))
        return models

    def get_post_model_by_soup(self, soup):
        models = []
        attr_map = {
            'title': ('span', {'class': 'h-threads-info-title'}),
            'author_email': ('span', {'class': 'h-threads-info-email'}),
            'create_time':  ('span', {'class': 'h-threads-info-createdat'}),
            'author_id': ('span', {'class': 'h-threads-info-uid'}),
            'post_id': ('a', {'class': 'h-threads-info-id'}),
            'content': ('div', {'class': 'h-threads-content'})
        }
        replys = soup.find_all('div', {'class': "h-threads-item-reply"})
        for reply in replys:
            content_map = {}
            for k, attr_item in attr_map.items():
                _item = reply.find(*attr_item)
                text = _item.text.strip()
                if k == 'post_id':
                    content = text[3:] if text else ''
                elif k == 'author_id':
                    content = text[3:] if text else ''
                else:
                    content = text
                content_map[k] = content
            models.append(PostModel(**content_map))
        return models

    def get_categories(self) -> List[CategoryModel]:
        soup = get_html_soup_by_url(self.homepage_url)
        models = self.get_category_model_by_soup(soup)
        self.category_models = models
        return models

    def reset_post_info(self):
        self.has_next_post = True
        self.post_page = 0

    def reset_thread_info(self):
        self.has_next_thread = True
        self.thread_page = 0


    def get_next_page_threads(self) -> Union[List[ThreadModel], InfoModel]:
        if not self.current_category:
            return InfoModel(level=InfoLevel.ERROR, text='please select category first')
        if not self.has_next_thread:
            return InfoModel(level=InfoLevel.ERROR, text="already at the end")
        url = urllib.parse.urljoin(self.category_prefix_url, self.current_category.url)
        self.thread_page += 1
        if self.thread_page:
            url = url + f'?page={self.thread_page}'

        soup = get_html_soup_by_url(url)
        self.thread_models = self.get_thread_model_by_soup(soup)
        if not self.thread_models:
            self.has_next_thread = False
        return self.thread_models


    def get_prev_page_threads(self) -> Union[List[ThreadModel], InfoModel]:
        if not self.current_category:
            return InfoModel(level=InfoLevel.ERROR, text='please select category first')
        url = urllib.parse.urljoin(self.category_prefix_url, self.current_category.url)
        self.thread_page = self.thread_page - 1 if self.thread_page >= 1 else 0
        if self.thread_page:
            url = url + f'?page={self.thread_page}'

        soup = get_html_soup_by_url(self.url)
        self.thread_models = self.get_thread_model_by_soup(soup)
        return self.thread_models

    def change_thread(self, thread_index):
        if not str(thread_index).isdigit() or int(thread_index) >= len(self.thread_models):
            return InfoModel(level=InfoLevel.ERROR, text='invlaid thread index')
        thread_index = int(thread_index)
        self.current_thread = self.thread_models[thread_index]
        self.reset_post_info()
        return InfoModel(level=InfoLevel.INFO, text='thread changed')


    def get_next_post(self):
        if not self.current_thread:
            return InfoModel(level=InfoLevel.ERROR, text="please select thread first")
        if not self.has_next_post:
            return InfoModel(level=InfoLevel.ERROR, text="already at the end")
        self.post_page += 1
        url = f'https://adnmb3.com/t/{self.current_thread.id}/'
        if self.post_page >= 2:
            url = urllib.parse.urljoin(url, f'page/{self.post_page}.html')
        soup = get_html_soup_by_url(url)
        models = self.get_post_model_by_soup(soup)
        if not models:
            self.has_next_post = False
        if self.post_page <= 1:
            models = [self.current_thread.to_post()] + models
        return models

    def get_prev_post(self):
        if not self.current_thread:
            return InfoModel(level=InfoLevel.ERROR, text="please select thread first")
        self.post_page -= 1
        url = f'https://adnmb3.com/t/{self.current_thread.id}/'
        if self.post_page >= 2:
            url = urllib.parse.urljoin(url, f'page/{self.post_page}.html')
        soup = get_html_soup_by_url(url)
        models = self.get_post_model_by_soup(soup)
        if self.post_page <= 1:
            models = [self.current_thread.to_post()] + models
        return models

    def change_category(self, category_index):
        if not str(category_index).isdigit() or int(category_index) >= len(self.category_models):
            return InfoModel(level=InfoLevel.ERROR, text='invlaid category index')
        category_index = int(category_index)
        self.current_category = self.category_models[category_index]
        self.reset_post_info()
        self.reset_thread_info()
        return InfoModel(level=InfoLevel.INFO, text='category changed')
