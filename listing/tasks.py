from celery import shared_task
import requests
import base64
import json
import time
from .models import CompanyURL,WebsiteData
from celery.utils.log import get_task_logger
from celery.exceptions import Ignore
from requests.auth import HTTPBasicAuth


logger = get_task_logger(__name__)

def get_root_domain(url):
    # Add scheme if missing
    if not urlparse(url).scheme:
        url = f"http://{url}"
    
    # Parse the URL and extract the root domain
    parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.split('.')
    root_domain = '.'.join(domain_parts[-2:]) if len(domain_parts) > 1 else parsed_url.netloc
    return root_domain

def convert_to_embed_url(youtube_url):
    # Return an empty string if the input URL is blank
    if not youtube_url:
        return ""

    # Check if the URL is already an embed URL
    if "youtube.com/embed/" in youtube_url:
        return youtube_url  # It's already an embed URL, no change needed

    # Check if the URL is a valid watch URL and extract the video ID
    elif "watch?v=" in youtube_url:
        video_id = youtube_url.split('watch?v=')[-1]
        # Create the embed URL with the extracted video ID
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        return embed_url

    else:
        return "Invalid YouTube URL"

@shared_task
def sample_task():
  print("Test task executed.")
  return 1

@shared_task
def create_company_profile_post(row_values, json_url, website, user, password, html_template):
    credentials = user + ':' + password
    token = base64.b64encode(credentials.encode())
    header = {'Authorization': 'Basic ' + token.decode('utf-8'), 'Content-Type': 'application/json'}

    # Ensure row_values is a list with enough elements

    company_name = row_values[0]
    post_slug = row_values[1]
    description = row_values[2]
    complete_address = row_values[3]
    company_website = row_values[4]
    company_phone_number = row_values[5]
    contact_email = row_values[6]
    company_hours_raw = row_values[7]
    company_logo_url = row_values[8]
    google_map_src = row_values[9]
    target_location = row_values[10]
    services_offered = row_values[11]
    gallery_image_urls = row_values[12]
    youtube_video_url = convert_to_embed_url(row_values[13])
    linkedin_url = row_values[14]
    facebook_url = row_values[15]
    twitter_url = row_values[16]
    youtube_url = row_values[17]
    new_username = row_values[18]
    user_email = row_values[19]
    user_password = row_values[20]
    schema_code = row_values[21]
    
    ##Direction Logic
    
    if row_values[22] is None or "iframe" not in row_values[22]:
        map_direction_iframe_1 = '</div>'
        map_direction_iframe_2 = ""
        map_direction_iframe_3 = ''
    else:
        map_direction_iframe_1 = '<h2>How to Visit Us</h2><div style="display: flex; flex-wrap: wrap; justify-content: center; margin: 0; padding: 0;">' + row_values[22] + '</div></div><style>@media (max-width: 668px) { div { flex-direction: column; } iframe { width: 100%; margin: 3px; } } @media (min-width: 669px) { iframe { width: 47%; margin: 0px; } }</style>'
        map_direction_iframe_2 = '<h2 class="feature-title">How to Visit Us</h2><div style="display: flex; flex-wrap: wrap; justify-content: center; margin: 0; padding: 0;">' + row_values[22] + '</div><style>@media (max-width: 668px) { div { flex-direction: column; } iframe { width: 100%; margin: 3px; } } @media (min-width: 669px) { iframe { width: 47%; margin: 0px; } }</style>'
        map_direction_iframe_3 = '<h2>How to Visit Us</h2><div style="display: flex; flex-wrap: wrap; justify-content: center; margin: 0; padding: 0;">' + row_values[22] + '</div><style>@media (max-width: 668px) { div { flex-direction: column; } iframe { width: 100%; margin: 3px; } } @media (min-width: 669px) { iframe { width: 47%; margin: 0px; } }</style>'

    print(youtube_url)
    # Processing company hours
    company_hours = company_hours_raw.split('\n') if company_hours_raw else []
    hours_html = "".join(f"<span><i class='fas fa-clock'></i> {day}</span><br>" for day in company_hours)
    # Processing gallery images
    galleries = ""
    if gallery_image_urls:
        url_list = [url.strip() for url in gallery_image_urls.split(',')]
        gallery_images_html = "".join([f'<img src="{url}" alt="Photo {index + 1}">' for index, url in enumerate(url_list)])
        galleries = f"""<div class="company-info">
            <h2>Our Gallery</h2>
            <div class="gallery">{gallery_images_html}</div>
          </div>"""

    if youtube_video_url:
        youtube_template_1 = f"""<div class="company-info">
            <h2>Watch Our Video</h2>
            <iframe src="{youtube_video_url}" style="width: 65%; height: 400px;" allowfullscreen></iframe>
          </div>"""
    else:
      youtube_template_1 = ""


    linkedin_link_html_1 = ""
    facebook_link_html_1 = ""
    twitter_link_html_1 = ""
    youtube_link_html_1 = ""

    if linkedin_url:
        linkedin_link_html_1 = f"""<a href="{linkedin_url}" target="_blank" rel="noopener"><i class="fab fa-linkedin-in"></i></a>"""
    else:
        linkedin_link_html_1 = ""
    if facebook_url:
        facebook_link_html_1 = f"""<a href="{facebook_url}" target="_blank" rel="noopener"><i class="fab fa-facebook-f"></i></a>"""
    else:
        facebook_link_html_1= ""
    if twitter_url:
        twitter_link_html_1 = f"""<a href="{twitter_url}" target="_blank" rel="noopener"><i class="fab fa-twitter"></i></a>"""
    else:
        twitter_link_html_1 = ""
    if youtube_url:
        youtube_link_html_1 = f"""<a href="{youtube_url}" target="_blank" rel="noopener"><i class="fab fa-youtube"></i></a>"""
    else:
        youtube_link_html_1 = ""

    if not (linkedin_url or facebook_url or twitter_url or youtube_url):
        social_template_1 = ""
    else:
        social_template_1 = f"""<div class="company-info">
            <h2>Connect With Us</h2>
            <div class="social-media">
             {linkedin_link_html_1}
             {facebook_link_html_1}
             {twitter_link_html_1}
             {youtube_link_html_1}
            </div>
          </div>"""
        
    # Constructing the HTML content
    html_1 = f"""<!-- wp:html --><div class="container">
          <div class="company-profile-header">
            <img src="{company_logo_url}" alt="Company Logo">
          </div>
          <div class="info-and-map">
            <div class="info-block">
            <div class="highlight">
              <h2>About the Company</h2>
                <p>{description}</p>
              </div>
              <div class="highlight">
                <h2>Opening Hours</h2>
                <p>{hours_html}</p>
              </div>
            </div>
            <div class="map-container">
              <h2>Contact Information</h2>
                <p><i class="fas fa-map-marker-alt"></i> Address: {complete_address}</p>
                <p><i class="fas fa-globe"></i> Website: <a href="{company_website}" target="_blank">{company_website}</a></p>
                <p><i class="fas fa-phone"></i> Phone: <a href="tel:{company_phone_number}">{company_phone_number}</a></p>
                <p><i class="fas fa-envelope"></i> Email: <a href="mailto:{contact_email}">{contact_email}</a></p>
              <h2>Find Us On The Map</h2>
              {google_map_src}
            </div>
          </div>
         <div class="highlight">
            <h2>Brands/Services Offered</h2>
            <p>{services_offered}</p>
          </div>
            {galleries}

         {youtube_template_1}
        {social_template_1}         

        {map_direction_iframe_1} {schema_code}<!-- /wp:html -->"""
    
        
    galleries_2 = ""
    img_list = ""  # Initialize img_list here

    if gallery_image_urls:
        url_list = [url.strip() for url in gallery_image_urls.split(',')]
        for i, url in enumerate(url_list, start=1):
            img_list += f'<div class="gallery-item"><img src="{url}" alt="Gallery Image {i}"></div>\n'

    galleries_2 = f'<section id="gallerySection" class="gallery-section"><h2 class="feature-title">Gallery</h2><div class="gallery-content">{img_list}</div></section>'

   # Initialize an empty string to store the HTML code
    social_media_buttons = ""

    # Check if each URL has a value and generate the corresponding HTML
    print("LInkedin URL:", linkedin_url)
    if linkedin_url:
        social_media_buttons += f'''
          <!-- LinkedIn -->
          <a title="LinkedIn" class="button-social has-action" href="{linkedin_url}" target="_blank">
            <i class="fab fa-linkedin-in"></i>
          </a>
        '''

    if facebook_url:
        social_media_buttons += f'''
          <!-- Facebook -->
          <a title="Facebook" class="button-social has-action" href="{facebook_url}" target="_blank">
            <i class="fab fa-facebook-f"></i>
          </a>
        '''

    if twitter_url:
        social_media_buttons += f'''
          <!-- Twitter -->
          <a title="Twitter" class="button-social has-action" href="{twitter_url}" target="_blank">
            <i class="fab fa-twitter"></i>
          </a>
        '''

    if youtube_url:
        social_media_buttons += f'''
          <!-- YouTube -->
          <a title="YouTube" class="button-social has-action" href="{youtube_url}" target="_blank">
           <i class="fab fa-youtube"></i>
          </a>
        '''

    # Check if any social media buttons were generated
    if social_media_buttons:
        # Create the enclosing <div> for the buttons
        social_media_buttons = f'<section class="section-wrap" id="socialMediaLinks"><h2 class="feature-title">Digital & Online Presence</h2><div class="social-presence"><ul><li class="social-action"><div class="btn-group">\n{social_media_buttons}\n</div></li></ul></div></section>'
    
    hours_html_2 = "".join(f"<span><i class='fas fa-clock'></i> {day}</span>" for day in company_hours)

    if youtube_video_url:
        youtube_template_2 = f"""<!-- YouTube Video Embed Section -->
    <div id="youtubeVideoSection" class="youtube-video-section">
        <h2 class="feature-title">Our YouTube Video</h2>
        <div class="youtube-video-embed">
            <iframe width="560" height="315" src="{youtube_video_url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
        </div>
    </div>"""
    else:
        youtube_template_2 = ""

    html_2 = f"""<!-- wp:html --><div class="business-profile">
    <div class="navigation-menu">
      <div class="menu-links">
        <a href="#companyOverview" class="link-item active">About Company</a>
        <a href="#gallerySection" class="link-item">Gallery</a>
        <a href="#socialMediaLinks" class="link-item">Social Media</a>
      </div>
    </div>

    <div id="companyOverview" class="profile-overview">
        <div class="overview-content">
          <h2 class="section-title">Business Overview</h2>
          <div class="business-description">
            <p>
              {description}
            </p>
          </div>
          <div class="services-offered">
            <h3 class="services-title">Services offered</h3>
            <span>{services_offered}</span>
          </div>

          <div class="additional-info">
            <div class="info-item">
              <h3>Company Website</h3>
              <p><a href="{company_website}">{company_website}</a></p>
            </div>
            <div class="info-item">
              <h3>Company Phone Number</h3>
              <p><a href="tel:{company_phone_number}">{company_phone_number}</a></p>
            </div>
            <div class="info-item">
              <h3>Company Email</h3>
              <p><a href="mailto:{contact_email}">{contact_email}</a></p>
            </div>
            <div class="info-item">
              <h3>Address</h3>
              <p>{complete_address}</p>
            </div>
          </div>
        </div>
    </div>

    <!-- Opening Hours Section -->
    <div class="opening-hours">
        <div class="hours-content">
            <h2 class="section-title">Opening Hours</h2>
            <div class="hours-list">
                {hours_html_2}
            </div>
        </div>
    </div>

    {galleries_2}

    {youtube_template_2}

    <div id="mapsection" class="map-location-section">
        <h2 class="feature-title">Find Us On Map</h2>
        <div class="google-maps-embed">
            {google_map_src}
        </div>
    </div>
    {social_media_buttons} 
</div> {map_direction_iframe_2} {schema_code} <!-- /wp:html -->"""
    
    html_img_tags = ""
    # Split the URLs and remove any leading/trailing whitespace
    url_list = [url.strip() for url in gallery_image_urls.split(',')]

    # Iterate over the image URLs and create HTML img tags
    for i, url in enumerate(url_list, start=1):
        html_img_tags += f'<img decoding="async" src="{url}" alt="Photo {i}">\n'



    # Generate the HTML for each image
    gallery_images_html_3 = "".join([
        f'<img decoding="async" src="{url}" alt="Gallery image {index + 1}">'
        for index, url in enumerate(url_list)
    ])


    if facebook_url:
        facebook_link_html_3 = f"""<a title="Facebook" class="button-social has-action" href="{facebook_url}" target="_blank">
              <i class="fab fa-facebook-f"></i></a>"""
    else:
        facebook_link_html_3 = ""
        
    if youtube_url:
        youtube_link_html_3 = f"""<a title="YouTube" class="button-social has-action" href="{youtube_url}" target="_blank">
              <i class="fab fa-youtube"></i></a>"""
    else:
        youtube_link_html_3 = ""
                  
    # Check if linkedin_url is not empty
    if linkedin_url:
        linkedin_link_html_3 = f"""<a title="LinkedIn" class="button-social has-action" href="{linkedin_url}" target="_blank">
              <i class="fab fa-linkedin"></i></a>"""
    else:
        linkedin_link_html_3 = ""

    # Check if twitter_url is not empty
    if twitter_url:
        twitter_link_html_3 = f"""<a title="Twitter" class="button-social has-action" href="{twitter_url}" target="_blank">
              <i class="fa fa-twitter"></i></a>"""  # Note: Change 'fa fa-times' to 'fa fa-twitter'
    else:
        twitter_link_html_3 = ""

    if youtube_video_url:
        youtube_template_3 = f"""<div><ul class="nav nav-tabs" id="myTab" role="tablist">
            <li class="nav-item" role="presentation">
              <button class="nav-link active" id="youtube-tab" data-bs-toggle="tab" data-bs-target="#youtube" type="button" role="tab" aria-controls="gallery" aria-selected="false">Youtube</button>
      </li>
    </ul>
    </div>
    <div class="tab-content" id="myTabContentYoutube">
      <div class="tab-pane fade show active" id="youtube" role="tabpanel" aria-labelledby="youtube-tab">
          <div class="youtube-embed">
            <iframe width="100%" height="auto" src="{youtube_video_url}" frameborder="0" allowfullscreen></iframe>
          </div>
      </div>
  </div>"""
    else:
        youtube_template_3 = ""

    html_3 = f"""<!-- wp:html --><div class="profile-box">
    <div class="container">
    <div class="row">
    <div class="col-12 col-lg-12 col-xl-9 float-left">
      <div class="dc-docsingle-header">
        <figure class="dc-docsingleimg">
        <img class="dc-ava-detail entered lazyloaded" src="{company_logo_url}" alt="Stuart Gordon" data-lazy-src="https://doctortoyou.b-cdn.net/wp-content/themes/doctreat/images/dravatar-255x250.jpg" data-ll-status="loaded"><noscript><img class="dc-ava-detail" src="https://doctortoyou.b-cdn.net/wp-content/themes/doctreat/images/dravatar-255x250.jpg" alt="Stuart Gordon"></noscript>
        <img class="dc-ava-detail-2x" src="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%200%200'%3E%3C/svg%3E" alt="Stuart Gordon" data-lazy-src="https://doctortoyou.b-cdn.net/wp-content/themes/doctreat/images/dravatar-545x428.jpg"><noscript><img class="dc-ava-detail-2x" src="https://doctortoyou.b-cdn.net/wp-content/themes/doctreat/images/dravatar-545x428.jpg" alt="Stuart Gordon"></noscript>
    
            </figure>
      <div class="dc-docsingle-content">
      <div class="dc-title">
                    <h2><a href="{company_website}" data-wpel-link="internal">{company_name}</a>
            <i class="far fa-check-circle dc-awardtooltip dc-tipso tipso_style" data-tipso="Verified user"></i>
              </h2>
    
      </div>
            <div class="rd-description">
          <p>{description}</p>
        </div>
    
    </div>
    </div>
    <div>
      <ul class="nav nav-tabs" id="myTab" role="tablist">
        <li class="nav-item" role="presentation">
          <button class="nav-link active" id="services-tab" data-bs-toggle="tab" data-bs-target="#services" type="button" role="tab" aria-controls="services" aria-selected="true">Offered Services</button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="social-tab" data-bs-toggle="tab" data-bs-target="#social" type="button" role="tab" aria-controls="social" aria-selected="false">Social Presence</button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="opening-tab" data-bs-toggle="tab" data-bs-target="#opening" type="button" role="tab" aria-controls="opening" aria-selected="false">Opening Hours</button>
        </li>
    </ul>
    </div>
          
    <div class="tab-content" id="myTabContent">
      <div class="tab-pane fade show active" id="services" role="tabpanel" aria-labelledby="services-tab">
       {services_offered}
      </div>
    
        <div class="tab-pane fade" id="social" role="tabpanel" aria-labelledby="social-tab">
              <div class="btn-group">
              {facebook_link_html_3}
              {youtube_link_html_3}
              {linkedin_link_html_3}
              {twitter_link_html_3}
          </div>
            </div>
        <div class="tab-pane fade" id="opening" role="tabpanel" aria-labelledby="opening-tab">
           <p>{hours_html}</p>
        </div>           
          </div>
          <div>
          <ul class="nav nav-tabs" id="myTab" role="tablist">
              <li class="nav-item" role="presentation">
                <button class="nav-link active" id="contact-tab" data-bs-toggle="tab" data-bs-target="#contact" type="button" role="tab" aria-controls="contact" aria-selected="false">Contact Details</button>
              </li>
          </ul>
          </div>
    <div class="tab-content" id="myTabContent">
      <div class="tab-pane fade show active" id="contact" role="tabpanel" aria-labelledby="contact-tab">
    <p><i class="fas fa-globe"></i> Website: <a href="{company_website}" target="_blank" rel="noopener">{company_website}</a></p>
          <p><i class="fas fa-phone"></i> Phone: <a href="tel:{company_phone_number}">{company_phone_number}</a></p>
          <p><i class="fas fa-envelope"></i> Email: <a href="mailto:{contact_email}">{contact_email}</a></p>
        </div>
    </div>
    <div><ul class="nav nav-tabs" id="myTab" role="tablist">
            <li class="nav-item" role="presentation">
              <button class="nav-link active" id="gallery-tab" data-bs-toggle="tab" data-bs-target="#gallery" type="button" role="tab" aria-controls="gallery" aria-selected="false">Gallery</button>
            </li>
    </ul>
    </div>
    <div class="tab-content" id="myTabContent">
            <div class="tab-pane fade show active" id="gallery" role="tabpanel" aria-labelledby="gallery-tab">
              <div class="gallery">
                {gallery_images_html_3}
              </div>
            </div>  
          </div>
    {youtube_template_3}            
    </div>
    <div class="col-12 col-md-6 col-lg-6 col-xl-3 float-left">
      <aside id="dc-sidebar" class="dc-sidebar dc-sidebar-grid float-left mt-xl-0">
        <div class="map-container">
           {google_map_src}
      </div>							
    <div class="dc-contactinfobox dc-locationbox">
                <ul class="dc-contactinfo">
                    <li class="dcuser-location">
                    <i class="lnr lnr-location"></i>
                        {complete_address}
                    </li>
                        <li class="dcuser-screen">
                        <i class="lnr lnr-screen"></i>
                        <span><a href="{company_website}" target="_blank" data-wpel-link="external" rel="external noopener noreferrer">{company_website}</a></span>
                    </li>                        
                    </ul>
    </div>
        
    </aside>
    </div>
    </div>
    </div>
    </div> {map_direction_iframe_3} {schema_code} <!-- /wp:html -->"""

    if html_template == 1:
        final_content = html_1
    elif html_template == 2:
        final_content = html_2
    elif html_template == 3:
        final_content = html_3
        


    # Data for creating a new user with the 'author' role
    new_user_data = {
        'username': new_username,
        'email': user_email,
        'password': user_password,
        'roles': ['author']  # Set the role to 'author'
    }

    # Send the request to create a new user
    print("USER", new_username)
    print("mail", user_email)
    print("PASS:", user_password)



    # Initialize a flag to determine whether we have a valid user ID
    valid_user_id = False
    Author_name = "Default"

    # Only attempt to create or fetch a user if all user details are provided
    if new_username and user_email and user_password:

        new_user_data = {
            'username': new_username,
            'email': user_email,
            'password': user_password,
            'roles': ['author']  # Assuming the platform supports setting roles via API
        }

        # Attempt to create a new user
        user_response = requests.post(json_url + '/users', headers=header, json=new_user_data)

        if user_response.status_code == 201:
            print('New user created successfully!')
            new_user_id = user_response.json()['id']
            valid_user_id = True
            Author_name = new_username
        else:
            print('User already exists. Fetching existing user ID...')
            user_query_params = {'search': new_username}
            existing_user_response = requests.get(json_url + '/users', headers=header, params=user_query_params)

            if existing_user_response.status_code == 200 and existing_user_response.json():
                new_user_id = existing_user_response.json()[0]['id']
                print('Existing user ID:', new_user_id)
                valid_user_id = True
                Author_name = new_username
            else:
                print('Failed to fetch existing user. Proceeding without specifying an author.')

    post_data = {
        'title': company_name,
        'slug': post_slug,
        'status': 'publish',
        'content': final_content
    }

    if valid_user_id:
        post_data['author'] = new_user_id

    # Send the post request
    response = requests.post(json_url + '/posts', headers=header, json=post_data)



    if response.status_code == 201:
        print("Post created successfully.")
        post_link = response.json().get('link')
        return Author_name, post_link, website, company_website
    else:
        print("Failed to create post.")
        print(response.text)
        return Author_name, None, website, company_website



