scrape:
	city=$(city) && \
	cond=$(cond) && \
	export COND=$(cond) && \
	export CITY=$(city) && \
	scrapy crawl zap -o data/$(shell echo ${city}-${cond} | cut -d '+' -f 2).csv && python3 ./scripts/clean.py && Rscript scripts/geocode.R
