from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke
from bs4 import BeautifulSoup as BS
import requests
import re
from pprint import pprint


client = MongoClient('localhost', 27017)
db = client['vacancy_hh']
vacancies_col = db.vacancies

#vacancies.create_index([(vacancy)])
# https://chelyabinsk.hh.ru/search/vacancy?area=104&fromSearchLine=true&text=python

main_url = 'https://chelyabinsk.hh.ru'

search_vacancy = 'python'
page = 0
params = {'area': '104',
              'fromSearchLine': 'true',
              'text': search_vacancy,
              'page': page,
          'items_on_page': 20}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}

response = requests.get(main_url + '/search/vacancy', params=params, headers=headers)


while True:
    if response.ok:
        dom = BS(response.text, 'html.parser')

        vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})

        for vacancy in vacancies:
            vacancy_data = {}
            name = vacancy.find('span', {'class': 'resume-search-item__name'}).text
            full_link = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).get('href')
            link = full_link.split('?')[0]
            ids = re.search(r'\d+', link)[0]

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

            vacancy_data['_id'] = ids
            vacancy_data['vacancy'] = name
            vacancy_data['maximal compensation'] = max_wage
            vacancy_data['minimal compensation'] = min_wage
            vacancy_data['currency'] = currency
            vacancy_data['link'] = link
            vacancy_data['employer'] = employer
            vacancy_data['source'] = main_url

            try:
                vacancies_col.insert_one(vacancy_data)
            except dke:
                pass

        if dom.find('a', {'data-qa': 'pager-next'}) is not None:
            next_url = dom.find('a', {'data-qa': 'pager-next'}).get('href')
            response = requests.get(main_url + next_url, headers=headers)

        else:
            break

print(f'Всего вакансий: ', vacancies_col.count_documents({}))
# for doc in vacancies_col.find({}):
#     pprint(doc)

def wage_greater_than():
    basic_wage = int(input('Введите желаемую зарплату: '))
    vacancy_list = []
    for doc in vacancies_col.find({'$or':
                                       [{'minimal compensation': {'$gt': basic_wage}},
                                        {'maximal compensation': {'$gt': basic_wage}}
                                         ]}):
        vacancy_list.append(doc)

    print(f'Количество подходящих вакансий: {len(vacancy_list)}')
    return vacancy_list

pprint(wage_greater_than())













