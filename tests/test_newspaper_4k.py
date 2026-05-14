import newspaper


url = 'https://cafef.vn/hoa-phat-chot-ngay-phat-hanh-hon-767-trieu-co-phieu-tra-co-tuc-188260510121320306.chn?utm_source=du-lieu'
url = 'https://vneconomy.vn/vi-pham-5-loi-chung-khoan-bms-bi-phat-toi-780-trieu-dong.htm'
url = 'https://cafef.vn/thi-truong-chung-khoan.chn'
article = newspaper.article(url)

print(article.authors)
print(article.publish_date)
print(article.text)

article.nlp()
print(" ")
print(article.summary)
