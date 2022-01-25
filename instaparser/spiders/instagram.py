import json
import re

import scrapy
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from instaparser.items import InstaparserItem
from copy import deepcopy


class InstaSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login_name = 'testtestovich25'
    inst_login_pwd = '#PWD_INSTAGRAM_BROWSER:10:1643021517:AddQAO94EvnnyyAcucoFqw606CwOtQ1yUOwq72EvB9Mj5IdJZTw+aXlJF3ION35+iuSaJPpTj3jDyFMKXVcn3lBGTTSCM/tuY2C39phgWC5WhKbGhDQKkfU19bIDQqfZm9pyI9gPVZVM5QxNgQ=='
    parse_user_list = ['jenya_asha', 'evgeni_knaub', 'elizshadow', 'sova_brow_al']
    frendships_url = 'https://i.instagram.com/api/v1/friendships'
    posts_hash = '8c2a529969ee035a5063f2fc8602a0fd'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login_name, 'enc_password': self.inst_login_pwd},
            headers={'X-CSRFToken': csrf}
        )

    def login(self, response: HtmlResponse):
        j_body = response.json()
        if j_body.get('authenticated'):
            for user in self.parse_user_list:
                yield response.follow(f'/{user}',
                                      callback=self.user_followers_list_parse,
                                      cb_kwargs={'username': user}
                                      )

    def user_followers_list_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)

        yield response.follow(f'{self.frendships_url}/{user_id}/followers/?count=12&search_surface=follow_list_page',
                              callback=self.user_followers_parse,
                              cb_kwargs={'username': username, 'user_id': user_id},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'})

        yield response.follow(f'{self.frendships_url}/{user_id}/following/?count=12',
                              callback=self.user_following_parse,
                              cb_kwargs={'username': username, 'user_id': user_id},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'})

    def user_followers_parse(self, response: HtmlResponse, username, user_id):

        j_data = response.json()
        if j_data.get('big_list'):
            max_id = j_data.get('next_max_id')
            url_followers = f'{self.frendships_url}/{user_id}/followers/?count=12&max_id={max_id}&search_surface=follow_list_page'
            yield response.follow(url_followers,
                                  callback=self.user_followers_parse,
                                  cb_kwargs={'username': username, 'user_id': deepcopy(user_id)},
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'})
        followers = j_data.get('users')
        for follower in followers:
            item = InstaparserItem(
                user_id=user_id,
                username=username,
                follower_id=follower.get('pk'),
                follower_name=follower.get('full_name'),
                follower_username=follower.get('username'),
                photo=follower.get('profile_pic_url'),

            )
            yield item

    def user_following_parse(self, response: HtmlResponse, username, user_id):

        j_data = response.json()
        if j_data.get('big_list'):
            max_id = j_data.get('next_max_id')
            url_followers = f'{self.frendships_url}/{user_id}/following/?count=12&max_id={max_id}'
            yield response.follow(url_followers,
                                  callback=self.user_following_parse,
                                  cb_kwargs={'username': username, 'user_id': deepcopy(user_id)},
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'})
        followings = j_data.get('users')
        for following in followings:
            item = InstaparserItem(
                user_id=user_id,
                username=username,
                following_id=following.get('pk'),
                following_name=following.get('full_name'),
                following_username=following.get('username'),
                photo=following.get('profile_pic_url'),

            )
            yield item

    def fetch_csrf_token(self, text):
        ''' Get csrf-token for auth '''
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        try:
            matched = re.search(
                '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"', text)[-1].split('"')[-2]
