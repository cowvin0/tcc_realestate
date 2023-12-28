scrape:
	city=$(city) && \
	cond=$(cond) && \
	export COND=$(cond) && \
	export CITY=$(city) && \
	python3 ./scrapy_zap/get_url_with_playwright.py && scrapy crawl zap -o data/$(shell echo ${city}-${cond} | cut -d '+' -f 2).csv && python3 ./scripts/clean.py && Rscript scripts/geocode.R #&& rm info.csv
