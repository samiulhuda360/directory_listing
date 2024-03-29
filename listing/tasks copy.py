from celery import shared_task
import requests
import base64
import json
import time
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)



def convert_to_embed_url(youtube_url):
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
def create_company_profile_post(row_values, json_url, user, password, html_template):
    credentials = user + ':' + password
    token = base64.b64encode(credentials.encode())
    header = {'Authorization': 'Basic ' + token.decode('utf-8')}
    # Ensure row_values is a list with enough elements

    company_name = row_values[0]
    description = row_values[1]
    complete_address = row_values[2]
    company_website = row_values[3]
    company_phone_number = row_values[4]
    contact_email = row_values[5]
    company_hours_raw = row_values[6]
    company_logo_url = row_values[7]
    google_map_src = row_values[8]
    target_location = row_values[9]
    services_offered = row_values[10]
    gallery_image_urls = row_values[11]
    youtube_video_url = convert_to_embed_url(row_values[12])
    linkedin_url = row_values[13]
    facebook_url = row_values[14]
    twitter_url = row_values[15]
    youtube_url = row_values[16]
    print(youtube_url)
    # Processing company hours
    company_hours = company_hours_raw.split('\n') if company_hours_raw else []
    hours_html = "".join(f"<span><i class='fas fa-clock'></i> {day}</span>" for day in company_hours)
    # Processing gallery images
    galleries = ""
    if gallery_image_urls:
        url_list = [url.strip() for url in gallery_image_urls.split(',')]
        gallery_images_html = "".join([f'<img src="{url}" alt="Photo {index + 1}">' for index, url in enumerate(url_list)])
        galleries = f"""<div class="company-info">
            <h2>Our Gallery</h2>
            <div class="gallery">{gallery_images_html}</div>
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
                <p><i class="fas fa-phone"></i> Phone: <a href="tel:+19312578004">{company_phone_number}</a></p>
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
          <div class="company-info">
            <h2>Watch Our Video</h2>
            <iframe src="{youtube_video_url}" style="width: 65%; height: 400px;" allowfullscreen></iframe>
          </div>

          <div class="company-info">
            <h2>Connect With Us</h2>
            <div class="social-media">
              <a href="{linkedin_url}" target="_blank" rel="noopener"><i class="fab fa-linkedin-in"></i></a>
              <a href="{facebook_url}" target="_blank" rel="noopener"><i class="fab fa-facebook-f"></i></a>
              <a href="{twitter_url}" target="_blank" rel="noopener"><i class="fab fa-twitter"></i></a>
              <a href="{youtube_url}" target="_blank" rel="noopener"><i class="fab fa-youtube"></i></a>
            </div>
          </div>

        </div><!-- /wp:html -->"""
    
        
    galleries_2 = ""
    img_list = ""  # Initialize img_list here

    if gallery_image_urls:
        url_list = [url.strip() for url in gallery_image_urls.split(',')]
        for i, url in enumerate(url_list, start=1):
            img_list += f'<div class="gallery-item"><img src="{url}" alt="Gallery Image {i}"></div>'

    galleries_2 = f'<section id="gallerySection" class="gallery-section"><h2 class="feature-title">Gallery</h2><div class="gallery-content">{img_list}</div></section>'

   # Initialize an empty string to store the HTML code
    social_media_buttons = ""

    # Check if each URL has a value and generate the corresponding HTML
    print("LInkedin URL:", linkedin_url)
    if linkedin_url:
        social_media_buttons += f'''
          <!-- LinkedIn -->
          <a title="LinkedIn" class="button-social has-action" href="{linkedin_url}" target="_blank">
            <i class="fa fa-linkedin" aria-hidden="true"></i>
          </a>
        '''

    if facebook_url:
        social_media_buttons += f'''
          <!-- Facebook -->
          <a title="Facebook" class="button-social has-action" href="{facebook_url}" target="_blank">
            <i class="fa fa-facebook" aria-hidden="true"></i>
          </a>
        '''

    if twitter_url:
        social_media_buttons += f'''
          <!-- Twitter -->
          <a title="Twitter" class="button-social has-action" href="{twitter_url}" target="_blank">
             <i class="fa fa-times" aria-hidden="true"></i>
          </a>
        '''

    if youtube_url:
        social_media_buttons += f'''
          <!-- YouTube -->
          <a title="YouTube" class="button-social has-action" href="{youtube_url}" target="_blank">
           <i class="fa fa-youtube" aria-hidden="true"></i>
          </a>
        '''

    # Check if any social media buttons were generated
    if social_media_buttons:
        # Create the enclosing <div> for the buttons
        social_media_buttons = f'<section class="section-wrap" id="socialMediaLinks"><h2 class="feature-title">Digital & Online Presence</h2><div class="social-presence"><ul><li class="social-action"><div class="btn-group">\n{social_media_buttons}\n</div></li></ul></div></section>'
    
    
    html_2 = f"""<!-- wp:html --><div class="business-profile">
        <section class="navigation-menu">
          <div class="menu-links">
            <a href="#companyOverview" class="link-item active">About Company</a>
            <a href="#gallerySection" class="link-item">Gallery</a>
            <a href="#socialMediaLinks" class="link-item">Social Media</a>
          </div>
        </section>


          <section id="companyOverview" class="profile-overview">
            <div class="overview-content">
              <h2 class="section-title">Business Overview</h2> <!-- Business Description -->
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
                  <p><a href="{company_phone_number}">{company_phone_number}</a></p>
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
          </section>

          <!-- Opening Hours Section -->
          <section class="opening-hours">
              <div class="hours-content">
                  <h3 class="section-title">Opening Hours</h3>
                  <div class="hours-list">
                      <!-- Insert the generated HTML here -->
                      {hours_html}
                  </div>
              </div>
          </section>
        </section>        
          {galleries_2}

        <!-- YouTube Video Embed Section -->
      <section id="youtubeVideoSection" class="youtube-video-section">
          <h3 class="feature-title">Our YouTube Video</h3>
          <div class="youtube-video-embed">
              <iframe width="560" height="315" src="{youtube_video_url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
          </div>
      </section>       

      <section id="mapsection" class="map-location-section">
          <h3 class="feature-title">Find Us On Map</h3>
          <div class="google-maps-embed">
              {google_map_src}
          </div>
      </section>

        {social_media_buttons} 
              </div><!-- /wp:html -->"""
    
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
        youtube_link_html_3 = f"""<a title="YouTube" class="button-social has-action" href="https://www.youtube.com/channel/UCFjaJZ-sktqV9LJqSSVEwCw" target="_blank">
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
                        <address>{complete_address}</address>
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
        
    print(json_url+'/posts')
    # Preparing the post data
    post = {
        'title': company_name,
        'slug': company_name,
        'status': 'publish',
        'content': final_content,
        # 'categories': 11,   # Uncomment and use as needed
        # 'featured_media': image_id  # Uncomment and use as needed
    }

    # Sending the POST request
    try:
      response = requests.post(json_url + '/posts', headers=header, json=post)
      print(response)
      if response.status_code == 201:
        json_data = response.json()
        draft_post_link = json_data.get('link', None)
        logger.info(f"Task completed successfully with URL: {draft_post_link}")

        return draft_post_link
    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise e



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
    

@shared_task(bind=True)  # bind the task to have self parameter for retry etc.
def perform_test_task(self, config_id):
    try:
        from .models import APIConfig, TestResult  # Import here to avoid circular import
        config = APIConfig.objects.get(id=config_id)
        
        # Mocking the test function behavior
        response = test_post_to_wordpress(config.url, config.user, config.password, "Test Content")
        if response.status_code in [200, 201]:
            response_data = response.json()
            post_id = response_data.get('id')
            delete_response = delete_from_wordpress(config.url, config.user, config.password, post_id)
            
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
