from celery import shared_task
import pandas as pd
import openai
import requests
from django.core.files.storage import default_storage
from .models import APIConfig
from django.conf import settings
from .models import OpenAI_APIKeyConfig, SiteRecordContentGen
import os
from django.core.exceptions import ObjectDoesNotExist
from openpyxl.utils.exceptions import InvalidFileException
import logging
from celery.utils.log import get_task_logger
from urllib.parse import urlparse
from celery.exceptions import Ignore
import time

def get_openai_api_key():
    try:
        # Try to get the API key from the database
        api_config_api = OpenAI_APIKeyConfig.objects.first()
        if api_config_api and api_config_api.api_key:
            return api_config_api.api_key
        else:
            raise ValueError("No OpenAI API key found in the database")
    except Exception as e:
        # Log the exception (optional)
        print(f"Database error: {e}")
        raise e  # Reraise the exception instead of returning a hardcoded key

# Set the OpenAI API key
openai.api_key = get_openai_api_key()

def get_root_domain(url):
    """Extract the root domain from a given URL."""
    parsed_url = urlparse(url)
    return parsed_url.netloc

def get_unique_filename(original_filename, output_dir):
    """
    Generate a unique filename by appending _1, _2, etc., if a file with the same name exists.
    """
    base_name, ext = os.path.splitext(original_filename)
    counter = 1
    new_filename = original_filename

    while os.path.exists(os.path.join(output_dir, new_filename)):
        new_filename = f"{base_name}_{counter}{ext}"
        counter += 1

    return new_filename



# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_xls_file_incrementally(self, file_path, num_sites, avoid_root_domain, original_filename):
    logger.info(f"Starting task with avoid_root_domain: {avoid_root_domain}")
    logger.info(f"Starting task process_xls_file_incrementally with file_path: {file_path}, num_sites: {num_sites}")

    output_file_path = None  # Initialize output_file_path

    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Validate the file extension
        valid_extensions = ['.xlsx', '.xlsm', '.xltx', '.xltm']
        if not any(file_path.endswith(ext) for ext in valid_extensions):
            raise ValueError(f"Invalid file format: {file_path}. Supported formats are: {valid_extensions}")

        posted_urls = []
        successful_postings = 0

        # Load the Excel file into a DataFrame
        logger.info(f"Loading Excel file: {file_path}")
        df = pd.read_excel(file_path, header=None, engine='openpyxl')
        logger.info("Excel file loaded successfully.")

        # Set the first column as the index and extract required columns
        df.set_index(0, inplace=True)
        second_column_data = df[1]
        column_c_data = df[2].dropna().tolist()

        # Fetch enabled API config sites
        api_config_sites = APIConfig.objects.filter(site_enable=True).order_by('?')
        logger.info(f"Found {len(api_config_sites)} enabled API config sites.")

        total_sites_processed = len(api_config_sites)
        logger.info("Starting to process sites.")

        for i, api_config_site in enumerate(api_config_sites):
            time.sleep(10)  # Simulating delay
            if successful_postings >= num_sites:
                break
            
            map_iframe = column_c_data[i % len(column_c_data)] if column_c_data else None

            # Process the site and get the result
            success, posted_url = process_site(second_column_data, api_config_site, map_iframe, avoid_root_domain)

            if success and posted_url:  # Ensure success and posted_url are valid
                posted_urls.append(posted_url)
                logger.info(f"Posting successful for {api_config_site.website}. Posted URL: {posted_url}")
                successful_postings += 1

                self.update_state(state='single_post_done', meta={
                    'current': successful_postings,
                    'total': num_sites,
                    'posted_urls': posted_urls,
                    'last_posted_url': posted_url
                })
            else:
                logger.info(f"Posting skipped for {api_config_site.website}.")

        if successful_postings > 0:
                output_dir = os.path.join(settings.MEDIA_ROOT, 'GEO_output_folder')
                os.makedirs(output_dir, exist_ok=True)
                  # Get a unique filename
                unique_filename = get_unique_filename(f"{original_filename}_url_lists.xlsx", output_dir)
                output_file_path = os.path.join(output_dir, unique_filename)
                save_posted_urls_to_excel(posted_urls, output_file_path)

                logger.info(f"Excel file with posted URLs created at: {output_file_path}")

                self.update_state(state='SUCCESS', meta={
                    'result': posted_urls,  
                    'successful_postings': successful_postings,
                    'file_path': output_file_path
                })
        else:
            self.update_state(state='FAILURE', meta={'error': "No successful postings."})

        
        return posted_urls

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        self.update_state(state='FAILURE', meta={
            'exc_type': type(e).__name__,
            'error': str(e),
        })
        raise Ignore()  


def save_posted_urls_to_excel(posted_urls, output_file_path):
    """Save the list of posted URLs to an Excel file."""
    df = pd.DataFrame(posted_urls, columns=['Posted URL'])
    df.to_excel(output_file_path, index=False, engine='openpyxl')
    return output_file_path  # Return the file path