# Function to post content to WordPress site
def test_post_to_wordpress(site_url, username, app_password, content):
    url_json = "https://" + site_url + "/wp-json/wp/v2/posts"
    credentials = username + ':' + app_password
    token = base64.b64encode(credentials.encode())
    headers = {'Authorization': 'Basic ' + token.decode('utf-8')}
    data = {
        "title": "Test Post from API",
        "content": content,
        "status": "draft"
    }

    try:
        response = requests.post(url_json, headers=headers, json=data)
        return response
    
    except requests.exceptions.ConnectionError:
        return None  # Or return an appropriate response indicating a connection error

def delete_from_wordpress(site_url, username, app_password, post_id):
    url_json = "https://" + site_url + f"/wp-json/wp/v2/posts/{post_id}"
    credentials = username + ':' + app_password
    token = base64.b64encode(credentials.encode())
    headers = {'Authorization': 'Basic ' + token.decode('utf-8')}

    try:
        response = requests.delete(url_json, headers=headers)
        return response
    except requests.exceptions.ConnectionError:
        return None  # Or return an appropriate response indicating a connection error
    

@shared_task(bind=True) 
def perform_test_task(self, config_id):
    try:
        from .models import APIConfig, TestResult  # Import here to avoid circular import
        config = APIConfig.objects.get(id=config_id)
        
        # Mocking the test function behavior
        response = test_post_to_wordpress(config.website, config.user, config.password, "Test Content")
        if response.status_code in [201]:
            response_data = response.json()
            post_id = response_data.get('id')
            delete_response = delete_from_wordpress(config.website, config.user, config.password, post_id)
            
            if delete_response is not None and delete_response.status_code == 200:
                result = 'Success'
            else:
                result = 'Failed to delete post'
        else:
            result = f'Failed with status code: {response.status_code}'
        
        # Store the result somewhere that the AJAX can retrieve
        TestResult.objects.create(config=config, status=result)
    except Exception as e:
        # Log the error
        print(f"Error in perform_test_task for config ID {config_id}: {e}")
        # Store the error status
        TestResult.objects.create(config_id=config_id, status='Error')

