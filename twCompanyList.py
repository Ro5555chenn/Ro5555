import requests
import csv

# API URL 與輸出檔案路徑
list_api_url = "https://findit.org.tw/api/getDicTwCompanyList"
detail_api_url = "https://findit.org.tw/api/getTwDicCompanyInfo"
output_file = 'company_data_1234.csv'

# CSV Header
header = ['公司名稱', '公司狀態', '團隊人數', '負責人', '主分類', '網站', '產品/服務簡介', '公司簡介', '創立時間', '總公司地址', '統一編號']

# 寫入 CSV 表頭
with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(header)

# 請求設定
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

# 頁碼控制變數
page_index = 0
total_count = 0  # 總共爬取的資料筆數

while True:
    # 設定請求的參數
    params_list = {
        'strSortColumn': 'strFundDate',
        'strSortDirection': 'descending',
        'intPageIndex': page_index,
        'intCountPerPage': 50  # 每頁最多顯示 50 筆
    }

    # 請求資料
    response = requests.get(list_api_url, params=params_list, headers=headers)

    if response.status_code == 200:
        result = response.json()
        companies = result.get('lstCompany', [])

        # 如果沒有資料則跳出迴圈
        if not companies:
            print(f"已處理完所有頁面。")
            break

        # 取得實際返回的筆數
        per_page_actual = len(companies)

        # 處理每一條公司資料
        for company in companies:
            strId = company.get('strId')
            company_name = company.get('strCompanyName')

            # 獲取詳細資料
            detail_params = {'strId': strId}
            detail_response = requests.get(detail_api_url, params=detail_params, headers=headers)

            if detail_response.status_code == 200:
                details = detail_response.json()

                # 擷取資料
                row = [
                    company_name,  # 公司名稱
                    details.get('strCompanyStatus', ""),  # 公司狀態
                    details.get('strTeamMemberNum', ""),  # 團隊人數
                    details.get('lstStrFounder', ""),  # 負責人
                    details.get('lstStrTag', ""),  # 主分類
                    details.get('strWebsiteUrl', ""),  # 網站
                    details.get('strProductIntro', ""),  # 產品/服務簡介
                    details.get('strCompanyIntro', ""),  # 公司簡介
                    details.get('strFoundedDate', ""),  # 創立時間
                    details.get('strHeadquarterLocation', ""),  # 總公司地址
                    details.get('strCompanyIdNo', "")  # 統一編號
                ]

                # 將資料寫入 CSV
                with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(row)

                # 更新爬取筆數
                total_count += 1

                print(f"成功處理公司：{company_name}")
            else:
                print(f"詳細資料 API 請求失敗，ID: {strId}，狀態碼：{detail_response.status_code}")

        # 如果返回的公司數量少於 50，說明沒有更多頁數，跳出循環
        if per_page_actual < 50:
            break

    else:
        print(f"公司列表 API 請求失敗，頁碼: {page_index}，狀態碼：{response.status_code}")
    
    # 增加頁碼，繼續處理下一頁
    page_index += 1

# 最後輸出總共爬取的資料筆數
print(f"頁面 {page_index} 資料數量 {per_page_actual}，已處理完所有資料。")
print(f"總共爬取了 {total_count} 筆資料。")