def process_site(second_column_data, api_config_site, map_iframe, avoid_root_domain):
    # Extract required fields from the dataframe safely
    city = second_column_data.get('city_single', '')
    state = second_column_data.get('state_single', '')
    zip_code = second_column_data.get('zip_single', '')
    keywords_list = second_column_data.get('keywords_list', [])
    services_provide_list = second_column_data.get('services_provide_list', [])
    business_name = second_column_data.get('business_name_single', '')
    street_address = second_column_data.get('street_address_single', '')
    phone = second_column_data.get('phone_single', '')
    target_url = second_column_data.get('target_url_single', '')

    # Fetch or create the site record
    site_record, created = SiteRecordContentGen.objects.get_or_create(site_name=api_config_site.website)

    # Simplified check for root domain matching
    if avoid_root_domain:
        # Get root domain of the target URL
        target_root_domain = get_root_domain(target_url)
        
        # Loop through business_domains and check root domains
        for domain in site_record.business_domains:
            if get_root_domain(domain) == target_root_domain:
                logger.warning(f"Root domain {target_root_domain} already exists for {api_config_site}, skipping posting.")
                return False, None
    else:
        # Regular check for exact target URL in business_domains
        if target_url in site_record.business_domains:
            logger.warning(f"Target URL {target_url} already exists for {api_config_site}, skipping posting.")
            return False, None

    logger.info(f"Start to post on {api_config_site.website}")
    # Generate article using OpenAI
    generate_title = generate_article(generate_prompt_for_title(city, state, zip_code))
    # generate_title = "TE$T TITLE"
    prompt = generate_prompt_for_content(city, state, zip_code, keywords_list, services_provide_list, business_name, street_address, phone, target_url, map_iframe)
    article = generate_article(prompt)
    # article = "TEST CONTENT"


    # Post article to WordPress using the APIConfig model
    status_code, response_or_posted_url = post_to_wordpress(api_config_site, generate_title, article)

    # If post to WordPress is successful (201), update the SiteRecordContentGen
    if status_code == 201:
        # Append the new target_url to business_domains and save
        site_record.business_domains.append(target_url)
        site_record.save()
        logger.info(f"Updated SiteRecordContentGen for {api_config_site} with new domain: {target_url}")
        return True, response_or_posted_url
    else:
        logger.error(f"Failed to post to WordPress. Status code: {status_code}, response: {response_or_posted_url}")
        return False, response_or_posted_url if response_or_posted_url else 'No response'


def post_to_wordpress(api_config, generate_title, article):
    # Define the WordPress REST API endpoint and authentication
    wp_url = f"https://{api_config.website}/wp-json/wp/v2/posts"
    auth = (api_config.user, api_config.password)
    
    # Post data payload
    post_data = {
        'title': generate_title.strip('“').strip('”') if generate_title else "Untitled",
        'content': article,
        'status': 'publish'
    }

    # Send POST request to WordPress
    try:
        response = requests.post(wp_url, json=post_data, auth=auth)
        response.raise_for_status()  # Raise an error for bad responses
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create post: {e}")
        return 500, str(e)

    logger.info(f"Post created successfully: {response.json()['link']}")
    return 201, response.json()['link']


def generate_prompt_for_title(city, state, zip_code):
    """
    Generates a title for the article, instructing the model to focus on geo-related aspects without quotation marks.
    """
    return f"""
    You are a professional content writer tasked with creating a compelling title for a geo-related article. The title must highlight the specific location, notable places, and things to do in or around the area of {city}, {state} {zip_code}. The title should not mention the company name but should be engaging and reflect the local aspects of the region.
    The title should be concise and relevant to people interested in the area.
    **Note:** Do not use quotation marks (") at the beginning or end of the title. Simply create a blog post title without any surrounding quotes.
    """

        
def generate_prompt_for_content(city, state, zip_code, keywords_list, services_provide_list, business_name, street_address, phone, target_url,map_iframe):
    """
    Generates the content prompt for the article based on the business and location information.
    The content should follow the guidelines provided for writing geo-related articles.
    """
    # Combine city, state, and zip code for full location reference
    city_state_zip = f"{city}, {state} {zip_code}"
    
    # Return the structured OpenAI prompt for content
    return f"""
    You are a professional content writer for a business tasked with writing unique geo-related articles that must talk about the specific location, notable places, things to do, and historical sites. The article must meet the following requirements:

    1. Each article must be close to 650 words and never less than 600 words.
    2. The structure of each article must be as follows:
        a) A 500-word post that talks about the location, points of interest, and notable places around {city_state_zip}. **Do not talk about the company itself.**
        b) A "Member Spotlight" section that includes the Name, Address, Phone (NAP) of the business:
            - The business name: {business_name}, full address: {street_address}, {city_state_zip}, phone: {phone}, and website: {target_url}.
        c) A 100-word section that mentions only **one** keyword from the list: {keywords_list}. **This section should include just a single <h2> with the keyword and a short paragraph about the company and services:{services_provide_list}, without any additional heading such as "Keyword Part."**
    3. **Do not put any keywords into quotes**, and do not use keywords as search terms.
    4. The post don't need the title/h1, as title will be created on seperate prompt
    5. Include a Google Maps direction '{map_iframe}' exact iframe in the article to the business's location in the 'Member Spotlight' section.

    ### Here’s the company information for the 'Member Spotlight' section:

    <h2>Member Spotlight</h2>
    {business_name}<br>
    {street_address}<br>
    {city_state_zip}<br>
    {phone}<br>
    {target_url}

    ### Example HTML Formatting for WP:
    1. Use `<h2>` for section titles.
    2. Use `<p>` tags for paragraphs.
    3. Use `<strong>` tags for bold text where appropriate.
    4. Use `<ul>` and `<li>` tags for bullet points when necessary.

    **Note:** The article should be formatted with the appropriate HTML tags for WordPress.
    """

def generate_article(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a professional content writer."},
                  {"role": "user", "content": prompt}],
        max_tokens=1500
    )
    # access the content safely
    content = response.choices[0].message['content']
    return content.strip()

