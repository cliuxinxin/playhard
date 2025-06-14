class BibliocommonsFetchStrategy:
    def __init__(self):
        self.url = 'https://gateway.bibliocommons.com/v2/libraries/sjpl/events/search'
        self.headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
            'Origin': 'https://sjpl.bibliocommons.com',
            'Priority': 'u=1, i',
            'Referer': 'https://sjpl.bibliocommons.com/',
            'Sec-Ch-Ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        }
        self.cookies = {
            'branch': '%7B%22ip%22%3A%22128.199.14.41%22%2C%22sjpl%22%3Anull%7D',
            'NERF_SRV': 'nerf16',
            'SRV': 'app34',
            'EVENT': 'app04b',
        }

    def build_params(self, page, limit=2):
        return {
            'page': page,
            'limit': limit,
            'locale': 'en-US',
        }