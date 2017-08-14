from bs4 import BeautifulSoup
import scrapy
import json
import re

from scrapy.http import Request
from scrapy import FormRequest
from scrapy.selector import HtmlXPathSelector, Selector

from scraper.items import Course

import os
main_url = "https://edukacja.pwr.wroc.pl"
edu_url = "https://edukacja.pwr.wroc.pl/EdukacjaWeb/studia.do"
edu_pwd = os.environ['EDU_PASSWORD']
actual_year = '2016/2017'


class LoginSpider(scrapy.Spider):
    name = 'educwel.com'
    start_urls = [edu_url]

    def parse(self, response):
        """
        This is first step to access edukacja.cl, send login form

        """
        return FormRequest.from_response(
            response,
            formdata={'login': 'pwr230569', 'password': edu_pwd},
            callback=self.after_login
        )

    def after_login(self, response):
        """Check response and find link to right page"""

        if "Niepowodzenie logowania." in str(response.body):
            print('^^^^^^^^^^^^^^^^^^^^^^')
            print('Nie zalogowany')
        elif 'Nie przepadasz za chodzeniem do dziekanatu' in str(response.body):
            print('^^^^^^^^^^^^^^^^^^^^^^')
            print('zalogowany!')
            links = Selector(response=response).xpath('//a/@href').extract()

            for link in links:
                if 'zapisy' in str(link):
                    url = main_url + link
                    yield Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        """
        This function should find actual semestral year.
        :return:
        """
        if 'Rok</br>akademicki' in str(response.body):
            print('2016/2017')

            soup = BeautifulSoup(response.body)

            for link in soup.find_all('a'):
                if 'SluchaczSemestry' and actual_year in str(link):
                    url = main_url + str(link.get('href'))
                    yield Request(url=url, callback=self.parse_year)

    def parse_year(self, response):
        """
        This function is looking fot right table and finding data
        for form action.
        :param response:
        :return:
        """
        year_soup = BeautifulSoup(response.body)
        data = {}
        for year_link in year_soup.find_all('a'):
            if 'W04_ST_letni_2016/2017' in str(year_link):
                url = main_url + str(year_link.get('href'))
                row = year_link.parent \
                    .parent \
                    .parent \
                    .parent \
                    .parent

                forms = row.find_all('form')
                for form in forms:
                    if "Przeglądanie grup" in str(form):
                        inputs = form.find_all('input')
                        for input in inputs:
                            data[input.get('name')] = input.get('value')

            yield FormRequest(
                url='https://edukacja.pwr.wroc.pl/EdukacjaWeb/zapisy.do',
                formdata=data,
                callback=self.set_criterion
            )

    def set_criterion(self, response):
        """
        This function is setting criterion in form.
        Default is 'Z_PLANU', 'Z_WEKTORA_ZAP' - doesn't return all values for now
        :return:
        """
        data = {}
        soup = BeautifulSoup(response.body)

        try:
            inputs = soup.find('form', id='ZapisyFormFiltr').find_all('input')#.get('action')
        except:
            pass
        else:
            for input in inputs:
                try:
                    name = input.get('name')
                    if name is not None:
                        value = input.get('value')

                        if value is None:
                            value = ''
                        data[name] = value
                except:
                    pass
            data['KryteriumFiltrowania'] ='Z_PLANU' # 'Z_WEKTORA_ZAP'#
            data['NrSemestru'] = '4'
            data['kfkPkSymbol'] = 'PO-W04-TIN- - -ST-Ii-WRO- - - - - -PWR1-DWU'
            data['kfkPkSymbol'] = '1641'
            data['kfkPkId'] ='1641'
            data['kfkPkSymbol_cl_edu_web_lov_handlerClass'] = 'cl.edu.web.common.lov.handlers.PrzedmiotyKsztalceniaLovHandler'
            data['kfkPkSymbol_cl_edu_web_lov_callback'] = '/zapisy.do?event=forwardZapisy'
            data['kfkPkSymbol_cl_edu_web_lov_callback_href'] = 'hrefKryteriumFiltrowania'
            print(data)
            yield FormRequest(
               url='https://edukacja.pwr.wroc.pl/EdukacjaWeb/zapisy.do?event=ZapiszFiltr&event=wyborKryterium&href=#hrefKryteriumFiltrowania',
               formdata=data,
               callback=self.get_next_page
            )

    def get_next_page(self, response):
    #    self.get_courses(response)

        soup = BeautifulSoup(response.body)
       # print(soup.prettify())
        soup = soup.find_all('span')#, class_='paging-numeric-span')
        print(soup)
        for page in soup:
            print(page)

            for input_ in page.find_all('input'):
                if "pagingRangeStartGrupyZajecioweKursu" in input_.get('onclick'):
                    print(input_.get('onclick'))
                    print(input_.get('value'))


    def get_courses(self, response):
        self.get_next_page(response)
        soup = BeautifulSoup(response.body)
        [s.extract() for s in soup('form')]
        [s.extract() for s in soup('input')]
        class_group = soup.find_all('a')

        for link in class_group:
            if "hrefGrupyZajecioweKursuTabela" in str(link.get('name')):
                if str(link.get('name')) != "hrefGrupyZajecioweKursuTabela":

                    first_row = link.find_parent('tr')
                    second_row = first_row.find_next_sibling('tr')
                    third_row = second_row.find_next_sibling('tr')

                    first_row = [f.get_text().strip() for f in first_row.find_all('td')]
                    second_row = [f.get_text().strip()  for f in second_row.find_all('td')]
                    third_row = [f.get_text().strip()  for f in third_row.find_all('td')]
                    third_row = third_row[0].split(',')# ' '.join(r for r in third_row[0])
                    teacher = "".join(second_row[0].split())
                    teacher = re.sub(r"(\w)([A-Z])", r"\1 \2", teacher)
                    teacher = (teacher.split('.'))[1]
                    course = Course(groupCode=first_row[0],
                                    courseCode=first_row[1],
                                    courseName=first_row[2],
                                    seatsAmount=first_row[3],
                                    teacher=teacher,
                                    courseType=second_row[1],
                                    date=third_row[0],
                                    building=third_row[1],
                                    room=third_row[2]
                                    )
                    yield course

spider = LoginSpider

