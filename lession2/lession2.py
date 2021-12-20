from bs4 import BeautifulSoup as BS
import requests
from pprint import pprint
import pandas as pd

# https://chelyabinsk.hh.ru/search/vacancy?area=104&fromSearchLine=true&text=python

main_url = 'https://chelyabinsk.hh.ru/'
search_vacancy = 'python'
page = 0
params = {'area': '104',
              'fromSearchLine': 'true',
              'text': search_vacancy,
              'page': page,
          'items_on_page': '20'}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}

response = requests.get(main_url + 'search/vacancy', params=params, headers=headers)
vacancy_list = []

if response.ok:
    dom = BS(response.text, 'html.parser')

    vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})
    # ищем кнопку "дальше"
    next_bottom = dom.find('a', {'data-qa': 'pager-next'})
    # предыдущий элемент содержит в себе номер последней страницы,
    # извлекаем его, избавляемся от знака "..." и преобразуем к числу
    last_page = int(next_bottom.parent.previousSibling.text.replace('...', ''))
    print(last_page)

for page in range(last_page):
    params = {'area': '104',
              'fromSearchLine': 'true',
              'text': search_vacancy,
              'page': page,
              'items_on_page': '20'}
    response = requests.get(main_url + 'search/vacancy', params=params, headers=headers)

    if response.ok:
        dom = BS(response.text, 'html.parser')

        vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})

        for vacancy in vacancies:
            vacancy_data = {}
            name = vacancy.find('span', {'class': 'resume-search-item__name'}).text
            link = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).get('href')
            if vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}) is not None:
                employer = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).text
            else:
                employer = None

            wage_info = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})

            if wage_info is not None:
                wage_interval = wage_info.text.split()

                if wage_interval[0] == 'от':
                    min_wage = int(wage_interval[1] + wage_interval[2])
                    currency = wage_interval[3]
                    max_wage = None
                elif wage_interval[0] == 'до':
                    max_wage = int(wage_interval[1] + wage_interval[2])
                    currency = wage_interval[3]
                    min_wage = None
                else:
                    min_wage = int(wage_interval[0] + wage_interval[1])
                    max_wage = int(wage_interval[3] + wage_interval[4])
                    currency = wage_interval[5]
            else:
                max_wage = None
                min_wage = None
                currency = None

            vacancy_data['currency'] = currency
            vacancy_data['maximal compensation'] = max_wage
            vacancy_data['minimal compensation'] = min_wage
            vacancy_data['link'] = link
            vacancy_data['employer'] = employer
            vacancy_data['vacancy'] = name
            vacancy_data['source'] = main_url

            vacancy_list.append(vacancy_data)
    page += 1

vacancy_df = pd.DataFrame(vacancy_list, columns=['vacancy', 'employer', 'minimal compensation',
                                                 'maximal compensation', 'link', 'source'])

pprint(vacancy_df)




