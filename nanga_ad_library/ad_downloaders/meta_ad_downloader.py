import asyncio
import warnings
import time
import re

from urllib.parse import unquote
from datetime import datetime

from botasaurus.browser import browser, Driver

from nanga_ad_library.utils import *

"""
Define MetaAdDownloader class to retrieve ad elements using Playwright.
"""

class MetaAdDownloader:
    """
    A class instancing a scraper to retrieve elements from Meta Ad Library previews:
      Body, Title*, Image*, Video*, Description*, Landing page*, CTA caption*
      - "*" tagged elements are retrieved for each creative visual (1 for statics, several for carousels)
    """

    # Store the fields used to store (1) the Meta Ad Library preview url and (2) the ad delivery start date
    PREVIEW_FIELD = "ad_snapshot_url"
    DELIVERY_START_DATE_FIELD = "ad_delivery_start_time"
    
    # Store the number of parallel threads to use
    PARALLEL_THREADS = 5

    def __init__(self, start_date=None, end_date=None, verbose=False):
        """
        Initialize the MetaAdDownloader object.

        Args:
            start_date: If not empty: download only ads created after this date,
            end_date: If not empty: download only ads created before this date,
            verbose: Whether to display intermediate logs.
        """

        # Verbose
        self.__verbose = verbose or False

        # Store download start date
        try:
            self.__download_start_date = datetime.strptime(start_date, "%Y-%m-%d")
        except:
            self.__download_start_date = datetime.fromtimestamp(0)
            # Raise a warning if the start_date was given but parsing failed
            if start_date and self.__verbose:
                warnings.warn("Provided start date should match the following format '%Y-%m-%d'.")

        # Store download end date
        try:
            self.__download_end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except:
            self.__download_end_date = datetime.today()
            # Raise a warning if the start_date was given but parsing failed
            if start_date and self.__verbose:
                warnings.warn("Provided end date should match the following format '%Y-%m-%d'.")

        # Whether Meta has spotted our webdriver and blocked it.
        self.__spotted = False


    @classmethod
    def init(cls, **kwargs):
        """
        Process the provided payload and create a MetaAdDownloader object if everything is fine

        Returns:
            A new MetaAdDownloader object
        """

        # Initiate a playwright downloader
        ad_downloader = cls(
            start_date=kwargs.get("download_start_date"),
            end_date=kwargs.get("download_end_date"),
            verbose=kwargs.get("verbose")
        )

        return ad_downloader
    
    def download_from_new_batch(self, ad_library_batch):
        """
        Use sequential calls to download ad elements for each row of a batch

        Args:
            ad_library_batch: A list of records from a ResponseCursor object.

        Returns:
             The updated batch with new key "ad_elements".
        """

        # Download ad_elements 1 by 1 using Botasaurus driver
        updated_batches = []
        while ad_library_batch:
            smaller_batch = ad_library_batch[:self.PARALLEL_THREADS]
            ad_library_batch = ad_library_batch[self.PARALLEL_THREADS:]
            
            # Download ad elements
            updated_batch = self.__download_ads_elements(smaller_batch)
            updated_batches.extend(updated_batch)

        return updated_batches

    def __download_ads_elements(self, ad_payloads):
        """ [Hidden method]
        Use scraping to extract all ad elements from the ad preview url.
        The url used is private (needs our access token).

        Args:
            ad_payloads: The batch of ad_payloads.

        Returns:
            A dict with the downloaded ad elements.
        """
        
        # Prepare template ad_elements hash
        ad_elements = {
            "body": None,
            "type": None,
            "carousel": [],
            "spotted": self.__spotted
        }

        # Prepare list of hashes to send to __botasaurus_scrap_ad_elements
        extraction_array = []
        for ad_payload in ad_payloads:
            # Check that delivery_start_date is between __download_start_date et __download_end_date
            delivery_start_date = datetime.strptime(ad_payload.get(self.DELIVERY_START_DATE_FIELD), "%Y-%m-%d")
            download_needed = (self.__download_start_date <= delivery_start_date <= self.__download_end_date)

            # Make parallel extraction (only if needed and not already spotted)
            if download_needed and not self.__spotted:
                # Extract preview url from ad payload
                extraction_hash = {
                    "preview": ad_payload.get(self.PREVIEW_FIELD),
                    "ad_elements": ad_elements,
                    "ad_payload": ad_payload
                }
                extraction_array.append(extraction_hash)
            else:
                # Extract preview url from ad payload
                extraction_hash = {
                    "preview": None,
                    "ad_elements": ad_elements,
                    "ad_payload": ad_payload
                }
                extraction_array.append(extraction_hash)

        # Update payload
        updated_payloads = self.__botasaurus_scrap_ad_elements(extraction_array)

        # Check if spotted
        self.__spotted = any([payload.get("ad_elements", {}).get("spotted", False) for payload in updated_payloads])

        return updated_payloads
    
    @staticmethod
    @browser(
        parallel=5,
        headless=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        output=None,
        create_error_logs=False,
        close_on_crash=True
    )
    def __botasaurus_scrap_ad_elements(driver: Driver, data):
        """
        Use scraping to extract all ad elements from the ad preview url with Botasaurus (https://github.com/omkarcloud/botasaurus/tree/70a67abcead7b39cba32e947240d30aaafa704b2).
        The url used is private (needs our access token).
        """
        
        # Extract data from provided data
        preview = data.get("preview")
        ad_elements = data.get("ad_elements")
        ad_payload = data.get("ad_payload")

        if preview:
            current_url = preview
            try:
                # Open Ad Library card and wait until all requests are finished / Increase nav timeout to 5 minutes.
                driver.google_get(preview, timeout=300000)

                # Check if Meta redirected us to a login page
                current_url = driver.current_url
                print(current_url)
                if "login" in current_url:
                    ad_elements["spotted"] = True
                    raise Exception(f"Meta detected a non-human behavior and redirected us to '{current_url}'.")

                # Get Body
                try:
                    body_locator = driver.select("""div[id="content"]>div>div>div>div>div>div>div:nth-child(2)>div:nth-child(1)""")
                except:
                    body_locator = None
                if body_locator:
                    # Ensure that it is really the creative body by checking that it contains no image or video
                    only_text = len(body_locator.select_all("img")) == 0 and len(body_locator.select_all("video")) == 0
                    if only_text:
                        ad_elements["body"] = body_locator.text

                # Distinguish between single ads and carousel
                try:
                    carousel_locator = driver.select_all("""div[id="content"]>div>div>div>div>div>div>div:nth-child(3)>div>div:nth-child(2)>div>div>div""")
                except:
                    carousel_locator = None

                # Deal with Carousels (several creatives in the ad)
                if carousel_locator:
                    ad_elements["type"] = "carousel"
                    # Retrieve data from each creative of the carousel
                    for carousel_child in carousel_locator:
                        # Prepare dict
                        creative = {
                            "title": None,
                            "image": None,
                            "video": None,
                            "landing_page": None,
                            "cta": None,
                            "caption": None,
                            "description": None
                        }
                        # Image
                        try:
                            image_locator = carousel_child.select("div>div>img")
                        except:
                            image_locator = None
                        if image_locator:
                            creative["image"] = image_locator.get_attribute("src")
                        # Video
                        try:
                            video_locator = carousel_child.select("div>div>video")
                        except:
                            video_locator = None
                        if video_locator:
                            creative["image"] = video_locator.get_attribute("poster")
                            creative["video"] = video_locator.get_attribute("src")
                        # Landing page
                        try:
                            landing_page_locator = carousel_child.select("div>div>a")
                        except:
                            landing_page_locator = None
                        if landing_page_locator:
                            creative["landing_page"] = extract_lp_from_meta_url(landing_page_locator.get_attribute("href"))
                        # Call to action
                        try:
                            cta_locator = carousel_child.select("div>div>a>div>div:nth-child(2)")
                        except:
                            cta_locator = None
                        if cta_locator:
                            creative["cta"] = cta_locator.text
                        # Caption
                        try:
                            caption_locator = carousel_child.select("div>div>a>div>div:nth-child(1)>div:nth-child(1)")
                        except:
                            caption_locator = None
                        if caption_locator:
                            creative["caption"] = caption_locator.text
                        # Title
                        try:
                            title_locator = carousel_child.select("div>div>a>div>div:nth-child(1)>div:nth-child(2)")
                        except:
                            title_locator = None
                        if title_locator:
                            creative["title"] = title_locator.text
                        # Description
                        try:
                            description_locator = carousel_child.select("div>div>a>div>div:nth-child(1)>div:nth-child(3)")
                        except:
                            description_locator = None
                        if description_locator:
                            creative["description"] = description_locator.text
                        # Add to list
                        ad_elements["carousel"].append(creative)

                # Deal with ads displaying only one creative
                else:
                    # Prepare dict
                    creative = {
                        "title": None,
                        "image": None,
                        "video": None,
                        "landing_page": None,
                        "cta": None,
                        "caption": None,
                        "description": None
                    }

                    # Get creative card
                    try:
                        creative_locator = driver.select("""div[id="content"]>div>div>div>div>div>div>div:nth-child(2)""")
                    except:
                        creative_locator = None

                    if creative_locator:
                        # Image (with title + links)
                        try:
                            image_locator_1 = creative_locator.select("a>img")
                        except:
                            image_locator_1 = None
                        if image_locator_1:
                            links_path = "div:nth-child(2)"
                            creative["image"] = image_locator_1.get_attribute("src")
                        # Image (without title + links)
                        try:
                            image_locator_2 = creative_locator.select("div>img")
                        except:
                            image_locator_2 = None
                        if image_locator_2:
                            links_path = "div:nth-child(2)"
                            creative["image"] = image_locator_2.get_attribute("src")
                        # Video
                        try:
                            video_locator = creative_locator.select("div>video")
                        except:
                            video_locator = None
                        if video_locator:
                            links_path = "div"
                            creative["image"] = video_locator.get_attribute("poster")
                            creative["video"] = video_locator.get_attribute("src")
                        # Landing page
                        try:
                            landing_page_locator = creative_locator.select("a")
                        except:
                            landing_page_locator = None
                        if landing_page_locator:
                            creative["landing_page"] = extract_lp_from_meta_url(landing_page_locator.get_attribute("href"))
                        # Call to action
                        try:
                            cta_locator = creative_locator.select(f"a>{links_path}>div:nth-child(2)")
                        except:
                            cta_locator = None
                        if cta_locator:
                            creative["cta"] = cta_locator.text
                        # Caption
                        try:
                            caption_locator = creative_locator.select(f"a>{links_path}>div:nth-child(1)>div:nth-child(1)")
                        except:
                            caption_locator = None
                        if caption_locator:
                            creative["caption"] = caption_locator.text
                        # Title
                        try:
                            title_locator = creative_locator.select(f"a>{links_path}>div:nth-child(1)>div:nth-child(2)")
                        except:
                            title_locator = None
                        if title_locator:
                            creative["title"] = title_locator.text
                        # Description
                        try:
                            description_locator = creative_locator.select(f"a>{links_path}>div:nth-child(1)>div:nth-child(3)")
                        except:
                            description_locator = None
                        if description_locator:
                            creative["description"] = description_locator.text
                    # Add to list
                    ad_elements["carousel"].append(creative)

            except Exception as e:
                print(f"[ERROR] Scrapping page '{current_url}' failed with error: {e}")

        # Update ad_payload with ad_elements
        ad_payload.update({"ad_elements": ad_elements})

        return ad_payload

"""
Helper methods
"""
def extract_lp_from_meta_url(url):
    """
    Extract the landing page that is embedded in the Facebook URL

    Args:
        url: The url extracted from the Meta Ad Library preview

    Returns:
        The raw landing page that was "embedded" in the Meta URL.
            We remove utms (all elements after "?" in the landing page).
    """

    pattern = re.compile("https://l\.facebook\.com/l\.php\?u=([^&]+)&.")
    match = re.match(pattern, url)
    landing_page = unquote(match.group(1)).split("?")[0] if match else url

    return landing_page

