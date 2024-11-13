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
2. [Installation](#installation)
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

[Learn more about the Digital Services Act (DSA)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32022R2065)

The Nanga Ad Library SDK allows you to query the ad library of several social media platforms.
You only need to provide access tokens for each platform, and you'll be able to retrieve rich data about

## Installation

You can install this package directly from PyPI using `pip`:
```bash
pip install nanga_ad_library
```

This command will automatically download and install all required dependencies.  

### Updating

To update the package to the latest version, use:
```bash
pip install --upgrade nanga_ad_library
```

### Verifying the Installation

To verify that the package was installed correctly, you can try importing the module in Python:
```python
import nanga_ad_library
print(nanga_ad_library.__version__)
```

Ensure the displayed version matches the one you installed.

### Prepare Ad Library for each platform

How to set up your Ad Library app ?
- [Meta](https://www.facebook.com/ads/library/api/)

### Initiate and use the API

Try to extract some results from the Nanga Ad Library API:
```python
from nanga_ad_library import NangaAdLibraryApi

# Prepare the arguments to send to initiate the API
init_hash = {}

# Prepare connection hash depending on the platform to use (here is an example for Meta):
platform = "Meta"
if platform == "Meta":
    connection_hash = {
        "access_token": "{meta_access_token}"
    }
else:
    connection_hash = {}
init_hash.update(connection_hash)

# Prepare query hash (here is an example for Meta):
query_hash = {
    "payload": {
        "search_terms": "Facebook",
        "ad_reached_countries": ["FR"]
    },
    "fields": []
}
init_hash.update(query_hash)

# Initiating api
api = NangaAdLibraryApi.init(platform=platform, **init_hash)

# Extract the first results from the Ad Library API
results = api.get_results()
```
__Note:__ please replace the {access_token} tag with valid tokens:
- Meta Ad Library: replace'{meta_access_token}' with your [Facebook Developer access token](https://developers.facebook.com/tools/accesstoken/)

## Contributing

Contributions are not yet available for members outside the Nanga project.

## License

This project is licensed under the GNU general public License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Meta Business SDK](https://github.com/facebook/facebook-python-business-sdk) was a great inspiration for this work. 
