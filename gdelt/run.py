from gdeltdoc import GdeltDoc, Filters
import pandas as pd
pd.set_option('display.width', None)

f = Filters(
    keyword = "Netanyahu",
    start_date = "2023-08-16",
    end_date = "2023-08-17",
    country = "US"
)

gd = GdeltDoc()

# Search for articles matching the filters
articles = gd.article_search(f)

# Get a timeline of the number of articles matching the filters
timeline = gd.timeline_search("timelinevol", f)

print(articles)

for url in articles.url:
    print(url)
    
print(timeline)