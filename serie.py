class Serie:
    def __init__(self, name, human_name):
        self.name = name
        self.human_name = human_name


def serie_from_url(url):
    return Serie(
        name=url.split("/series/")[1].rstrip("/"),
        human_name=url.split("/series/")[1].rsplit("-", 1)[0].replace("-", " "),
    )
