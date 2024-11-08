from nanga_ad_library import NangaAdLibraryApi

if __name__ == '__main__':

    # Initiate api and start with a focus on the search terms Quitoque in France
    init_hash = {
        "access_token": "EAACwplIENusBO6Jmw2HCFVhxU3WfZBiRCyXAUnJOLJ6MCPESgD6rhTgcSRq0d2QG2yx2L433tFzkGbNVnLzyxb0JWtsmw7PFUAgOvuTmsGq6aZAdJhbdKYGhPxZASlJuMvSYoHARiMubZB4LGSHMgjN5ChvDHMufRUB5sKZCwAndN5wHf9ZBn0BKCa",
        "app_secret": "3f834f93ae20261b1b14070289120758",
        "payload": {
            "search_terms": "Quitoque",
            "ad_reached_countries": ["FR"]
        },
        "verbose": True
    }
    print("\n~~~~~~ Initiating api ~~~~~~\n")
    api = NangaAdLibraryApi.init(platform="Meta", **init_hash)
    print("\n~~~~ Focusing on Quitoque ~~~~\n")
    results_quitoque = api.get_results()

    # Focus on 900.care page in Italie
    print("\n~~~~ Focusing on 900.care ~~~~\n")
    new_payload = {
        "search_page_ids": [121852905877303],
        "ad_reached_countries": ["FR"]
    }
    api.reload_payload(new_payload)
    results_900 = api.get_results()

    # Have a look at retrieved records for quitoque (session still active and launching queries to get next pages)
    count = 0
    print(len(results_quitoque))
    for result in results_quitoque:
        count += 1
        print(result.id, result.ad_snapshot_url)
        if count > 30:
            break

    # Have a look at retrieved record for 900 (session still active and launching queries to get next pages)
    count = 0
    print(len(results_900))
    for result in results_900:
        count += 1
        print(result.id, result.ad_snapshot_url)
        if count > 30:
            break

    # kwargs = {
    #     "appid": "value_id",
    # }
    #
    # needed_params = {member.value for member in MetaMandatoryParam}
    # provided_params = set(kwargs.keys())
    #
    # if not needed_params.issubset(provided_params):
    #     missing_params_str = "\n\t- ".join(list(needed_params - provided_params))
    #     # To update
    #     raise ValueError(
    #         f"""Missing mandatory parameters to initiate Meta Graph Session:\n\t- {missing_params_str}"""
    #     )



"""
# self.max_retries = app_id
        # self.app_secret = app_secret
        # self.access_token = access_token
        # self.proxies = proxies
        # self.timeout = timeout
        # self.debug = debug
        # 
        # 
        # # # SSL Config
        # self.requests.verify = cert_path if cert_path else True
        # # # Proxies
        # if proxies:
        #     self.requests.proxies.update(proxies)
        # # # Headers
        # default_headers = {
        #     "Accept": "application/json",
        #     "Content-Type": "application/json",
        # }
        # if headers:
        #     default_headers.update(headers)
        # self.requests.headers.update(default_headers)
        # # # Retries
        # if max_retries and backoff_factor:
        #     retries = Retry(
        #         total=max_retries,
        #         backoff_factor=backoff_factor,
        #         status_forcelist=[500, 502, 503, 504]
        #     )
        #     adapter = HTTPAdapter(max_retries=retries)
        #     self.requests.mount("http://", adapter)
        #     self.requests.mount("https://", adapter)
        # else:
        #     self.requests.adapters.clear()
        # # # Default parameters
        # params = {
        #     "access_token": self.access_token,
        # }
        # if app_id and app_secret:
        #     params["appsecret_proof"] = self._gen_appsecret_proof(app_id, app_secret)
        # self.requests.params.update(params)

"""