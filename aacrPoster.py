import pandas as pd
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup

# chrome driver 설정
chrome_service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('window-size=1920,1080')
driver = webdriver.Chrome(service=chrome_service, options=options)
driver.implicitly_wait(5)

# 로그인
print("\n\n로그인\n\n")
driver.get(url='https://aacr22.org/login')

elem = driver.find_element(By.ID, "last-name-/-family-name")
elem.send_keys('id')
elem = driver.find_element(By.ID, "7-digit-confirmation-number")
elem.send_keys('pw')
elem.send_keys(Keys.ENTER)

# 사이트 접속
poster_url = 'https://cattendee.abstractsonline.com/meeting/10517/search?' \
             'query=%40AllPosters%7EYes&type=presentation&view=appendToCards&' \
             'initialSearchId=70400&searchId=70400'

# xpath_list = []
# 각 topic에 대한 xpath
# for i in range(14):
#     xpath_list.append('//*[@id="content"]/div/div[2]/div/ul/li[3]/ul/li[' + str(i + 1) + ']/a')
xpath_list = [
    '//*[@id="content"]/div/div[2]/div/ul/li[3]/ul/li[9]/a',
    '//*[@id="content"]/div/div[2]/div/ul/li[3]/ul/li[10]/a',
    '//*[@id="content"]/div/div[2]/div/ul/li[3]/ul/li[11]/a',
    '//*[@id="content"]/div/div[2]/div/ul/li[3]/ul/li[12]/a',
    '//*[@id="content"]/div/div[2]/div/ul/li[3]/ul/li[13]/a',
    '//*[@id="content"]/div/div[2]/div/ul/li[3]/ul/li[14]/a',
]


all_obj = []
count = 0
for xpath in xpath_list:
    driver.get(url=poster_url)
    time.sleep(5)

    obj_ = []

    _topic = driver.find_element(By.XPATH, xpath).text.split('\n')
    print('_topic :', _topic)
    # topic 내의 수
    each_topic_len = int(_topic[1])
    # topic
    topic = (_topic[0])
    # topic 으로 접속
    driver.find_element(By.XPATH, xpath).click()
    print('\n\n\n****************topic  :  ', topic, '**********************\n\n\n')

    html_url = []
    title = []
    while len(html_url) < each_topic_len:
        print('topic 수: ', each_topic_len)
        print('url 저장 수: ',len(html_url))
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        elem = driver.find_element(By.CLASS_NAME, "action__link")
        elem.send_keys(Keys.PAGE_DOWN)
        html_url = soup.select("a.action__link")
        titles = soup.select("div.gallery-item>h2>span")

    for (url, title) in zip(html_url, titles):
        count += 1
        obj_ = []
        full_url = 'https://cattendee.abstractsonline.com' + url['href']
        driver.get(full_url)
        driver.implicitly_wait(10)
        time.sleep(1)
        try:
            elem = driver.find_element(By.CLASS_NAME, "cattendee-view-abstract").click()
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            html_abstracts = soup.select("p.popper-text")

            abstract = ""
            for i in html_abstracts:
                abstract += (i.text + " ")

            print('\n')
            print("count : ", count)
            print("topic : ", topic)
            print("full_url : ", full_url)
            print("title : ", title.text)
            print("abstract : ", abstract)
            print('\n')

            obj_.append(topic)
            obj_.append(full_url)
            obj_.append(title.text)
            obj_.append(abstract)

        except selenium.common.exceptions.NoSuchElementException:

            print('\n')
            print("topic : ", topic)
            print("full_url : ", full_url)
            print("title : ", title.text)
            print('\n')

            obj_.append(topic)
            obj_.append(full_url)
            obj_.append(title.text)

        all_obj.append(obj_)

    excel = pd.DataFrame(all_obj, columns=['TOPIC', 'URL', 'TITLE', 'ABSTRACT'])
    excel.to_excel("./AACR_posters2_" + str(each_topic_len) + ".xlsx")

driver.quit()

excel = pd.DataFrame(all_obj, columns=['TOPIC', 'URL', 'TITLE', 'ABSTRACT'])
excel.to_excel("./AACR_posters.xlsx")
