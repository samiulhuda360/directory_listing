import pandas as pd
import openai
import requests
from django.core.files.storage import default_storage
from .models import APIConfig
from django.conf import settings
from .models import OpenAI_APIKeyConfig, SiteRecordContentGen
import os
from django.core.exceptions import ObjectDoesNotExist

def get_openai_api_key():
    try:
        api_config = OpenAI_APIKeyConfig.objects.first()
        if api_config:
            return api_config.api_key
        else:
            raise ValueError("No OpenAI API key found")
    except ObjectDoesNotExist:
        raise ValueError("OpenAI_APIKeyConfig table does not exist. Please run migrations.")


openai.api_key = get_openai_api_key()



def process_xls_file(file, num_sites):
    # Ensure the 'tmp/' directory exists
    tmp_dir = 'tmp/'
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    # Save the uploaded file temporarily
    file_path = default_storage.save(os.path.join(tmp_dir, file.name), file)

    # Check if the file exists before proceeding
    full_file_path = default_storage.path(file_path)
    if not os.path.exists(full_file_path):
        return []

    # Load the file using pandas
    df = pd.read_excel(full_file_path, header=None, engine='openpyxl')

    # Set the first column as index (for variable names or something else)
    df = df.set_index(0)

    # Extract the second column (B column in Excel)
    second_column_data = df[1]  # Extracting column B

    # Extract the data from the third column (C column in Excel, index 2)
    column_c_data = df[2].dropna().tolist()  # Drop blank rows and convert to list

    # Fetch all enabled sites from API configuration
    api_config_sites = APIConfig.objects.filter(site_enable=True)
    print("All Site List:", api_config_sites)

    # List to store posted URLs
    posted_urls = []
    
    successful_postings = 0  # Initialize a counter for successful postings
    total_sites_processed = 0  # Counter to track processed sites

    while successful_postings < num_sites:
        # If all sites have been processed, stop
        if total_sites_processed >= len(api_config_sites):
            print("All enabled sites have been processed.")
            break

        # Get the current site from the API config
        api_config_site = api_config_sites[total_sites_processed]

        map_iframe = column_c_data[total_sites_processed % len(column_c_data)] if column_c_data else None  
        
        success, posted_url = process_site(second_column_data, api_config_site, map_iframe)   

        # Process the site and check if successful
        if success:
            posted_urls.append(posted_url)
            print(f"Posting successful for {api_config_site.website}.")
            successful_postings += 1  # Increment the successful postings counter
        else:
            print(f"Posting skipped for {api_config_site.website}.")

        total_sites_processed += 1  # Increment the total sites processed counter

    # After the loop, you can print the total number of successful postings
    print(f"Total successful postings: {successful_postings} out of {total_sites_processed}.")     
    print(posted_urls)
    return posted_urls 


def process_site(second_column_data, api_config_site, map_iframe):
    # Extract required fields from the dataframe
    city = second_column_data.get('city_single')
    state = second_column_data.get('state_single')
    zip_code = second_column_data.get('zip_single')
    keywords_list = second_column_data.get('keywords_list')
    services_provide_list = second_column_data.get('services_provide_list')
    business_name = second_column_data.get('business_name_single')
    street_address = second_column_data.get('street_address_single')
    phone = second_column_data.get('phone_single')
    target_url = second_column_data.get('target_ur_single')
    
    
    # Fetch or create the site record
    site_record, created = SiteRecordContentGen.objects.get_or_create(site_name=api_config_site.website)

    # Check if the target URL already exists in the business_domains list
    if target_url in site_record.business_domains:
        print(f"Target URL {target_url} already exists for {api_config_site.website}, skipping posting.")
        return False  
    print(f"Start to post on {api_config_site.website}")
    # Generate article using OpenAI
    generate_title = generate_article(generate_prompt_for_title(city, state, zip_code))
    prompt = generate_prompt_for_content(city, state, zip_code, keywords_list, services_provide_list, business_name, street_address, phone, target_url, map_iframe)
    print("Title: ", generate_title)
    print(prompt)
    article = generate_article(prompt)


    # Post article to WordPress using the APIConfig model
    status_code, response_or_posted_url = post_to_wordpress(api_config_site, generate_title, article)

    # If post to WordPress is successful (201), update the SiteRecordContentGen
    if status_code == 201:
        # Append the new target_url to business_domains and save
        site_record.business_domains.append(target_url)
        site_record.save()
        print(f"Updated SiteRecordContentGen for {api_config_site.website} with new domain: {target_url}")
        return True, response_or_posted_url  # Indicate success
    else:
        print(f"Failed to post to WordPress. Status code: {status_code}, response: {response_data}")
        return False  # Indicate failure




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
    print(city_state_zip)
    
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
    return response.choices[0]['message']['content'].strip()


def post_to_wordpress(api_config, generate_title, article):
    # Define the WordPress REST API endpoint and authentication
    wp_url = f"https://{api_config.website}/wp-json/wp/v2/posts"
    auth = (api_config.user, api_config.password)
    
    # Post data payload
    post_data = {
        'title': generate_title,
        'content': article,
        'status': 'draft'
    }

    # Send POST request to WordPress
    response = requests.post(wp_url, json=post_data, auth=auth)

    if response.status_code == 201:
        print(f"Post created successfully: {response.json()['link']}")
        return 201, response.json()['link']
    else:
        print(f"Failed to create post: {response.content}")
        return response.status_code, response.content

