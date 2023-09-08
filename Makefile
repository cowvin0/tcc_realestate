scrape:
	city=$(city)
	export CITY=$(city) && \
	./scrapy_zap/get_url_with_playwright.py && scrapy crawl zap -o data/$(shell echo ${city} | cut -d '+' -f 2).csv && rm info.csv
