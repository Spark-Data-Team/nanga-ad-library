import warnings

from enum import Enum

from nanga_ad_library.utils import *

"""
Define MetaAdLibrary class to prepare api request:
    Check parameters
    Deal with platform particularities
    Prepare fields to parse
"""


class MetaAdLibrary:
    """A class instancing the Meta Ad Library API (https://www.facebook.com/ads/library/api/)"""

    # https://developers.facebook.com/docs/graph-api/reference/ads_archive/?locale=fr_FR
    BASE_URL = "https://graph.facebook.com"
    ENDPOINT = "ads_archive"
    METHOD = "GET"
    PLATFORM = "meta"
    API_NAME = "META_GRAPH_API"

    def __init__(self, payload, verbose=False):
        """Initializes the object's internal data.

        Args:
            payload: The payload provided by the user.
        """

        # Retrieves all url components to prepare final_url to query
        self.__base_url = self.BASE_URL
        self.__endpoint = self.ENDPOINT
        self.__version = get_default_api_version(self.API_NAME)

        # Components to use in api module
        self.__method = self.METHOD
        self.__final_url = f"{self.__base_url}/{self.__version}/{self.__endpoint}"
        self.__payload = payload

        # Other useful components:
        self.__target_political_ads = False  # Set to False first, it's then calculated in self.init() (lines 118-131)
        self.__verbose = verbose or False

    def __del__(self):
        if self.__verbose:
            print("Meta Ad Library object killed")
        self.__dict__.clear()

    @classmethod
    def check_political_ads_targeting(cls, payload: dict):
        """
        Checks if political ads are targeted
        """
        return payload.get("ad_type") == "POLITICAL_AND_ISSUE_ADS"

    def get_api_version(self):
        return self.__version

    def update_api_version(self, new_version):
        self.__version = compare_version_to_default(new_version, self.__version)

    def get_method(self):
        return self.__method

    def update_method(self, method: str):
        # Check provided method is valid
        MetaLibraryHttpMethods.check_method(method)
        # Update stored method
        self.__method = method

    def get_final_url(self):
        return self.__final_url

    def get_payload(self):
        return self.__payload

    def update_payload(self, payload: dict):
        """"
        Update the payload or part of it with params dict
        """
        # Check if target_political_ads needs to be updated
        self.__target_political_ads = self.__target_political_ads or self.check_political_ads_targeting(payload)

        # Check that the provided dict is valid
        for param_name, param_value in payload.items():
            if param_name == "fields":
                self.__payload[param_name] = MetaField.review_fields(param_value, self.__verbose)
            else:
                self.__payload[param_name] = MetaParam.ensure_validity(
                    param_name,
                    param_value,
                    self.__target_political_ads
                )

    @classmethod
    def init(cls, **kwargs):
        """
        Process the provided payload and create a MetaAdLibrary object if everything is fine

        Returns:
            A new MetaAdLibrary object.
        """
        # Check kwargs has mandatory arguments
        MetaLibraryMandatoryArgs.check_arguments(**kwargs)

        # Extract verbose
        verbose = kwargs.get("verbose")

        # Extract fields and params
        payload = kwargs.get("payload")
        fields = payload.get("fields")
        params = {key: val for key, val in payload.items() if key != "fields"}

        # Check if only political ads are targeted
        target_political_ads = cls.check_political_ads_targeting(params)

        # Check params dict is fully compatible for a Meta GRAPH API request
        MetaParam.check_mandatory_params(params)
        for param in params.keys():
            if params[param] is not None:
                params[param] = MetaParam.ensure_validity(param, params[param], target_political_ads)

        # Check fields are fully compatible for a Meta GRAPH API request and add them to params dict
        params.update({"fields": MetaField.review_fields(fields)})

        # Create MetaAdLibrary object and add elements
        library = cls(params, verbose)
        library.__target_political_ads = target_political_ads
        if kwargs.get("version"):
            library.update_api_version(kwargs.get("version"))
        if kwargs.get("method"):
            library.update_method(kwargs.get("method"))

        return library


"""
Useful classes to help MetaAdLibrary objects creation.
"""


class MetaLibraryMandatoryArgs(Enum):
    """
    Mandatory arguments for class MetaAdLibrary init.
    """
    PAYLOAD = "payload"

    @classmethod
    def check_arguments(cls, **kwargs):
        """
        Check that all parameters needed to initiate a MetaAdLibrary object are provided in kwargs.

        Args:
            kwargs: Args dict received in NANGA_AD_LIBRARY initiation.

        Returns:
             Whether all mandatory arguments are provided.
        """
        needed_args = {member.value for member in cls}
        provided_args = set(kwargs.keys())

        if not needed_args.issubset(provided_args):
            missing_args_str = "\n\t- ".join(list(needed_args - provided_args))
            # To update
            raise ValueError(
                f"""Missing mandatory arguments to initiate Meta Ad Library object:\n\t- {missing_args_str}"""
            )


