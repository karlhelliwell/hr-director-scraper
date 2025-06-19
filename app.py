import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.title("HR Director Job Scraper")

job_title = st.text_input("Job Title", "HR Director")
location = st.text_input("Location (optional)", "")
run_search = st.button("Search Jobs")

@st.cache_data
def scrape_reed(job_title, location):
    search_term = job_title.replace(" ", "-").lower()
    base_url = f"https://www.reed.co.uk/jobs/{search_term}-jobs"
    if location:
        base_url += f"-in-{location.replace(' ', '-').lower()}"

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    jobs = soup.find_all("article", class_="job-result")
    results = []

    for job in jobs:
        try:
            title = job.find("h3").get_text(strip=True)
            company = job.find("a", class_="gtmJobListingPostedBy").get_text(strip=True)
            loc = job.find("li", class_="location").get_text(strip=True)
            link = "https://www.reed.co.uk" + job.find("a")["href"]
            results.append([title, company, loc, link])
        except:
            continue

    return pd.DataFrame(results, columns=["Job Title", "Company", "Location", "Link"])

@st.cache_data
def scrape_jobted(job_title, location):
    search_term = job_title.replace(" ", "+").lower()
    loc_term = location.replace(" ", "+").lower() if location else ""
    base_url = f"https://uk.jobted.com/jobs?q={search_term}&l={loc_term}"

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    job_cards = soup.find_all("div", class_="job")
    results = []

    for job in job_cards:
        try:
            title = job.find("h2").get_text(strip=True)
            company = job.find("span", class_="company").get_text(strip=True)
            loc = job.find("span", class_="location").get_text(strip=True)
            link = job.find("a")["href"]
            results.append([title, company, loc, link])
        except:
            continue

    return pd.DataFrame(results, columns=["Job Title", "Company", "Location", "Link"])

@st.cache_data
def scrape_cvlibrary(job_title, location):
    search_term = job_title.replace(" ", "+").lower()
    loc_term = location.replace(" ", "+").lower() if location else ""
    base_url = f"https://www.cv-library.co.uk/search-jobs?k={search_term}&l={loc_term}"

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    job_cards = soup.find_all("div", class_="job" or "job__body")
    results = []

    for job in job_cards:
        try:
            title = job.find("h2").get_text(strip=True)
            company = job.find("div", class_="job__details__company").get_text(strip=True)
            loc = job.find("div", class_="job__details__location").get_text(strip=True)
            link = "https://www.cv-library.co.uk" + job.find("a")["href"]
            results.append([title, company, loc, link])
        except:
            continue

    return pd.DataFrame(results, columns=["Job Title", "Company", "Location", "Link"])

if run_search:
    st.info("Scraping jobs...")
    df_reed = scrape_reed(job_title, location)
    df_jobted = scrape_jobted(job_title, location)
    df_cv = scrape_cvlibrary(job_title, location)

    combined_df = pd.concat([df_reed, df_jobted, df_cv]).drop_duplicates().reset_index(drop=True)
    st.success(f"Found {len(combined_df)} jobs.")
    st.dataframe(combined_df)

    csv = combined_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "hr_director_jobs.csv", "text/csv")
