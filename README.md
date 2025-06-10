# Vertretungsplan

Live instance: [vertretung.bababue.com](https://vertretung.bababue.com)

## Usage
### Scraping
1. Set up "DATABASE_URL" enviroment variable with Postgres Connection String
2. Run main.py with the date range which should be scraped

```python
python main.py 0 5 #This will scrape dates starting today, 5 days into the future
python main.py -5 3 #This will scrape dates starting 5 days ago, up until in 3 days
```

### Server
1. Set up "DATABASE_URL" enviroment variable with Postgres Connection String
2. Start flask app in a production enviroment like gunicorn

## Docker Setup
1. Clone the repository
2. Run `docker-compose up -d` to create containers
3. To fetch new data, simply rerun the cmd container