class MetaLibraryHttpMethods(Enum):
    """
    HTTP methods allowed for Meta Ad Library ('ads_archive' endpoint of Meta GRAPH API).
    """
    GET = "GET"

    @classmethod
    def check_method(cls, method):
        """
        Check that provided method is an allowed HTTP method for the Meta Ad Library.

        Args:
             method: HTTP method to use to query

        Raises:
            ValueError if the method is not allowed.
        """

        if method not in [member.value for member in cls]:
            # To update
            raise ValueError(
                f"""{method} is not an available HTTP method for Meta Ad Library API."""
            )


"""
    Following classes are designed to ensure only available values are chosen.
    Cf Facebook Developers doc: https://developers.facebook.com/docs/graph-api/reference/ads_archive
"""


class AdStatus(Enum):
    """
    Values available for ad_active_status parameter.
    """
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ALL = "ALL"


class AdCountry(Enum):
    """
    Values available for ad_reached_countries parameter.
    """
    ALL = "ALL"
    BRAZIL = "BR"
    INDIA = "IN"
    UNITED_KINGDOM = "GB"
    UNITED_STATES = "US"
    CANADA = "CA"
    ARGENTINA = "AR"
    AUSTRALIA = "AU"
    AUSTRIA = "AT"
    BELGIUM = "BE"
    CHILE = "CL"
    CHINA = "CN"
    COLOMBIA = "CO"
    CROATIA = "HR"
    DENMARK = "DK"
    DOMINICAN_REPUBLIC = "DO"
    EGYPT = "EG"
    FINLAND = "FI"
    FRANCE = "FR"
    GERMANY = "DE"
    GREECE = "GR"
    HONG_KONG = "HK"
    INDONESIA = "ID"
    IRELAND = "IE"
    ISRAEL = "IL"
    ITALY = "IT"
    JAPAN = "JP"
    JORDAN = "JO"
    KUWAIT = "KW"
    LEBANON = "LB"
    MALAYSIA = "MY"
    MEXICO = "MX"
    NETHERLANDS = "NL"
    NEW_ZEALAND = "NZ"
    NIGERIA = "NG"
    NORWAY = "NO"
    PAKISTAN = "PK"
    PANAMA = "PA"
    PERU = "PE"
    PHILIPPINES = "PH"
    POLAND = "PL"
    RUSSIA = "RU"
    SAUDI_ARABIA = "SA"
    SERBIA = "RS"
    SINGAPORE = "SG"
    SOUTH_AFRICA = "ZA"
    SOUTH_KOREA = "KR"
    SPAIN = "ES"
    SWEDEN = "SE"
    SWITZERLAND = "CH"
    TAIWAN = "TW"
    THAILAND = "TH"
    TURKEY = "TR"
    UNITED_ARAB_EMIRATES = "AE"
    VENEZUELA = "VE"
    PORTUGAL = "PT"
    LUXEMBOURG = "LU"
    BULGARIA = "BG"
    CZECH_REPUBLIC = "CZ"
    SLOVENIA = "SI"
    ICELAND = "IS"
    SLOVAKIA = "SK"
    LITHUANIA = "LT"
    TRINIDAD_AND_TOBAGO = "TT"
    BANGLADESH = "BD"
    SRI_LANKA = "LK"
    KENYA = "KE"
    HUNGARY = "HU"
    MOROCCO = "MA"
    CYPRUS = "CY"
    JAMAICA = "JM"
    ECUADOR = "EC"
    ROMANIA = "RO"
    BOLIVIA = "BO"
    GUATEMALA = "GT"
    COSTA_RICA = "CR"
    QATAR = "QA"
    EL_SALVADOR = "SV"
    HONDURAS = "HN"
    NICARAGUA = "NI"
    PARAGUAY = "PY"
    URUGUAY = "UY"
    PUERTO_RICO = "PR"
    BOSNIA_AND_HERZEGOVINA = "BA"
    PALESTINE = "PS"
    TUNISIA = "TN"
    BAHRAIN = "BH"
    VIETNAM = "VN"
    GHANA = "GH"
    MAURITIUS = "MU"
    UKRAINE = "UA"
    MALTA = "MT"
    BAHAMAS = "BS"
    MALDIVES = "MV"
    OMAN = "OM"
    NORTH_MACEDONIA = "MK"
    LATVIA = "LV"
    ESTONIA = "EE"
    IRAQ = "IQ"
    ALGERIA = "DZ"
    ALBANIA = "AL"
    NEPAL = "NP"
    MACAU = "MO"
    MONTENEGRO = "ME"
    SENEGAL = "SN"
    GEORGIA = "GE"
    BRUNEI = "BN"
    UGANDA = "UG"
    GUADELOUPE = "GP"
    BARBADOS = "BB"
    AZERBAIJAN = "AZ"
    TANZANIA = "TZ"
    LIBYA = "LY"
    MARTINIQUE = "MQ"
    CAMEROON = "CM"
    BOTSWANA = "BW"
    ETHIOPIA = "ET"
    KAZAKHSTAN = "KZ"
    NAMIBIA = "NA"
    MADAGASCAR = "MG"
    NEW_CALEDONIA = "NC"
    MOLDOVA = "MD"
    FIJI = "FJ"
    BELARUS = "BY"
    JERSEY = "JE"
    GUAM = "GU"
    YEMEN = "YE"
    ZAMBIA = "ZM"
    ISLE_OF_MAN = "IM"
    HAITI = "HT"
    CAMBODIA = "KH"
    ARUBA = "AW"
    FRENCH_POLYNESIA = "PF"
    AFGHANISTAN = "AF"
    BERMUDA = "BM"
    GUYANA = "GY"
    ARMENIA = "AM"
    MALAWI = "MW"
    ANTIGUA_AND_BARBUDA = "AG"
    RWANDA = "RW"
    GUERNSEY = "GG"
    GAMBIA = "GM"
    FAROE_ISLANDS = "FO"
    SAINT_LUCIA = "LC"
    CAYMAN_ISLANDS = "KY"
    BENIN = "BJ"
    ANDORRA = "AD"
    GRENADA = "GD"
    VIRGIN_ISLANDS_US = "VI"
    BELIZE = "BZ"
    SAINT_VINCENT_AND_THE_GRENADINES = "VC"
    MONGOLIA = "MN"
    MOZAMBIQUE = "MZ"
    MALI = "ML"
    ANGOLA = "AO"
    FRENCH_GUIANA = "GF"
    UZBEKISTAN = "UZ"
    DJIBOUTI = "DJ"
    BURKINA_FASO = "BF"
    MONACO = "MC"
    TOGO = "TG"
    GREENLAND = "GL"
    GABON = "GA"
    GIBRALTAR = "GI"
    CONGO_DEMOCRATIC_REPUBLIC = "CD"
    KYRGYZSTAN = "KG"
    PAPUA_NEW_GUINEA = "PG"
    BHUTAN = "BT"
    SAINT_KITTS_AND_NEVIS = "KN"
    ESWATINI = "SZ"
    LESOTHO = "LS"
    LAOS = "LA"
    LIECHTENSTEIN = "LI"
    NORTHERN_MARIANA_ISLANDS = "MP"
    SURINAME = "SR"
    SEYCHELLES = "SC"
    VIRGIN_ISLANDS_BRITISH = "VG"
    TURKS_AND_CAICOS_ISLANDS = "TC"
    DOMINICA = "DM"
    MAURITANIA = "MR"
    ALAND_ISLANDS = "AX"
    SAN_MARINO = "SM"
    SIERRA_LEONE = "SL"
    NIGER = "NE"
    CONGO_REPUBLIC = "CG"
    ANGUILLA = "AI"
    MAYOTTE = "YT"
    CAPE_VERDE = "CV"
    GUINEA = "GN"
    TURKMENISTAN = "TM"
    BURUNDI = "BI"
    TAJIKISTAN = "TJ"
    VANUATU = "VU"
    SOLOMON_ISLANDS = "SB"
    ERITREA = "ER"
    SAMOA = "WS"
    AMERICAN_SAMOA = "AS"
    FALKLAND_ISLANDS = "FK"
    EQUATORIAL_GUINEA = "GQ"
    TONGA = "TO"
    COMOROS = "KM"
    PALAU = "PW"
    MICRONESIA = "FM"
    CENTRAL_AFRICAN_REPUBLIC = "CF"
    SOMALIA = "SO"
    MARSHALL_ISLANDS = "MH"
    VATICAN_CITY = "VA"
    CHAD = "TD"
    KIRIBATI = "KI"
    SAO_TOME_AND_PRINCIPE = "ST"
    TUVALU = "TV"
    NAURU = "NR"
    REUNION = "RE"
    LIBERIA = "LR"
    ZIMBABWE = "ZW"
    IVORY_COAST = "CI"
    MYANMAR = "MM"
    NETHERLANDS_ANTILLES = "AN"
    ANTARCTICA = "AQ"
    BONAIRE = "BQ"
    BOUVET_ISLAND = "BV"
    BRITISH_INDIAN_OCEAN_TERRITORY = "IO"
    CHRISTMAS_ISLAND = "CX"
    COCOS_ISLANDS = "CC"
    COOK_ISLANDS = "CK"
    CURACAO = "CW"
    FRENCH_SOUTHERN_AND_ANTARCTIC_LANDS = "TF"
    GUINEA_BISSAU = "GW"
    HEARD_ISLAND_AND_MCDONALD_ISLANDS = "HM"
    KOSOVO = "XK"
    MONTSERRAT = "MS"
    NIUE = "NU"
    NORFOLK_ISLAND = "NF"
    PITCAIRN_ISLANDS = "PN"
    SAINT_BARTHELEMY = "BL"
    SAINT_HELENA = "SH"
    SAINT_MARTIN = "MF"
    SAINT_PIERRE_AND_MIQUELON = "PM"
    SINT_MAARTEN = "SX"
    SOUTH_GEORGIA_AND_SOUTH_SANDWICH_ISLANDS = "GS"
    SOUTH_SUDAN = "SS"
    SVALBARD_AND_JAN_MAYEN = "SJ"
    TIMOR_LESTE = "TL"
    TOKELAU = "TK"
    UNITED_STATES_MINOR_OUTLYING_ISLANDS = "UM"
    WALLIS_AND_FUTUNA = "WF"
    WESTERN_SAHARA = "EH"


