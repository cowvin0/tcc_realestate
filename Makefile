scrape:
	export CITY=$(city) && ./scrapy_zap/get_url_with_playwright.py && scrapy crawl zap -o data/{$(city).csv:4} && rm info.csv
