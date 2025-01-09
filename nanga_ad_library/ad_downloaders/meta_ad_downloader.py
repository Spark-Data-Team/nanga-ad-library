import asyncio
import subprocess
import re

from urllib.parse import unquote

from playwright._impl._driver import compute_driver_executable, get_driver_env
from playwright.async_api import async_playwright

"""
Define MetaAdDownloader class to retrieve ad elements using Playwright.
"""


class MetaRequestInterceptor:
    """
    A class designed to passively intercept network requests from the Meta Ad Library preview while downloading
      ad elements (Title, Body, Description, Image url, Video url and Call to action).
    It blocks direct video requests (to avoid detection) and captures video and image URLs instead.
    These URLs are stored for extracting video links and thumbnails (in __intercepted_videos & __intercepted_images),
      enabling a bypass of Meta's anti-scraping measures.
    """

    def __init__(self, verbose):
        self.__verbose = verbose
        self.__intercepted_videos = []
        self.__intercepted_images = []

    async def intercept(self, route, request):
        # Intercept video requests
        if "video" in request.url:
            await route.abort()
            if self.__verbose:
                print(f"Video request blocked: {request.url}")
            # Store video
            self.__intercepted_videos.append(request.url)

        # Intercept image requests
        elif "scontent" in request.url:
            await route.continue_()
            if self.__verbose:
                print(f"Image request passed: {request.url}")
            # Store image
            self.__intercepted_images.append(request.url)

        else:
            await route.continue_()
            if self.__verbose:
                print(f"Other request passed: {request.url}")

    def get_videos(self):
        return self.__intercepted_videos

    def get_images(self):
        return self.__intercepted_images