class AdType(Enum):
    """
    Values available for ad_type parameter.
    """
    ALL = "ALL"
    EMPLOYMENT_ADS = "EMPLOYMENT_ADS"
    FINANCIAL_PRODUCTS_AND_SERVICES_ADS = "FINANCIAL_PRODUCTS_AND_SERVICES_ADS"
    HOUSING_ADS = "HOUSING_ADS"
    POLITICAL_AND_ISSUE_ADS = "POLITICAL_AND_ISSUE_ADS"


class AudienceSizeMax(Enum):
    """
    Values available for estimated_audience_size_max parameter.
    """
    _1K = 1000
    _5K = 5000
    _10K = 10000
    _50K = 50000
    _100K = 100000
    _500K = 500000
    _1M = 1000000


class AudienceSizeMin(Enum):
    """
    Values available for estimated_audience_size_min parameter.
    """
    _1H = 100
    _1K = 1000
    _5K = 5000
    _10K = 10000
    _50K = 50000
    _100K = 100000
    _500K = 500000
    _1M = 1000000


class AdLanguages(Enum):
    """
    Values available for languages parameter.
    Language codes are based on the ISO 639-1 language codes and also includes ISO 639-3 language codes CMN and YUE
    """
    # ISO 639-1 codes
    AFAR = "aa"
    ABKHAZIAN = "ab"
    AFRIKAANS = "af"
    AKAN = "ak"
    AMHARIC = "am"
    ARAGONESE = "an"
    ARABIC = "ar"
    ASSAMESE = "as"
    AVARIC = "av"
    AYMARA = "ay"
    AZERBAIJANI = "az"
    BASHKIR = "ba"
    BELARUSIAN = "be"
    BULGARIAN = "bg"
    BIHARI = "bh"
    BISLAMA = "bi"
    BAMBARA = "bm"
    BENGALI = "bn"
    TIBETAN = "bo"
    BRETON = "br"
    BOSNIAN = "bs"
    CATALAN = "ca"
    CHECHEN = "ce"
    CHAMORRO = "ch"
    CORSICAN = "co"
    CREE = "cr"
    CZECH = "cs"
    CHURCH_SLAVIC = "cu"
    CHUVASH = "cv"
    WELSH = "cy"
    DANISH = "da"
    GERMAN = "de"
    MALDIVIAN = "dv"
    DZONGKHA = "dz"
    EWE = "ee"
    GREEK = "el"
    ENGLISH = "en"
    ESPERANTO = "eo"
    SPANISH = "es"
    ESTONIAN = "et"
    BASQUE = "eu"
    PERSIAN = "fa"
    FULA = "ff"
    FINNISH = "fi"
    FIJIAN = "fj"
    FAROESE = "fo"
    FRENCH = "fr"
    WESTERN_FRISIAN = "fy"
    IRISH = "ga"
    SCOTTISH_GAELIC = "gd"
    GALICIAN = "gl"
    GUARANI = "gn"
    GUJARATI = "gu"
    MANX = "gv"
    HAUSA = "ha"
    HEBREW = "he"
    HINDI = "hi"
    HIRI_MOTU = "ho"
    CROATIAN = "hr"
    HAITIAN_CREOLE = "ht"
    HUNGARIAN = "hu"
    ARMENIAN = "hy"
    HERERO = "hz"
    INTERLINGUA = "ia"
    INDONESIAN = "id"
    INTERLINGUE = "ie"
    IGBO = "ig"
    SICHUAN_YI = "ii"
    INUPIAQ = "ik"
    IDO = "io"
    ICELANDIC = "is"
    ITALIAN = "it"
    INUKTITUT = "iu"
    JAPANESE = "ja"
    JAVANESE = "jv"
    GEORGIAN = "ka"
    KONGO = "kg"
    KIKUYU = "ki"
    KINYARWANDA = "rw"
    KAZAKH = "kk"
    KALAALLISUT = "kl"
    KHMER = "km"
    KANNADA = "kn"
    KOREAN = "ko"
    KANURI = "kr"
    KASHMIRI = "ks"
    KURDISH = "ku"
    KOMI = "kv"
    CORNISH = "kw"
    KYRGYZ = "ky"
    LATIN = "la"
    LUXEMBOURGISH = "lb"
    GANDA = "lg"
    LIMBURGISH = "li"
    LINGALA = "ln"
    LAO = "lo"
    LITHUANIAN = "lt"
    LUBA_KATANGA = "lu"
    LATVIAN = "lv"
    MALAGASY = "mg"
    MARSHALLESE = "mh"
    MAORI = "mi"
    MACEDONIAN = "mk"
    MALAYALAM = "ml"
    MONGOLIAN = "mn"
    MARATHI = "mr"
    MALAY = "ms"
    MALTESE = "mt"
    BURMESE = "my"
    NAURU = "na"
    NORWEGIAN_BOKMAL = "nb"
    NORTH_NDEBELE = "nd"
    NEPALI = "ne"
    NDONGA = "ng"
    DUTCH = "nl"
    NORWEGIAN_NYNORSK = "nn"
    NORWEGIAN = "no"
    SOUTH_NDEBELE = "nr"
    NAVAJO = "nv"
    CHICHEWA = "ny"
    OCCITAN = "oc"
    OJIBWE = "oj"
    OROMO = "om"
    ORIYA = "or"
    OSSETIAN = "os"
    PUNJABI = "pa"
    PALI = "pi"
    POLISH = "pl"
    PASHTO = "ps"
    PORTUGUESE = "pt"
    QUECHUA = "qu"
    ROMANSH = "rm"
    KIRUNDI = "rn"
    ROMANIAN = "ro"
    RUSSIAN = "ru"
    SANSKRIT = "sa"
    SARDINIAN = "sc"
    SINDHI = "sd"
    NORTHERN_SAMI = "se"
    SAMOAN = "sm"
    SANGO = "sg"
    SERBIAN = "sr"
    GAELIC = "gd"
    SHONA = "sn"
    SINHALA = "si"
    SLOVAK = "sk"
    SLOVENIAN = "sl"
    SOMALI = "so"
    ALBANIAN = "sq"
    SERBIAN_LATIN = "sr"
    SWATI = "ss"
    SOTHO = "st"
    SUNDANESE = "su"
    SWEDISH = "sv"
    SWAHILI = "sw"
    TAMIL = "ta"
    TELUGU = "te"
    TAJIK = "tg"
    THAI = "th"
    TIGRINYA = "ti"
    TURKMEN = "tk"
    TAGALOG = "tl"
    TSWANA = "tn"
    TONGA = "to"
    TURKISH = "tr"
    TSONGA = "ts"
    TATAR = "tt"
    TWI = "tw"
    TAHITIAN = "ty"
    UIGHUR = "ug"
    UKRAINIAN = "uk"
    URDU = "ur"
    UZBEK = "uz"
    VENDA = "ve"
    VIETNAMESE = "vi"
    VOLAPUK = "vo"
    WALLOON = "wa"
    WOLLOF = "wo"
    XHOSA = "xh"
    YIDDISH = "yi"
    YORUBA = "yo"
    ZHUANG = "za"
    CHINESE = "zh"
    ZULU = "zu"
    # ISO 639-3 codes
    MANDARIN = "cmn"
    CANTONESE = "yue"


