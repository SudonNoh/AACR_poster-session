import pandas as pd
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

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

sessionUrl = 'https://aacr22.org/sessions#Filter+by+Day=All'

driver.get(url=sessionUrl)
wait_elem = WebDriverWait(driver, 1000).until(
    ec.presence_of_element_located(
        (By.XPATH, '//*[@id="content"]/div[2]/section/div[2]/div[2]/div[1]/div/div[1]/div/h1/a')
    )
)
print(wait_elem.text)

# page의 수
count = 1
# url의 수
num = 1
# while의  go/stop을 결정
stop = 1
url_list = []
while stop > 0:
    try:
        # url 수집
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        url = soup.select('a.session-tab_sessionTitleLink__12Cl0')

        print("==========================PAGE COUNT: ", count, " ==========================")

        for i in url:
            print(num, ". : ", i['href'])
            url_list.append(i['href'])
            num += 1

        # 2. next 버튼 클릭
        if count == 1:
            btn_xpath = '//*[@id="content"]/div[2]/section/div[2]/div[2]/div[11]/button'
        else:
            btn_xpath = '//*[@id="content"]/div[2]/section/div[2]/div[2]/div[11]/button[2]'

        driver.find_element(By.XPATH, btn_xpath).click()
        count += 1

    except selenium.common.exceptions.NoSuchElementException:
        stop = 0

# 3. 각 url로 접근 후 제목, 연사, 시간 수집
all_content_list = []
url_count = 0
for url in url_list:
    url_count += 1
    enter_url = "https://aacr22.org" + url

    try:
        driver.get(enter_url)
        time.sleep(3)
    except selenium.common.exceptions.WebDriverException:
        time.sleep(3)
        driver.get(enter_url)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    try:
        title = driver.find_element(By.XPATH, '//*[@id="content"]/div/div/div[1]/section[2]/h1').text
    except selenium.common.exceptions.NoSuchElementException:
        driver.implicitly_wait(10)
        driver.get(enter_url)
        time.sleep(5)
        title = driver.find_element(By.XPATH, '//*[@id="content"]/div/div/div[1]/section[2]/h1').text

    date = driver.find_element(By.XPATH, '//*[@id="content"]/div/div/div[1]/section[1]/div/h2').text
    try:
        _speak_information = driver.find_elements(By.CLASS_NAME, "speaker-card_speakerContainer__1l66w")
        for info in _speak_information:
            subtitle = info.find_element(By.CLASS_NAME, "undefined").text
            speaker = info.find_element(By.CLASS_NAME, "speaker-card_speakerName__3RC3X").text
            content_list = [title, date, subtitle, speaker, enter_url]
            print("\n\n")
            print(url_count)
            print("Title  :  ", title)
            print("Date   :  ", date)
            print("Subtitle  :  ", subtitle)
            print("Speaker   :  ", speaker)
            print("URL  :  ", enter_url)
            print("\n\n")
            all_content_list.append(content_list)
    except selenium.common.exceptions.NoSuchElementException:
        content_list = [title, date, "", "", enter_url]
        print("\n\n")
        print(url_count, "  except")
        print("Title  :  ", title)
        print("Date   :  ", date)
        print("Subtitle  :  ", )
        print("Speaker   :  ", )
        print("URL  :  ", enter_url)
        print("\n\n")
        all_content_list.append(content_list)

driver.quit()

print(len(all_content_list))
excel = pd.DataFrame(all_content_list, columns=['Title', 'Date', 'SubTitle', 'Speaker', 'URL'])
excel.to_excel("./AACR_session.xlsx")
