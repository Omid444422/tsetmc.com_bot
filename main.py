from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from json import dumps
from time import sleep
from sys import exit
from glob import glob
from requests import get

BASE_URL = 'https://www.tsetmc.com/'
HISTORY_API_URL = 'https://cdn.tsetmc.com/api/Trade/GetTradeHistory/COMPANY_ID/HISTORY_ID/false'

print('choose mode:')
print('='*100)
print('[0]: exit the program')
print('[1]: information')
print('[2]: start the program')
print('='*100)

user_input = input(': ')

if int(user_input) == 0:
    exit()

elif int(user_input) == 1:
    print('='*50 + 'information' + '='*39)
    print('input most be like this: \n test1,test2,testx')
    print('='*100)

elif int(user_input) == 2:
    print('enter companies name here: ')
    company_names = input(' ')
    print('enter count here: ')
    company_days = int(input(' ')) - 1

    counter = 0

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    if not company_names:
        read_file_name = glob('*.txt')
        if read_file_name:
            txt_file = open(read_file_name[0],'r',encoding='utf-8')
            company_names = ','.join(txt_file.readlines())
        else:
            driver.get(BASE_URL+'Loader.aspx?ParTree=15131F')
            sleep(7)

            companies = driver.find_elements(By.CSS_SELECTOR,'a.inst')

            for single_company in companies:
               try:
                    driver.execute_script("arguments[0].scrollIntoView();", single_company)
                    company_names += single_company.text + ','
               except:
                   print('skip')
                   continue
         
    company_list = company_names.split(',')

    complete_company_data = list()
    company_history_data = {'company_name':None,'data':None,'histroy_date_info':list()}
    
    for index,single_company in enumerate(company_list):
        company_history_data = {'company_name':None,'data':None,'histroy_date_info':list()} 
        
        driver.get(BASE_URL)

        sleep(2)

        search_show_button = driver.find_element(By.CSS_SELECTOR,'a#search')
        search_show_button.click()

        sleep(1)

        search_input = driver.find_element(By.CSS_SELECTOR,'input[name="search"]')
        search_input.send_keys(single_company)

        sleep(2)

        search_list = driver.find_elements(By.CSS_SELECTOR,'body > div:nth-child(8) > div.jss1 > div > div > div.tabcontent.content > div > div > div > div.ag-root-wrapper-body.ag-layout-auto-height.ag-focus-managed > div.ag-root.ag-unselectable.ag-layout-auto-height > div.ag-body-viewport.ag-layout-auto-height.ag-row-no-animation > div.ag-center-cols-clipper > div > div > div')

        search_urls = list()

        for single_search in search_list:
            search_urls.append(single_search.find_element(By.XPATH,'.//div[1]/span/a').get_attribute('href'))
            break # برای انتخاب فقط اولین جستجوی مرتبط

        for single_url in search_urls:
            driver.get(single_url)

            sleep(2)

            single_company_names = driver.find_elements(By.CSS_SELECTOR,'#MainBox > div.header.bigheader span')
            complete_company_name = driver.find_element(By.XPATH,'//*[@id="MainBox"]/div[1]/span[1]').text + driver.find_element(By.XPATH,'//*[@id="MainBox"]/div[1]/span[2]').text


            PE = driver.find_element(By.CSS_SELECTOR,'td#d12').text
            PE_group = driver.find_element(By.CSS_SELECTOR,'#TopBox > div.box2.zi1 > div:nth-child(6) > table > tbody > tr:nth-child(1) > td:nth-child(6)').text

            moon_volume_avg = driver.find_element(By.CSS_SELECTOR,'#TopBox > div.box2.zi1 > div:nth-child(4) > table > tbody > tr:nth-child(4) > td:nth-child(2) > div').get_attribute('title')

            floating_share = driver.find_element(By.CSS_SELECTOR,'#TopBox > div.box2.zi1 > div:nth-child(4) > table > tbody > tr:nth-child(3) > td:nth-child(2)').text

            company_history_data['company_name'] = complete_company_name
            company_history_data['data'] = {'pe':PE,'pe_group':PE_group,'moon_volume_avg':moon_volume_avg,'floating_share':floating_share}

            sleep(3)

            show_history_button = driver.find_element(By.CSS_SELECTOR,'a.torquoise')
            show_history_button.click()

            sleep(3)

            company_histories_url = list()

            while len(company_histories_url) <= int(company_days):

                sleep(2)

                company_histories = driver.find_elements(By.CSS_SELECTOR,'#HistoryContent > div > div.ag-theme-alpine > div > div > div.ag-root-wrapper-body.ag-layout-auto-height.ag-focus-managed > div.ag-root.ag-unselectable.ag-layout-auto-height > div.ag-body-viewport.ag-layout-auto-height.ag-row-no-animation > div.ag-pinned-right-cols-container div[role="row"]')

                for single_history in company_histories:

                    url = single_history.find_element(By.XPATH,'.//div[1]/a').get_attribute('href')
                    company_histories_url.append(url)

                try:
                    next_page_button = driver.find_element(By.CSS_SELECTOR,'#ag-977 > span.ag-paging-page-summary-panel > div:nth-child(4)')
                    next_page_button.click()
                except:
                    pass

                sleep(3)

            for index,history_url in enumerate(company_histories_url):

                if int(company_days) < index:
                    break

                driver.get(history_url)

                sleep(3)

                transactions_count = driver.find_element(By.CSS_SELECTOR,'#MainContent > div:nth-child(1) > div.box2.z2_4.h250 > div.box4.zi1_4.h60 > table > tr:nth-child(1)').text

                transactions_volume = driver.find_element(By.CSS_SELECTOR,'#MainContent > div:nth-child(1) > div.box2.z2_4.h250 > div.box4.zi1_4.h60 > table > tr:nth-child(2)').text

                transactions_value = driver.find_element(By.CSS_SELECTOR,'#MainContent > div:nth-child(1) > div.box2.z2_4.h250 > div.box4.zi1_4.h60 > table > tr:nth-child(3)').text

                yesterday_price = driver.find_element(By.CSS_SELECTOR,'#MainContent > div:nth-child(1) > div.box2.z2_4.h250 > div:nth-child(2) > table > tr:nth-child(3) td:nth-child(2)').text

                first_price = driver.find_element(By.CSS_SELECTOR,'#MainContent > div:nth-child(1) > div.box2.z2_4.h250 > div:nth-child(1) > table > tr:nth-child(3)').text

                last_transactions = driver.find_element(By.CSS_SELECTOR,'#MainContent > div:nth-child(1) > div.box2.z2_4.h250 > div:nth-child(1) > table > tr:nth-child(1)').text

                end_price = driver.find_element(By.CSS_SELECTOR,'#MainContent > div:nth-child(1) > div.box2.z2_4.h250 > div:nth-child(1) > table > tr:nth-child(2)').text

                lowest_price = driver.find_element(By.CSS_SELECTOR,'#MainContent > div:nth-child(1) > div.box2.z2_4.h250 > div:nth-child(2) > table > tr:nth-child(1) td:nth-child(3)').text

                highest_price = driver.find_element(By.CSS_SELECTOR,'#MainContent > div:nth-child(1) > div.box2.z2_4.h250 > div:nth-child(2) > table > tr:nth-child(1) td:nth-child(2)').text

                share_numbers = driver.find_element(By.CSS_SELECTOR,'#MainContent > div:nth-child(1) > div.box2.z2_4.h250 > div.box4.z1_4.h60 > table > tr:nth-child(1) > td:nth-child(2)').get_attribute('title')

                base_valume = driver.find_element(By.CSS_SELECTOR,'#MainContent > div:nth-child(1) > div.box2.z2_4.h250 > div.box4.z1_4.h60 > table > tr:nth-child(2) > td:nth-child(2)').get_attribute('title')

                market_value = driver.find_element(By.CSS_SELECTOR,'#MainContent > div:nth-child(1) > div.box2.z2_4.h250 > div.box4.z1_4.h60 > table > tr:nth-child(3) > td:nth-child(2)').get_attribute('title')

                real_people_count = driver.find_element(By.CSS_SELECTOR,'#clientType > tr:nth-child(2) > td:nth-child(2) span').text

                real_people_volume = driver.find_element(By.CSS_SELECTOR,'#clientType > tr:nth-child(3) td:nth-child(2)').get_attribute('title')

                real_people_buy_avg = driver.find_element(By.CSS_SELECTOR,'#clientType > tr:nth-child(5) td:nth-child(2)').text
                

                # حقوقی

                legal_buy_count = driver.find_element(By.CSS_SELECTOR,'#clientType > tr:nth-child(2) > td:nth-child(3) span').text

                legal_buy_volume = driver.find_element(By.CSS_SELECTOR,'td#ct5').get_attribute('title')

                legal_buy_avg = driver.find_element(By.CSS_SELECTOR,'td#ct17').text

                legal_sell_count = driver.find_element(By.CSS_SELECTOR,'#clientType > tr:nth-child(2) > td:nth-child(4) span').text

                legal_sell_volume = driver.find_element(By.CSS_SELECTOR,'td#ct6').get_attribute('title')

                legal_buy_avg = driver.find_element(By.CSS_SELECTOR,'td#ct17').text

                # حقیقی
                
                real_people_sell_count = driver.find_element(By.CSS_SELECTOR,'#ct2').text

                real_people_sell_volume = driver.find_element(By.CSS_SELECTOR,'#ct6').get_attribute('title')

                real_people_sell_avg = driver.find_element(By.CSS_SELECTOR,'td#ct18').text

                # حقوقی

                leagal_sell_count = driver.find_element(By.CSS_SELECTOR,'span#ct3').text

                legal_sell_volume = driver.find_element(By.CSS_SELECTOR,'td#ct7').get_attribute('title')

                legal_sell_avg = driver.find_element(By.CSS_SELECTOR,'td#ct19').text

                change_owner_from_legal_to_people = driver.find_element(By.CSS_SELECTOR,'td#ct20').text
                
                # تب معاملات

                volume_price_tab_button = driver.find_element(By.CSS_SELECTOR,'#root > div > div:nth-child(3) > div.menuHolder2.zFull > ul > li:nth-child(2) > a')
                volume_price_tab_button.click()

                sleep(2)

                selected_date = driver.find_element(By.XPATH,'//*[@id="MainBox"]/div[1]/span[3]').text
                transactions_list = list()

                company_url_data = driver.current_url.split('/')
                company_id = company_url_data[4]
                company_history_id = company_url_data[5]
                
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                history_response = get(HISTORY_API_URL.replace('COMPANY_ID',company_id).replace('HISTORY_ID',company_history_id),headers=headers).json()


                histories = history_response

                for single_history in histories['tradeHistory']:
                
                    transactions_list.append({'date':selected_date,'transaction_id':single_history['nTran'],'transaction_time':single_history['hEven'],"transaction_volume":single_history['qTitTran'],'transaction_price':single_history['pTran']})

                company_history_data['histroy_date_info'].append({
                    'transactions_count':transactions_count
                    ,'transactions_volume':transactions_volume,
                    'transactions_value':transactions_value,
                    'yesterday_price':yesterday_price,
                    'first_price':first_price,
                    'last_transactions':last_transactions,
                    'end_price':end_price,
                    'lowest_price':lowest_price,
                    'highest_price':highest_price,
                    'share_numbers':share_numbers,
                    'base_valume':base_valume,
                    'market_value':market_value,
                    'real_people_count':real_people_count,
                    'real_people_volume':real_people_volume,
                    'real_people_buy_avg':real_people_buy_avg,
                    'legal_buy_count':legal_buy_count,
                    'legal_buy_volume':legal_buy_volume,
                    'legal_buy_avg':legal_buy_avg,
                    'legal_sell_count':legal_sell_count,
                    'legal_sell_volume':legal_sell_volume,
                    'legal_buy_avg':legal_buy_avg,
                    'real_people_sell_count':real_people_sell_count,
                    'real_people_sell_volume':real_people_sell_volume,
                    'real_people_sell_avg':real_people_sell_avg,
                    'leagal_sell_count':leagal_sell_count,
                    'legal_sell_volume':legal_sell_volume,
                    'legal_sell_avg':legal_sell_avg,
                    'change_owner_from_legal_to_people':change_owner_from_legal_to_people,'transactions_data':transactions_list})

                company_history_json = dumps(company_history_data,ensure_ascii=False)

            json_file = open(str(counter)+'.json','w',encoding='utf-8')
            json_file.write(company_history_json)
            json_file.close()

            counter += 1