from urllib.parse import urlparse
from .models import APIConfig

@shared_task(bind=True)
def delete_post_by_url(self, post_url):
    parsed_url = urlparse(post_url)
    domain = parsed_url.netloc
    logger.info("POST DOMAIN: %s", domain)

    try:
        config = APIConfig.objects.get(website__icontains=domain)
        post_id = find_post_id_by_url(domain, post_url, config.user, config.password)
        if post_id:
            api_url = f"https://{domain}/wp-json/wp/v2/posts/{post_id}"
            response = requests.delete(api_url, auth=(config.user, config.password))
            if response.status_code == 200:
                logger.info("Successfully deleted post: %s", post_url)
                try:
                    company_url_instance = CompanyURL.objects.get(generated_url=post_url)
                    company_website = company_url_instance.company_website
                    company_url_instance.delete()  # Delete from CompanyURL model

                    website_data_instances = WebsiteData.objects.filter(api_config__website__icontains=domain)
                    for website_data in website_data_instances:
                        existing_company_websites = json.loads(website_data.company_websites) if website_data.company_websites else []
                        if company_website in existing_company_websites:
                            existing_company_websites.remove(company_website)
                            website_data.company_websites = json.dumps(existing_company_websites) if existing_company_websites else None
                            website_data.save()
                    return True  # Indicate success
                except CompanyURL.DoesNotExist:
                    logger.warning("No company website found for URL: %s", post_url)
                    return False
                    # No need to change the return value as the post has been successfully deleted.
                except Exception as e:
                    # Handle unexpected exceptions during the database update.
                    logger.error("Unexpected error occurred: %s", str(e))
                    return False
                    
            else:  
                logger.error("Failed to delete post: %s, Status Code: %s", post_url, response.status_code)
                return False   
        else:
            logger.error("Post ID not found for URL: %s", post_url)
        return False   
    except APIConfig.DoesNotExist:
        logger.error("Configuration not found for %s", domain)
        return False
    except Exception as e:
        logger.error("An unexpected error occurred: %s", str(e))
    return False



