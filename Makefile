scrape:
	export CITY=$(city) && ./scrapy_zap/ && scrapy crawl zap -o data/$(city).csv