class MediaType(Enum):
    """
    Values available for media_type parameter.
    """
    ALL = "ALL"
    IMAGE = "IMAGE"
    MEME = "MEME"
    VIDEO = "VIDEO"
    NONE = "NONE"


class AdPlacement(Enum):
    """
    Values available for publisher_platforms parameter.
    """
    FACEBOOK = "FACEBOOK"
    INSTAGRAM = "INSTAGRAM"
    AUDIENCE_NETWORK = "AUDIENCE_NETWORK"
    MESSENGER = "MESSENGER"
    WHATSAPP = "WHATSAPP"
    OCULUS = "OCULUS"
    THREADS = "THREADS"


class SearchType(Enum):
    """
    Values available for search_type parameter.
    """
    THREADS = "THREADS"
    KEYWORD_EXACT_PHRASE = "KEYWORD_EXACT_PHRASE"


class EuropeanCountry(Enum):
    """
    Values available for ad_reached_countries parameter that match EU countries.
    """
    AUSTRIA = "AT"
    BELGIUM = "BE"
    BULGARIA = "BG"
    CROATIA = "HR"
    CYPRUS = "CY"
    CZECH_REPUBLIC = "CZ"
    DENMARK = "DK"
    ESTONIA = "EE"
    FINLAND = "FI"
    FRANCE = "FR"
    GERMANY = "DE"
    GREECE = "GR"
    HUNGARY = "HU"
    IRELAND = "IE"
    ITALY = "IT"
    LATVIA = "LV"
    LITHUANIA = "LT"
    LUXEMBOURG = "LU"
    MALTA = "MT"
    NETHERLANDS = "NL"
    POLAND = "PL"
    PORTUGAL = "PT"
    ROMANIA = "RO"
    SLOVAKIA = "SK"
    SLOVENIA = "SI"
    SPAIN = "ES"
    SWEDEN = "SE"