def find_post_id_by_url(domain_name, post_url, username, app_password):
    base_url = f"https://{domain_name}/wp-json/wp/v2/posts"
    headers = {
        'Authorization': f'Basic {username}:{app_password}'
    }
    per_page = 100
    page = 1
    while True:
        params = {
            'per_page': per_page,
            'page': page
        }
        response = requests.get(base_url, auth=HTTPBasicAuth(username, app_password), params=params)
        print(username)
        
        # If a 400 status code is received, stop the search
        if response.status_code == 400:
            print("Reached end of posts or encountered an error.")
            break
        
        # Check for successful response
        if response.status_code == 200:
            data = response.json()
            if not data:  # Empty list means no more posts available
                break
            # Find the post ID
            for post in data:
                if post['link'] == post_url:
                    return post['id']  # Return the found post ID
            page += 1  # Increment page number to fetch the next set of posts
        else:
            print(f"Error fetching posts: {response.status_code}")
            break

    return None  # Return None if post not found or if there was an error
  
@shared_task
def update_company_profile_post(row_values, json_url, website, user, password, html_template, post_id):
    credentials = user + ':' + password
    token = base64.b64encode(credentials.encode())
    header = {'Authorization': 'Basic ' + token.decode('utf-8'), 'Content-Type': 'application/json'}

    # Ensure row_values is a list with enough elements

    company_name = row_values[0]
    description = row_values[2]
    complete_address = row_values[3]
    company_website = row_values[4]
    company_phone_number = row_values[5]
    contact_email = row_values[6]
    company_hours_raw = row_values[7]
    company_logo_url = row_values[8]
    google_map_src = row_values[9]
    target_location = row_values[10]
    services_offered = row_values[11]
    gallery_image_urls = row_values[12]
    youtube_video_url = convert_to_embed_url(row_values[13])
    linkedin_url = row_values[14]
    facebook_url = row_values[15]
    twitter_url = row_values[16]
    youtube_url = row_values[17]
    new_username = row_values[18]
    user_email = row_values[19]
    user_password = row_values[20]



    print(youtube_url)
    # Processing company hours
    company_hours = company_hours_raw.split('\n') if company_hours_raw else []
    hours_html = "".join(f"<span><i class='fas fa-clock'></i> {day}</span><br>" for day in company_hours)
    # Processing gallery images
    galleries = ""
    if gallery_image_urls:
        url_list = [url.strip() for url in gallery_image_urls.split(',')]
        gallery_images_html = "".join([f'<img src="{url}" alt="Photo {index + 1}">' for index, url in enumerate(url_list)])
        galleries = f"""<div class="company-info">
            <h2>Our Gallery</h2>
            <div class="gallery">{gallery_images_html}</div>
          </div>"""

    if youtube_video_url:
        youtube_template_1 = f"""<div class="company-info">
            <h2>Watch Our Video</h2>
            <iframe src="{youtube_video_url}" style="width: 65%; height: 400px;" allowfullscreen></iframe>
          </div>"""
    else:
      youtube_template_1 = ""


    linkedin_link_html_1 = ""
    facebook_link_html_1 = ""
    twitter_link_html_1 = ""
    youtube_link_html_1 = ""

    if linkedin_url:
        linkedin_link_html_1 = f"""<a href="{linkedin_url}" target="_blank" rel="noopener"><i class="fab fa-linkedin-in"></i></a>"""
    else:
        linkedin_link_html_1 = ""
    if facebook_url:
        facebook_link_html_1 = f"""<a href="{facebook_url}" target="_blank" rel="noopener"><i class="fab fa-facebook-f"></i></a>"""
    else:
        facebook_link_html_1= ""
    if twitter_url:
        twitter_link_html_1 = f"""<a href="{twitter_url}" target="_blank" rel="noopener"><i class="fab fa-twitter"></i></a>"""
    else:
        twitter_link_html_1 = ""
    if youtube_url:
        youtube_link_html_1 = f"""<a href="{youtube_url}" target="_blank" rel="noopener"><i class="fab fa-youtube"></i></a>"""
    else:
        youtube_link_html_1 = ""

    if not (linkedin_url or facebook_url or twitter_url or youtube_url):
        social_template_1 = ""
    else:
        social_template_1 = f"""<div class="company-info">
            <h2>Connect With Us</h2>
            <div class="social-media">
             {linkedin_link_html_1}
             {facebook_link_html_1}
             {twitter_link_html_1}
             {youtube_link_html_1}
            </div>
          </div>"""
        
    # Constructing the HTML content
    html_1 = f"""<!-- wp:html --><div class="container">
          <div class="company-profile-header">
            <img src="{company_logo_url}" alt="Company Logo">
          </div>
          <div class="info-and-map">
            <div class="info-block">
            <div class="highlight">
              <h2>About the Company</h2>
                <p>{description}</p>
              </div>
              <div class="highlight">
                <h2>Opening Hours</h2>
                <p>{hours_html}</p>
              </div>
            </div>
            <div class="map-container">
              <h2>Contact Information</h2>
                <p><i class="fas fa-map-marker-alt"></i> Address: {complete_address}</p>
                <p><i class="fas fa-globe"></i> Website: <a href="{company_website}" target="_blank">{company_website}</a></p>
                <p><i class="fas fa-phone"></i> Phone: <a href="tel:{company_phone_number}">{company_phone_number}</a></p>
                <p><i class="fas fa-envelope"></i> Email: <a href="mailto:{contact_email}">{contact_email}</a></p>
              <h2>Find Us On The Map</h2>
              {google_map_src}
            </div>
          </div>
         <div class="highlight">
            <h2>Brands/Services Offered</h2>
            <p>{services_offered}</p>
          </div>
            {galleries}

         {youtube_template_1}
        {social_template_1}
          

        </div><!-- /wp:html -->"""
    
        
    galleries_2 = ""
    img_list = ""  # Initialize img_list here

    if gallery_image_urls:
        url_list = [url.strip() for url in gallery_image_urls.split(',')]
        for i, url in enumerate(url_list, start=1):
            img_list += f'<div class="gallery-item"><img src="{url}" alt="Gallery Image {i}"></div>\n'

    galleries_2 = f'<section id="gallerySection" class="gallery-section"><h2 class="feature-title">Gallery</h2><div class="gallery-content">{img_list}</div></section>'

   # Initialize an empty string to store the HTML code
    social_media_buttons = ""

    # Check if each URL has a value and generate the corresponding HTML
    print("LInkedin URL:", linkedin_url)
    if linkedin_url:
        social_media_buttons += f'''
          <!-- LinkedIn -->
          <a title="LinkedIn" class="button-social has-action" href="{linkedin_url}" target="_blank">
            <i class="fab fa-linkedin-in"></i>
          </a>
        '''

    if facebook_url:
        social_media_buttons += f'''
          <!-- Facebook -->
          <a title="Facebook" class="button-social has-action" href="{facebook_url}" target="_blank">
            <i class="fab fa-facebook-f"></i>
          </a>
        '''

    if twitter_url:
        social_media_buttons += f'''
          <!-- Twitter -->
          <a title="Twitter" class="button-social has-action" href="{twitter_url}" target="_blank">
            <i class="fab fa-twitter"></i>
          </a>
        '''

    if youtube_url:
        social_media_buttons += f'''
          <!-- YouTube -->
          <a title="YouTube" class="button-social has-action" href="{youtube_url}" target="_blank">
           <i class="fab fa-youtube"></i>
          </a>
        '''

    # Check if any social media buttons were generated
    if social_media_buttons:
        # Create the enclosing <div> for the buttons
        social_media_buttons = f'<section class="section-wrap" id="socialMediaLinks"><h2 class="feature-title">Digital & Online Presence</h2><div class="social-presence"><ul><li class="social-action"><div class="btn-group">\n{social_media_buttons}\n</div></li></ul></div></section>'
    
    hours_html_2 = "".join(f"<span><i class='fas fa-clock'></i> {day}</span>" for day in company_hours)

    if youtube_video_url:
        youtube_template_2 = f"""<!-- YouTube Video Embed Section -->
    <div id="youtubeVideoSection" class="youtube-video-section">
        <h2 class="feature-title">Our YouTube Video</h2>
        <div class="youtube-video-embed">
            <iframe width="560" height="315" src="{youtube_video_url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
        </div>
    </div>"""
    else:
        youtube_template_2 = ""

    html_2 = f"""<!-- wp:html --><div class="business-profile">
    <div class="navigation-menu">
      <div class="menu-links">
        <a href="#companyOverview" class="link-item active">About Company</a>
        <a href="#gallerySection" class="link-item">Gallery</a>
        <a href="#socialMediaLinks" class="link-item">Social Media</a>
      </div>
    </div>

    <div id="companyOverview" class="profile-overview">
        <div class="overview-content">
          <h2 class="section-title">Business Overview</h2>
          <div class="business-description">
            <p>
              {description}
            </p>
          </div>
          <div class="services-offered">
            <h3 class="services-title">Services offered</h3>
            <span>{services_offered}</span>
          </div>

          <div class="additional-info">
            <div class="info-item">
              <h3>Company Website</h3>
              <p><a href="{company_website}">{company_website}</a></p>
            </div>
            <div class="info-item">
              <h3>Company Phone Number</h3>
              <p><a href="tel:{company_phone_number}">{company_phone_number}</a></p>
            </div>
            <div class="info-item">
              <h3>Company Email</h3>
              <p><a href="mailto:{contact_email}">{contact_email}</a></p>
            </div>
            <div class="info-item">
              <h3>Address</h3>
              <p>{complete_address}</p>
            </div>
          </div>
        </div>
    </div>

    <!-- Opening Hours Section -->
    <div class="opening-hours">
        <div class="hours-content">
            <h2 class="section-title">Opening Hours</h2>
            <div class="hours-list">
                {hours_html_2}
            </div>
        </div>
    </div>

    {galleries_2}

    {youtube_template_2}

    <div id="mapsection" class="map-location-section">
        <h2 class="feature-title">Find Us On Map</h2>
        <div class="google-maps-embed">
            {google_map_src}
        </div>
    </div>

    {social_media_buttons} 
</div>
<!-- /wp:html -->"""
    
    html_img_tags = ""
    # Split the URLs and remove any leading/trailing whitespace
    url_list = [url.strip() for url in gallery_image_urls.split(',')]

    # Iterate over the image URLs and create HTML img tags
    for i, url in enumerate(url_list, start=1):
        html_img_tags += f'<img decoding="async" src="{url}" alt="Photo {i}">\n'



    # Generate the HTML for each image
    gallery_images_html_3 = "".join([
        f'<img decoding="async" src="{url}" alt="Gallery image {index + 1}">'
        for index, url in enumerate(url_list)
    ])


    if facebook_url:
        facebook_link_html_3 = f"""<a title="Facebook" class="button-social has-action" href="{facebook_url}" target="_blank">
              <i class="fab fa-facebook-f"></i></a>"""
    else:
        facebook_link_html_3 = ""
        
    if youtube_url:
        youtube_link_html_3 = f"""<a title="YouTube" class="button-social has-action" href="{youtube_url}" target="_blank">
              <i class="fab fa-youtube"></i></a>"""
    else:
        youtube_link_html_3 = ""
                  
    # Check if linkedin_url is not empty
    if linkedin_url:
        linkedin_link_html_3 = f"""<a title="LinkedIn" class="button-social has-action" href="{linkedin_url}" target="_blank">
              <i class="fab fa-linkedin"></i></a>"""
    else:
        linkedin_link_html_3 = ""

    # Check if twitter_url is not empty
    if twitter_url:
        twitter_link_html_3 = f"""<a title="Twitter" class="button-social has-action" href="{twitter_url}" target="_blank">
              <i class="fa fa-twitter"></i></a>"""  # Note: Change 'fa fa-times' to 'fa fa-twitter'
    else:
        twitter_link_html_3 = ""

    if youtube_video_url:
        youtube_template_3 = f"""<div><ul class="nav nav-tabs" id="myTab" role="tablist">
            <li class="nav-item" role="presentation">
              <button class="nav-link active" id="youtube-tab" data-bs-toggle="tab" data-bs-target="#youtube" type="button" role="tab" aria-controls="gallery" aria-selected="false">Youtube</button>
      </li>
    </ul>
    </div>
    <div class="tab-content" id="myTabContentYoutube">
      <div class="tab-pane fade show active" id="youtube" role="tabpanel" aria-labelledby="youtube-tab">
          <div class="youtube-embed">
            <iframe width="100%" height="auto" src="{youtube_video_url}" frameborder="0" allowfullscreen></iframe>
          </div>
      </div>
  </div>"""
    else:
        youtube_template_3 = ""

    html_3 = f"""<!-- wp:html --><div class="profile-box">
    <div class="container">
    <div class="row">
    <div class="col-12 col-lg-12 col-xl-9 float-left">
      <div class="dc-docsingle-header">
        <figure class="dc-docsingleimg">
        <img class="dc-ava-detail entered lazyloaded" src="{company_logo_url}" alt="Stuart Gordon" data-lazy-src="https://doctortoyou.b-cdn.net/wp-content/themes/doctreat/images/dravatar-255x250.jpg" data-ll-status="loaded"><noscript><img class="dc-ava-detail" src="https://doctortoyou.b-cdn.net/wp-content/themes/doctreat/images/dravatar-255x250.jpg" alt="Stuart Gordon"></noscript>
        <img class="dc-ava-detail-2x" src="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%200%200'%3E%3C/svg%3E" alt="Stuart Gordon" data-lazy-src="https://doctortoyou.b-cdn.net/wp-content/themes/doctreat/images/dravatar-545x428.jpg"><noscript><img class="dc-ava-detail-2x" src="https://doctortoyou.b-cdn.net/wp-content/themes/doctreat/images/dravatar-545x428.jpg" alt="Stuart Gordon"></noscript>
    
            </figure>
      <div class="dc-docsingle-content">
      <div class="dc-title">
                    <h2><a href="{company_website}" data-wpel-link="internal">{company_name}</a>
            <i class="far fa-check-circle dc-awardtooltip dc-tipso tipso_style" data-tipso="Verified user"></i>
              </h2>
    
      </div>
            <div class="rd-description">
          <p>{description}</p>
        </div>
    
    </div>
    </div>
    <div>
      <ul class="nav nav-tabs" id="myTab" role="tablist">
        <li class="nav-item" role="presentation">
          <button class="nav-link active" id="services-tab" data-bs-toggle="tab" data-bs-target="#services" type="button" role="tab" aria-controls="services" aria-selected="true">Offered Services</button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="social-tab" data-bs-toggle="tab" data-bs-target="#social" type="button" role="tab" aria-controls="social" aria-selected="false">Social Presence</button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="opening-tab" data-bs-toggle="tab" data-bs-target="#opening" type="button" role="tab" aria-controls="opening" aria-selected="false">Opening Hours</button>
        </li>
    </ul>
    </div>
          
    <div class="tab-content" id="myTabContent">
      <div class="tab-pane fade show active" id="services" role="tabpanel" aria-labelledby="services-tab">
       {services_offered}
      </div>
    
        <div class="tab-pane fade" id="social" role="tabpanel" aria-labelledby="social-tab">
              <div class="btn-group">
              {facebook_link_html_3}
              {youtube_link_html_3}
              {linkedin_link_html_3}
              {twitter_link_html_3}
          </div>
            </div>
        <div class="tab-pane fade" id="opening" role="tabpanel" aria-labelledby="opening-tab">
           <p>{hours_html}</p>
        </div>           
          </div>
          <div>
          <ul class="nav nav-tabs" id="myTab" role="tablist">
              <li class="nav-item" role="presentation">
                <button class="nav-link active" id="contact-tab" data-bs-toggle="tab" data-bs-target="#contact" type="button" role="tab" aria-controls="contact" aria-selected="false">Contact Details</button>
              </li>
          </ul>
          </div>
    <div class="tab-content" id="myTabContent">
      <div class="tab-pane fade show active" id="contact" role="tabpanel" aria-labelledby="contact-tab">
    <p><i class="fas fa-globe"></i> Website: <a href="{company_website}" target="_blank" rel="noopener">{company_website}</a></p>
          <p><i class="fas fa-phone"></i> Phone: <a href="tel:{company_phone_number}">{company_phone_number}</a></p>
          <p><i class="fas fa-envelope"></i> Email: <a href="mailto:{contact_email}">{contact_email}</a></p>
        </div>
    </div>
    <div><ul class="nav nav-tabs" id="myTab" role="tablist">
            <li class="nav-item" role="presentation">
              <button class="nav-link active" id="gallery-tab" data-bs-toggle="tab" data-bs-target="#gallery" type="button" role="tab" aria-controls="gallery" aria-selected="false">Gallery</button>
            </li>
    </ul>
    </div>
    <div class="tab-content" id="myTabContent">
            <div class="tab-pane fade show active" id="gallery" role="tabpanel" aria-labelledby="gallery-tab">
              <div class="gallery">
                {gallery_images_html_3}
              </div>
            </div>  
          </div>
    {youtube_template_3}            
    </div>
    <div class="col-12 col-md-6 col-lg-6 col-xl-3 float-left">
      <aside id="dc-sidebar" class="dc-sidebar dc-sidebar-grid float-left mt-xl-0">
        <div class="map-container">
           {google_map_src}
      </div>							
    <div class="dc-contactinfobox dc-locationbox">
                <ul class="dc-contactinfo">
                    <li class="dcuser-location">
                    <i class="lnr lnr-location"></i>
                        {complete_address}
                    </li>
                        <li class="dcuser-screen">
                        <i class="lnr lnr-screen"></i>
                        <span><a href="{company_website}" target="_blank" data-wpel-link="external" rel="external noopener noreferrer">{company_website}</a></span>
                    </li>                        
                    </ul>
    </div>
        
    </aside>
    </div>
    </div>
    </div>
    </div><!-- /wp:html -->"""

    if html_template == 1:
        final_content = html_1
    elif html_template == 2:
        final_content = html_2
    elif html_template == 3:
        final_content = html_3
        

    post_data = {
      'title': company_name,
      'status': 'publish',
      'content': final_content
             }   


    # Send the update request (PUT instead of POST)
    response = requests.put(json_url, headers=header, json=post_data)

     # Handle the response
    if response.status_code == 200:
        print("Post updated successfully.")
        post_link = response.json().get('link')
        return 'success', f"Post updated successfully. Post link: {post_link}"
    else:
        print("Failed to update post.")
        print(response.text)
        return 'error', f"Failed to update post. Error: {response.text}"
      
      
