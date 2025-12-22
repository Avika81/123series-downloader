class Serie:
    def __init__(self, name, human_name):
        self.name = name
        self.human_name = human_name


class Anime(Serie):
    pass


def anime_from_url(url):
    return Anime(
        name=url.split("/watch/")[1].rstrip("/"),
        human_name=url.split("/watch/")[1].rsplit("-", 1)[0].replace("-", " "),
    )


def serie_from_url(url):
    return Serie(
        name=url.split("/series/")[1].rstrip("/"),
        human_name=url.split("/series/")[1].rsplit("-", 1)[0].replace("-", " "),
    )