class MetaParam(Enum):
    """
    Parameters available for API. (https://developers.facebook.com/docs/graph-api/reference/ads_archive/)

    Members:
        name: Full name of the parameter.
        class: Class (Enum) listing the available values for this parameter.
        only_political: Whether the parameter is available only for 'POLITICAL_AND_ISSUE_ADS' requests.
        exp_type: Dict storing information on the expected shape of data for the parameter value:
            is_date: Whether the parameter value is expected to be representing a date.
            date_format: If is_date, then specify the expected format of the stringified date.
            is_list: Whether the parameter value is expected to be a list of values.
            t_types: Tuple of authorized types for the provided values (if empty tuple: all types are accepted).
            max_len: Max authorized length for the parameter value (if None: no size restrictions).
    """
    AD_STATUS = {
        "name": "ad_active_status",
        "class": AdStatus,
        "only_political": False,
        "mandatory_level": None,
        "exp_type": {
            "is_date": False,
            "date_format": None,
            "is_list": False,
            "t_types": tuple([]),
            "max_len": None
        }
    }
    AD_DELIVERY_MAX = {
        "name": "ad_delivery_date_max",
        "class": None,
        "only_political": False,
        "mandatory_level": None,
        "exp_type": {
            "is_date": True,
            "date_format": "%Y-%m-%d",
            "is_list": False,
            "t_types": tuple([]),
            "max_len": None
        }
    }
    AD_DELIVERY_MIN = {
        "name": "ad_delivery_date_min",
        "class": None,
        "only_political": False,
        "mandatory_level": None,
        "exp_type": {
            "is_date": True,
            "date_format": "%Y-%m-%d",
            "is_list": False,
            "t_types": tuple([]),
            "max_len": None
        }
    }
    AD_COUNTRY = {
        "name": "ad_reached_countries",
        "class": AdCountry,
        "only_political": False,
        "mandatory_level": 1,
        "exp_type": {
            "is_date": False,
            "date_format": None,
            "is_list": True,
            "t_types": tuple([]),
            "max_len": None
        }
    }
    AD_TYPE = {
        "name": "ad_type",
        "class": AdType,
        "only_political": True,
        "mandatory_level": None,
        "exp_type": {
            "is_date": False,
            "date_format": None,
            "is_list": False,
            "t_types": tuple([]),
            "max_len": None
        }
    }
    BYLINE = {
        "name": "bylines",
        "class": None,
        "only_political": True,
        "mandatory_level": None,
        "exp_type": {
            "is_date": False,
            "date_format": None,
            "is_list": True,
            "t_types": tuple([str]),
            "max_len": None
        }
    }
    LOCAL_DELIVERY = {
        "name": "delivery_by_region",
        "class": None,
        "only_political": True,
        "mandatory_level": None,
        "exp_type": {
            "is_date": False,
            "date_format": None,
            "is_list": True,
            "t_types": tuple([str]),
            "max_len": None
        }
    }
    AUDIENCE_MAX = {
        "name": "estimated_audience_size_max",
        "class": AudienceSizeMax,
        "only_political": True,
        "mandatory_level": None,
        "exp_type": {
            "is_date": False,
            "date_format": None,
            "is_list": False,
            "t_types": tuple([]),
            "max_len": None
        }
    }
    AUDIENCE_MIN = {
        "name": "estimated_audience_size_min",
        "class": AudienceSizeMin,
        "only_political": True,
        "mandatory_level": None,
        "exp_type": {
            "is_date": False,
            "date_format": None,
            "is_list": False,
            "t_types": tuple([]),
            "max_len": None
        }
    }
    LANGUAGE = {
        "name": "languages",
        "class": AdLanguages,
        "only_political": False,
        "mandatory_level": None,
        "exp_type": {
            "is_date": False,
            "date_format": None,
            "is_list": True,
            "t_types": tuple([]),
            "max_len": None
        }
    }
    MEDIA_TYPE = {
        "name": "media_type",
        "class": MediaType,
        "only_political": False,
        "mandatory_level": None,
        "exp_type": {
            "is_date": False,
            "date_format": None,
            "is_list": False,
            "t_types": tuple([]),
            "max_len": None
        }
    }
    PLACEMENT = {
        "name": "publisher_platforms",
        "class": AdPlacement,
        "only_political": False,
        "mandatory_level": None,
        "exp_type": {
            "is_date": False,
            "date_format": None,
            "is_list": True,
            "t_types": tuple([]),
            "max_len": None
        }
    }
    PAGE = {
        "name": "search_page_ids",
        "class": None,
        "only_political": False,
        "mandatory_level": 2,
        "exp_type": {
            "is_date": False,
            "date_format": None,
            "is_list": True,
            "t_types": tuple([int]),
            "max_len": 10
        }
    }
    SEARCH_TERM = {
        "name": "search_terms",
        "class": None,
        "only_political": False,
        "mandatory_level": 2,
        "exp_type": {
            "is_date": False,
            "date_format": None,
            "is_list": False,
            "t_types": tuple([str]),
            "max_len": 100
        }
    }
    SEARCH_TYPE = {
        "name": "search_type",
        "class": SearchType,
        "only_political": False,
        "mandatory_level": None,
        "exp_type": {
            "is_date": False,
            "date_format": None,
            "is_list": False,
            "t_types": tuple([]),
            "max_len": None
        }
    }
    UNMASK_REMOVED_CONTENT = {
        "name": "unmask_removed_content",
        "class": None,
        "only_political": False,
        "mandatory_level": None,
        "exp_type": {
            "is_date": False,
            "date_format": None,
            "is_list": False,
            "t_types": tuple([bool]),
            "max_len": None
        }
    }

    @classmethod
    def ensure_validity(cls, param_name: str, param_value: str, target_political_ads: bool):
        """
        Check that a parameter provided value is valid for the Meta Ad Library API
            (cf https://developers.facebook.com/docs/graph-api/reference/ads_archive/)

        Args:
            param_name: The parameter name.
            param_value: The parameter value.
            target_political_ads: Whether the request made by the user is targeting only political ads.

        Returns:
            The value of the parameter, updated if needed.
            Raise a ValueError if the provided value is not compatible with API standards.
        """

        # List available parameters (only_political params are available only if target_political_ads)
        available_params = {
            member.value.get("name"): member.value for member in cls
            if target_political_ads or not member.value.get("only_political")
        }

        # Check that the provided parameter is of the available ones
        if param_name in available_params.keys():
            meta_param = available_params.get(param_name)
        else:
            available_params_str = "\n\t- ".join(available_params.keys())
            # To update
            raise ValueError(
                f"""'{param_name}' is not a valid parameter for Meta Ad Library API.\n"""
                f"""Available parameters are: """
                f"""(cf https://developers.facebook.com/docs/graph-api/reference/ads_archive/)\n"""
                f"""\t- {available_params_str}"""
            )

        # Check that the param value is valid
        expected_type_dict = meta_param.get("exp_type")
        # # When limited options, check that provided value is accepted:
        if meta_param.get("class"):
            accepted_values = [member.value for member in meta_param.get("class")]
            check_param_value(
                param=param_name,
                value=param_value,
                accepted_values=accepted_values,
                is_list=expected_type_dict.get("is_list")
            )
        # # When param is expected to be a date check it is and apply format
        elif expected_type_dict.get("is_date"):
            param_value = enforce_date_param_format(
                param=param_name,
                value=param_value,
                date_format=expected_type_dict.get("date_format")
            )
        # # When types specs are given, check the provided value complies:
        else:
            check_param_type(
                param=param_name,
                value=param_value,
                types=expected_type_dict.get("t_types"),
                is_list=expected_type_dict.get("is_list")
            )
            # If param has a maximal size: ensure it's shorter than the limit
            max_len = expected_type_dict.get("max_len")
            try:
                exceed_max_len = isinstance(max_len, int) and len(param_value) > max_len
            except:
                exceed_max_len = True
            if exceed_max_len:
                # To update
                raise ValueError(
                    f"""{param_value} is not a valid value for {param_name} parameter.\n"""
                    f"""It's size is capped to {max_len}. """
                    f"""(cf https://developers.facebook.com/docs/graph-api/reference/ads_archive/)"""
                )

        return param_value

    @classmethod
    def check_mandatory_params(cls, params: dict):
        """
        Checks that all mandatory params are provided.

        Args:
             params: The params provided by the user.

        Raises:
            ValueError if at least one parameter is missing.
        """

        # Retrieve mandatory params using "mandatory_level" key
        mandatory_params = [member.value for member in cls if member.value.get("mandatory_level")]

        # Check which of these mandatory params are provided
        params_checker = {}
        params_display = {}
        for mandatory_param in mandatory_params:
            name, level, provided = mandatory_param.get("name"), str(mandatory_param.get("mandatory_level")), False
            # Update params display
            try:
                params_display[level].append(name)
            except:
                params_display[level] = [name]
            # Check if the param is provided
            provided = params.get(name) is not None
            # Update params checker
            params_checker[level] = params_checker.get(level) or provided

        # Check provided parameters are sufficient
        if not all(params_checker.values()):
            # Prepare error message
            min_missing_level = min([key for key, value in params_checker.items() if not value])
            missing_params = params_display[min_missing_level]
            if len(missing_params) == 1:
                error_message = f"""The parameter {missing_params[0]} is required."""
            else:
                error_message = f"""Parameters {' & '.join(missing_params)} cannot be both empty."""
            # To update
            raise ValueError(
                error_message
            )