def post_summary_to_wordpress(post_title, description, live_urls):
    try:
        # Randomly picking a random APIConfig with site_enable=True
        api_config = APIConfig.objects.filter(site_enable=True).order_by('?').first()
        if not api_config:
            logger.error("No enabled WordPress sites available for posting.")
            return None  # Return None if no WordPress site is available
        print(live_urls)
        # Construct the content
        # title = f"Here are Top Citations for {company_name}"
        url_list = "\n".join([f'<li><a href="{url}">{get_root_domain(url)}</a></li>' for url in live_urls])
        
        print("URL List:", url_list)
        content = f"""
            <p>{description}</p>
            <p>Top Citations::</p>
            <ul>
                {url_list}
            </ul>
        """
        print(content)

        # Prepare the JSON payload for posting
        json_url = f"https://{api_config.website.rstrip('/')}/wp-json/wp/v2/posts"
        payload = {
            "title": post_title,
            "content": content,
            "status": "publish",
        }

        # Make the POST request
        response = requests.post(
            json_url,
            json=payload,
            auth=(api_config.user, api_config.password),
        )

        if response.status_code == 201:  # Post created successfully
            logger.info(f"Summary post created on {api_config.website}")
            # Extract the published post URL from the response
            post_data = response.json()
            post_url = post_data.get('link')  # The link to the published post
            return post_url  # Return the URL of the published post
        else:
            logger.error(f"Failed to create summary post. Response: {response.text}")
            return None  # Return None if the post creation fails

    except Exception as e:
        logger.error(f"Error posting summary to WordPress: {e}", exc_info=True)
        return None  # Return None in case of an error


      
