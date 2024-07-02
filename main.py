import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
job_categories = {
    "PR": ["Head of PR", "PR Manager", "Director of PR"],
    "Paid Media": ["Paid Media Manager", "Media Buyer", "Facebook Ads Manager", "Social Ads Manager"],
    "Email Marketing": ["Retention Marketer", "Head of Email Marketing", "Email Marketing Manager", "Retention Marketing Manager"],
    "Influencer Marketing": ["Influencer Marketing Manager", "Head of Influencer Marketing"],
    "SEO": ["SEO Manager", "Head of SEO", "Senior SEO Manager", "SEO Optimizer"]
}
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Mobile/15E148 Safari/604.1",
]
def scrape_indeed(job_title, num_pages=2):
    jobs = []
    session = requests.Session()

    for page in range(0, num_pages):
        url = f"https://www.indeed.com/jobs?q={job_title.replace(' ', '+')}&l=United+States&fromage=30&start={page * 10}"
        headers = {
            "User-Agent": random.choice(user_agents),
            "Referer": "https://www.google.com/",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        print(f"Fetching URL: {url}")
        try:
            response = session.get(url, headers=headers)
            retries = 3
            while response.status_code != 200 and retries > 0:
                print(f"Failed to fetch {url}: Status code {response.status_code}")
                time.sleep(3)  
                response = session.get(url, headers=headers)
                retries -= 1
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all('div', class_='jobsearch-SerpJobCard')

            if not job_cards:
                print(f"No job cards found for {job_title} on page {page}")
                continue

            for card in job_cards:
                job_title_text = card.find('a', class_='jobtitle').text.strip() if card.find('a', class_='jobtitle') else 'N/A'
                job_url = "https://www.indeed.com" + card.find('a', class_='jobtitle')['href'] if card.find('a', class_='jobtitle') else 'N/A'
                company_name = card.find('span', class_='company').text.strip() if card.find('span', class_='company') else 'N/A'
                company_website = "" 
                contact_name = "" 

                job_info = {
                    "Job Title": job_title_text,
                    "Job Posting URL": job_url,
                    "Company Name": company_name,
                    "Company Website": company_website,
                    "Contact Name": contact_name
                }
                print(f"Scraped job: {job_info}") 
                jobs.append(job_info)
            time.sleep(random.uniform(2, 5))

        except Exception as e:
            print(f"Error while fetching {url}: {e}")
            continue

    return jobs
def collect_jobs(job_titles):
    all_jobs = []
    for title in job_titles:
        jobs = scrape_indeed(title)
        all_jobs.extend(jobs)
        if len(all_jobs) >= 100:
            break
    unique_jobs = {job['Job Posting URL']: job for job in all_jobs}.values()
    return list(unique_jobs)[:100]
data_frames = []
for category, titles in job_categories.items():
    print(f"Scraping {category} jobs...")
    jobs = collect_jobs(titles)
    if not jobs:
        print(f"No jobs found for category: {category}")
    else:
        df = pd.DataFrame(jobs)
        data_frames.append((category, df))
with pd.ExcelWriter('job_postings_without_selenium.xlsx', engine='xlsxwriter') as writer:
    for category, df in data_frames:
        if not df.empty:
            df.to_excel(writer, sheet_name=category, index=False)
for category, df in data_frames:
    if not df.empty:
        df.to_csv(f'job_postings_{category}_without_selenium.csv', index=False)

print("Job scraping completed successfully!")