class MetaField(Enum):
    """
    Available values for Meta Ad Library returned fields (All ads from all countries).
    Cf https://developers.facebook.com/docs/graph-api/reference/archived-ad/

    Members:
        name: Field's name to provide to Meta GRAPH API.
        mandatory: Whether the field is expected to be provided to Meta GRAPH API.
        warning: Warning message to display when the field is provided in the request. (Special behaviours)
    """
    ID = {
        "name": "id",
        "mandatory": True,
        "warning": None
    }
    AD_CREATION_TIME = {
        "name": "ad_creation_time",
        "mandatory": True,
        "warning": None
    }
    AD_CREATIVE_LINK_BODIES = {
        "name": "ad_creative_link_bodies",
        "mandatory": False,
        "warning": None
    }
    AD_CREATIVE_LINK_CAPTIONS = {
        "name": "ad_creative_link_captions",
        "mandatory": False,
        "warning": None
    }
    AD_CREATIVE_LINK_DESCRIPTIONS = {
        "name": "ad_creative_link_descriptions",
        "mandatory": False,
        "warning": None
    }
    AD_CREATIVE_LINK_TITLES = {
        "name": "ad_creative_link_titles",
        "mandatory": False,
        "warning": None
    }
    AD_DELIVERY_START_TIME = {
        "name": "ad_delivery_start_time",
        "mandatory": True,
        "warning": None
    }
    AD_DELIVERY_STOP_TIME = {
        "name": "ad_delivery_stop_time",
        "mandatory": True,
        "warning": None
    }
    AD_SNAPSHOT_URL = {
        "name": "ad_snapshot_url",
        "mandatory": True,
        "warning": None
    }
    AGE_COUNTRY_GENDER_REACH_BREAKDOWN = {
        "name": "age_country_gender_reach_breakdown",
        "mandatory": False,
        "warning": "The 'age_country_gender_reach_breakdown' field is available only for ads delivered to the EU" +
                   "and POLITICAL_AND_ISSUE_ADS delivered to Brazil."
    }
    BENEFICIARY_PAYERS = {
        "name": "beneficiary_payers",
        "mandatory": False,
        "warning": "The 'beneficiary_payers' field is available only for ads delivered to the EU."
    }
    BR_TOTAL_REACH = {
        "name": "br_total_reach",
        "mandatory": False,
        "warning": "The 'br_total_reach' field is available for POLITICAL_AND_ISSUE_ADS delivered to Brazil."
    }
    BYLINES = {
        "name": "bylines",
        "mandatory": False,
        "warning": "The 'bylines' field is available only for POLITICAL_AND_ISSUE_ADS."
    }
    CURRENCY = {
        "name": "currency",
        "mandatory": False,
        "warning": "The 'currency' field is available only for POLITICAL_AND_ISSUE_ADS."
    }
    DELIVERY_BY_REGION = {
        "name": "delivery_by_region",
        "mandatory": False,
        "warning": "The 'delivery_by_region' field is available only for POLITICAL_AND_ISSUE_ADS."
    }
    DEMOGRAPHIC_DISTRIBUTION = {
        "name": "demographic_distribution",
        "mandatory": False,
        "warning": "The 'demographic_distribution' field is available only for POLITICAL_AND_ISSUE_ADS."
    }
    ESTIMATED_AUDIENCE_SIZE = {
        "name": "estimated_audience_size",
        "mandatory": False,
        "warning": "The 'estimated_audience_size' field is available only for POLITICAL_AND_ISSUE_ADS."
    }
    EU_TOTAL_REACH = {
        "name": "eu_total_reach",
        "mandatory": False,
        "warning": "The 'eu_total_reach' field is available only for ads delivered to the EU."
    }
    IMPRESSIONS = {
        "name": "impressions",
        "mandatory": False,
        "warning": "The 'impressions' field is available only for POLITICAL_AND_ISSUE_ADS."
    }
    LANGUAGES = {
        "name": "languages",
        "mandatory": False,
        "warning": None
    }
    PAGE_ID = {
        "name": "page_id",
        "mandatory": True,
        "warning": None
    }
    PAGE_NAME = {
        "name": "page_name",
        "mandatory": True,
        "warning": None
    }
    PUBLISHER_PLATFORMS = {
        "name": "publisher_platforms",
        "mandatory": False,
        "warning": None
    }
    SPEND = {
        "name": "spend",
        "mandatory": False,
        "warning": "The 'spend' field is available only for POLITICAL_AND_ISSUE_ADS."
    }
    TARGET_AGES = {
        "name": "target_ages",
        "mandatory": False,
        "warning": "The 'target_ages' field is available only for ads delivered to the EU and " +
                   "POLITICAL_AND_ISSUE_ADS delivered to Brazil."
    }
    TARGET_GENDER = {
        "name": "target_gender",
        "mandatory": False,
        "warning": "The 'target_gender' field is available only for ads delivered to the EU and " +
                   "POLITICAL_AND_ISSUE_ADS delivered to Brazil."
    }
    TARGET_LOCATIONS = {
        "name": "target_locations",
        "mandatory": False,
        "warning": "The 'target_locations' field is available only for ads delivered to the EU and " +
                   "POLITICAL_AND_ISSUE_ADS delivered to Brazil."
    }

    @classmethod
    def review_fields(cls, fields: list, verbose=False):
        """
        Checks that:
            - mandatory fields are listed (else add them),
            - no unwanted fields are listed (else remove them).

        Args:
            fields: The fields to query from the Meta Ad Library API.
            verbose: Display the warning only if verbose is activated.

        Returns:
            The fields: reviewed and updated (if needed)
        """

        # Store fields in a dict
        meta_fields = {member.value.get("name"): member.value.get("warning") for member in cls}

        # Add mandatory fields if not provided
        mandatory_fields = [member.value.get("name") for member in cls if member.value.get("mandatory")]

        reviewed_fields = mandatory_fields
        # Review each provided field
        fields = fields or []
        for field in fields:
            field_warning, warning = meta_fields.get(field, "Field not found"), None
            if field_warning != "Field not found":
                # The field is available and can be added to the reviewed fields
                if field not in mandatory_fields:
                    reviewed_fields.append(field)
                # Prepare a warning to display if the field has special behaviour
                if field_warning:
                    warning = field_warning
            else:
                # If the provided field is not in the list, warn the user
                warning = f"""{field} is not an available field for Meta Ad Library API."""

            # Display a warning if needed
            if warning and verbose:
                warnings.warn(warning)

        return reviewed_fields

