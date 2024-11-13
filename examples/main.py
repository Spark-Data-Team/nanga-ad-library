from nanga_ad_library import NangaAdLibraryApi


def iter_on_results(results, limit):
    count = 0
    for res in results:
        count += 1
        print(res.id, res.ad_snapshot_url)
        if count >= limit:
            break


if __name__ == '__main__':
    """
    A quick introduction to the Nanga Ad Library API with the following example
    """

    # Limit number of result displayed when iterating on .get_results()
    limit_results = 30

    # Prepare the arguments to send to initiate the API
    init_hash = {
        "verbose": True  # Print all important steps to help for debugging.'verbose = False' will run it "silently"
    }

    # Add your personnal tokens here (provided one is expired)
    meta_access_token = "EAACwplIENusBO97zlPpMOZAPrhCHQfAPQLucRZBPU63zZCSeQ4HZANu3OBisZA25S3E97Q5LXhd" \
                        "2BBQJ1RAZB0T3FDnccwBdbYJ7ujWf15IgFYGQDOgTZCSO565uJWTpiyYhs9tbvQr0j5oslNoUn82" \
                        "oliaKpGe9Sf4M8KCc0ZCGoszuuEO6dDGr9ZAPLjCi9Wja4KlcECl0N4WGNramjuy96TriapJ8ZD"
    meta_app_secret = None

    # Prepare connection hash depending on the platform to use (here is an example for Meta):
    platform = "Meta"
    if platform == "Meta":
        connection_hash = {
            "access_token": meta_access_token,
            "app_secret": meta_app_secret
        }
    else:
        connection_hash = {}
    init_hash.update(connection_hash)

    # Prepare query hash (here is an example for Meta):
    query_hash = {
        "payload": {
            "search_terms": "Google",
            "ad_reached_countries": ["FR"],
            "fields": []
        }
    }
    init_hash.update(query_hash)

    print("\n~~~~~~ Initiating api ~~~~~~\n")
    api = NangaAdLibraryApi.init(platform=platform, **init_hash)

    print("\n~~~~ Focusing on Google FR ~~~~\n")
    results_google = api.get_results()

    print("\n~~~~ Focusing on Microsoft GB ~~~~\n")
    new_payload = {
        "search_page_ids": [208323729264134],
        "ad_reached_countries": ["GB"],
        "ad_status": "ACTIVE",
        "fields": ["ad_delivery_start_time", "ad_delivery_stop_time"]
    }
    api.reload_payload(new_payload)
    results_bing = api.get_results()

    # Have a look at retrieved records for Google (session still active and launching queries to get next pages)
    print(f"Number of Google results in queue: {len(results_google)}")
    print(f"First Google result: {results_google[0]}")
    iter_on_results(results_google, limit_results)

    # Have a look at retrieved records for Bing (session still active and launching queries to get next pages)
    print(f"Number of Bing results in queue: {len(results_google)}")
    print(f"First Bing result: {results_google[0]}")
    iter_on_results(results_google, limit_results)
