scrape:
	city=$(city) && \
	export CITY=$(city) && \
	python3 ./scrapy_zap/get_url_with_playwright.py && scrapy crawl zap -o data/$(shell echo ${city} | cut -d '+' -f 2).csv && rm info.csv && python3 ./scripts/clean.py && ./scripts/geocode