class MetaAdDownloader:
    """
    A class instancing a scraper to retrieve elements from Meta Ad Library previews:
      Body, Title*, Image*, Video*, Description*, Landing page*, CTA caption*
      - "*" tagged elements are retrieved for each creative visual (1 for statics, several for carousels)
    """

    # Store the field used to store the Meta Ad Library preview url (specific to Meta)
    PREVIEW_FIELD = "ad_snapshot_url"

    def __init__(self, verbose=False):
        self.__verbose = verbose or False

    @classmethod
    def init(cls, **kwargs):
        """
        Process the provided payload and create a MetaAdDownloader object if everything is fine

        Returns:
            A new MetaAdDownloader object
        """

        # Initiate a playwright downloader
        ad_downloader = cls(kwargs.get("verbose"))

        # Install chromium browser with all dependencies
        ad_downloader.__install_chromium_browser_async(with_deps=True)

        return ad_downloader

    def __install_chromium_browser_async(self, with_deps=True):
        """ [Hidden method]
        Install Playwright chromium browser (async)

        Args:
            with_deps (bool, optional): Whether deps have to be installed too.
        """

        # Install cmd arguments
        driver_executable, driver_cli = compute_driver_executable()
        args = [driver_executable, driver_cli, "install", "chromium", "--async"]

        # Update args if we need to install deps
        if with_deps:
            args.append("--with-deps")

        # Launch install cmd
        proc = subprocess.run(args, env=get_driver_env(), capture_output=True, text=True, check=False)  # noqa: S603
        if self.__verbose:
            print(
                "Playwright chromium browser successfully installed." if proc
                else "Failed to install Playwright chromium browser."
            )

    async def download_from_new_batch(self, ad_library_batch):
        """
        Use parallelized calls to download ad elements for each row of a batch

        Args:
            ad_library_batch: A list of records from a ResponseCursor object.

        Returns:
             The updated batch with new key "ad_elements".
        """

        async with async_playwright() as p:
            # Initiate playwright browser and use it for the whole batch
            browser = await p.chromium.launch()

            # Download ad elements (parallel calls)
            updated_batch = await asyncio.gather(
                *(self.__download_ad_elements(browser, ad_payload) for ad_payload in ad_library_batch)
            )

            # Close browser
            await browser.close()

        return updated_batch

    async def __download_ad_elements(self, browser, ad_payload):
        """ [Hidden method]
        Use scraping to extract all ad elements from the ad preview url.

        Args:
            browser: A playwright browser.
            ad_payload: The ad payload (response from Ad Library API).

        Returns:
            A dict with the downloaded ad elements.
        """

        # Extract preview url from ad payload
        preview = ad_payload.get(self.PREVIEW_FIELD)

        # Prepare payload to return
        ad_elements = {
            "body": None,
            "type": None,
            "carousel": []
        }

        # Initiate request interceptor
        interceptor = MetaRequestInterceptor(self.__verbose)

        # Initiate new playwright page
        page = await browser.new_page()

        # Activate page requests interception
        await page.route("**/*", interceptor.intercept)

        # Open Ad Library card and wait until all requests are finished / Increase nav timeout to 5 minutes.
        await page.goto(preview, timeout=300000)
        await page.wait_for_load_state("networkidle")

        # Deduplicate blocked videos
        blocked_videos = list(set(interceptor.get_videos()))

        # Store thumbnails from blocked videos
        page_images_locator, page_images = await page.locator("img").all(), []
        if page_images_locator:
            page_images = [await image.get_attribute("src") for image in page_images_locator]
        blocked_videos_thumbnails = list(set([image for image in interceptor.get_images() if image not in page_images]))

        # Get Body
        body_locator = await page.locator("""//*[@id="content"]/div/div/div/div/div/div/div[2]/div[1]""").all()
        if body_locator:
            ad_elements["body"] = await body_locator[0].inner_text()

        # Deal with Carousels (several creatives in the ad)
        carousel_path = """//*[@id="content"]/div/div/div/div/div/div/div[3]/div/div[2]/div/div/div"""
        carousel_locator = await page.locator(carousel_path).all()
        if carousel_locator:
            ad_elements["type"] = "carousel"
            for k in range(len(carousel_locator)):
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
                creative_path = f"""{carousel_path}[{k + 1}]/div/div"""
                # Image
                image_locator = await page.locator(f"""{creative_path}/a/div[1]/img""").all()
                if image_locator:
                    links_path = creative_path + "/a"
                    captions_path = links_path + "/div[2]"
                    creative["image"] = await image_locator[0].get_attribute("src")
                # Video
                video_locator = await page.locator(f"""{creative_path}/div[1]/div/div/div/div/video""").all()
                if video_locator:
                    links_path = creative_path + "/div[2]/a"
                    captions_path = links_path + "/div"
                    creative["image"] = await image_locator[0].get_attribute("playsinline poster")
                    creative["video"] = await image_locator[0].get_attribute("src")
                # Undetected video or empty
                if not (image_locator or video_locator):
                    if blocked_videos:
                        links_path = creative_path + "/div[2]/a"
                        captions_path = links_path + "/div"
                        creative["video"] = blocked_videos.pop(0)
                        if blocked_videos_thumbnails:
                            creative["image"] = blocked_videos_thumbnails.pop(0)
                    else:
                        links_path = creative_path + "/a"
                        captions_path = links_path + "/div[2]"
                # Landing page
                landing_page_locator = await page.locator(links_path).all()
                if landing_page_locator:
                    creative["landing_page"] = await landing_page_locator[0].get_attribute("href")
                # Call to action
                cta_locator = await page.locator(f"""{captions_path}/div[2]/div/div/span/div/div/div""").all()
                if cta_locator:
                    creative["cta"] = await cta_locator[0].inner_html()
                # Caption
                caption_locator = await page.locator(f"""{captions_path}/div[1]/div[1]/div/div""").all()
                if caption_locator:
                    creative["caption"] = await caption_locator[0].inner_html()
                # Title
                title_locator = await page.locator(f"""{captions_path}/div[1]/div[2]/div/div""").all()
                if title_locator:
                    creative["title"] = await title_locator[0].inner_html()
                # Description
                description_locator = await page.locator(f"""{captions_path}/div[1]/div[3]/div/div""").all()
                if description_locator:
                    creative["description"] = await description_locator[0].inner_html()
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
            creative_path = f"""//*[@id="content"]/div/div/div/div/div/div/div[2]"""
            # Image
            image_locator = await page.locator(f"""{creative_path}/a/div[1]/img""").all()
            if image_locator:
                ad_elements["type"] = "image"
                links_path = creative_path + "/a"
                captions_path = links_path + "/div[2]"
                creative["image"] = await image_locator[0].get_attribute("src")
            # Video
            video_locator = await page.locator(f"""{creative_path}/div[2]/div/div/div/div/video""").all()
            if video_locator:
                ad_elements["type"] = "video"
                links_path = creative_path + "/div[3]/a"
                captions_path = links_path + "/div"
                creative["image"] = await image_locator[0].get_attribute("playsinline poster")
                creative["video"] = await image_locator[0].get_attribute("src")
            # Undetected video or empty
            if not (image_locator or video_locator):
                if blocked_videos:
                    ad_elements["type"] = "video"
                    links_path = creative_path + "/div[3]/a"
                    captions_path = links_path + "/div"
                    creative["video"] = blocked_videos.pop(0)
                    if blocked_videos_thumbnails:
                        creative["image"] = blocked_videos_thumbnails.pop(0)
                else:
                    ad_elements["type"] = "status"
                    links_path = creative_path + "/a"
                    captions_path = links_path + "/div[2]"
            # Landing page
            landing_page_locator = await page.locator(links_path).all()
            if landing_page_locator:
                creative["landing_page"] = await landing_page_locator[0].get_attribute("href")
            # Call to action
            cta_locator = await page.locator(f"""{captions_path}/div[2]/div/div/span/div/div/div""").all()
            if cta_locator:
                creative["cta"] = await cta_locator[0].inner_html()
            # Caption
            caption_locator = await page.locator(f"""{captions_path}/div[1]/div[1]/div/div""").all()
            if caption_locator:
                creative["caption"] = await caption_locator[0].inner_html()
            # Title
            title_locator = await page.locator(f"""{captions_path}/div[1]/div[2]/div/div""").all()
            if title_locator:
                creative["title"] = await title_locator[0].inner_html()
            # Description
            description_locator = await page.locator(f"""{captions_path}/div[1]/div[3]/div/div""").all()
            if description_locator:
                creative["description"] = await description_locator[0].inner_html()
            # Add to list
            ad_elements["carousel"].append(creative)

        # Close used browser page
        await page.close()

        # Update payload
        ad_payload.update({"ad_elements": ad_elements})

        return ad_payload

    @staticmethod
    def __extract_lp_from_meta_url(url):
        """

        Args:
            url: The url extracted from the Meta Ad Library preview

        Returns:
            The raw landing page that was "embedded" in the Meta URL.
                We remove utms (all elements after "?" in the landing page).
        """

        # Identify meta embedding url pattern
        pattern = re.compile("https://l\.facebook\.com/l\.php\?u=([^&]+)&.")

        # Search if the url passed as arg matchs the pattern
        match = re.match(pattern, url)
        if match:
            # Extract the URL encoded
            encoded_landing_page = match.group(1)

            # Decode the landing page
            landing_page = unquote(encoded_landing_page)

        else:
            landing_page = url

        # Remove the parametric part of the url
        landing_page = landing_page.split("?")[0]

        return landing_page
