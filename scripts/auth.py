class authenticate():
    def __init__(self, xtoken):
        self.xtoken = xtoken

    def create_headers(self):
        headers = {
            "x-token": self.xtoken
        }
        return headers