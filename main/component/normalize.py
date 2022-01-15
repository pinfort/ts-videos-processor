import mojimoji

class Normalize():
    specifiedChars = str.maketrans({
        "\\": "￥",
        "/": "／",
        ":": "：",
        "*": "＊",
        "?": "？",
        "\"": "”",
        "<": "＜",
        ">": "＞",
        "|": "｜",
    })

    def normalize(self, name: str) -> str:
        converted: str = mojimoji.zen_to_han(name, kana=False)
        return converted.translate(self.specifiedChars)
