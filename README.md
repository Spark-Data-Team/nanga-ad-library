# Nanga Ad Library

__With [Nanga](https://app.nanga.tech/), stay ahead of the competition, maximize your ROI, and build a more credible, effective advertising 
strategy !__

Ad libraries are game-changer for advertisers, offering a wealth of strategic advantages:  
1) It allows you to track competitor campaigns in real-time, helping you understand which creatives, targeting 
strategies, and ad formats are driving results in your industry.  
2) By seeing detailed performance data like budgets, reach, and demographics, you can optimize your own ads with 
proven data-backed insights.

And today, __Nanga Ad Library__ is gathering for you all Ad Libraries from the main social media platforms in 
one place !


## Table of Contents

1. [Introduction](#introduction)
2. [Roadmap](#roadmap)
3. [Usage](#usage)
4. [Contributing](#contributing)
5. [License](#license)
6. [Acknowledgements](#acknowledgements)

## Introduction

The European regulation that requires social media platforms to make their advertising libraries publicly available is 
part of the Digital Services Act (DSA), which entered into force on August 25, 2023. This regulation is designed to 
enhance transparency and accountability across digital platforms. The DSA mandates that large platforms, such as social
media networks and search engines, disclose their advertising practices, including providing access to data on the
targeting of ads and the related algorithms.

The purpose of the DSA is to combat harmful content, enhance user safety, and ensure that platforms disclose details
about how ads are shown, particularly those based on user profiles. These transparency requirements also aim to give
researchers and the public access to this information, facilitating better oversight. Platforms such as Facebook, 
Google, and others with over 45 million active users are expected to follow these new rules, including publishing 
details about political ads, the algorithms used for targeting, and the effectiveness of these ads.

The regulations are enforced by the European Commission, and platforms that fail to comply face significant penalties,
including fines of up to 6% of their global revenue.

[Learn more about the Digital Services Act (DSA)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32022R2065).

The DSA regulation forced the main social advertising platforms to provide public access to their ad library and the 
Nanga Ad Library is gathering them all for you.

## Roadmap

New advertising platforms will soon be available in the Nanga Ad Library:
- [X] __January 2025__: [Facebook Ad Library](https://www.facebook.com/ads/library)
- [ ] __Q1 2025__: [Tiktok Ad Library](https://library.tiktok.com/ads)
- [ ] __Q1 2025__: [Google Ad Library](https://adstransparency.google.com)
- [ ] __Q1 2025__: [Microsoft Ad Library](https://adlibrary.ads.microsoft.com)
- [ ] __Q2 2025__: [Twitter Ad Library](https://ads.twitter.com/ads-repository)
- [ ] __Q2 2025__: [Apple Search Ad Library](https://adrepository.apple.com)
- [ ] __Q2 2025__: [LinkedIn Ad Library](https://www.linkedin.com/ad-library/home)

## Installation

You can install this package directly from PyPI using `pip`:
```bash
pip install nanga-ad-library --upgrade
playwright install --with-deps
```

These commands will automatically download and install all required dependencies.

## Usage

### Prepare Ad Library for each platform

How to set up your Ad Library app ?
- [Meta](https://www.facebook.com/ads/library/api/)

### Use the package locally

#### Installation

You can install this package and all required dependencies directly from PyPI using `pip`:
```bash
pip install nanga-ad-library --upgrade
```

To be able to download ads elements, you'll have to download [playwright](https://playwright.dev/python/) browsers:
```bash
playwright install --with-deps
```

#### Extract data from Ad Library

Try to extract some results from the Nanga Ad Library API:
```python
from nanga_ad_library import NangaAdLibrary

# Prepare the arguments to send to initiate the API
init_hash = {}

# Prepare connection hash depending on the platform to use (here is an example for Meta):
platform = "meta"
if platform == "meta":
    connection_hash = {
        "access_token": "{meta_access_token}"
    }
else:
    connection_hash = {}
init_hash.update(connection_hash)

# Prepare query hash (here is an example for Meta):
query_hash = {
    "payload": {
        "ad_active_status": "ACTIVE",
        "search_terms": "Facebook",
        "ad_reached_countries": ["FR"],
        "fields": [
            "id",
            "page_id",
            "ad_creation_time",
            "ad_delivery_start_time",
            "ad_delivery_stop_time",
            "ad_snapshot_url"
        ]
    }
}
init_hash.update(query_hash)

# Choose if ads elements will be downloaded (Title, Body, Description, Image or Video, Call to action).
# You can also provide download_start_date and download_end_date to retrieve ad_elements only for ads created 
# during this date range (both fields are optional).
download_hash = {
    "download_ads": True,
    "download_start_date": "2025-01-01",
    "download_end_date": "2025-01-25"
}
init_hash.update(download_hash)

# Initiating library
library = NangaAdLibrary.init(platform=platform, **init_hash)

# Extract the first results from the Ad Library API
results = library.get_results()
```
__Note:__ please replace the {access_token} tag with valid tokens:
- Meta Ad Library: replace'{meta_access_token}' with your [Facebook Developer access token](https://developers.facebook.com/tools/accesstoken/)

### Deploy the package on the cloud
-- More to come

### Use the package in a Jupyter Notebook
-- More to come

## Contributing

Contributions are not yet available for members outside the Nanga project.

## License

This project is licensed under the GNU general public License - see the [LICENSE](https://github.com/Spark-Data-Team/nanga-ad-library/blob/main/LICENSE) file for details.

## Acknowledgements

- [Meta Business SDK](https://github.com/facebook/facebook-python-business-sdk) was a great inspiration for this work. 
