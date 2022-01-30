from typing import Any

classes = []

def register(func):
    def wrapper(*args, **kwargs):
        instance = func(*args, **kwargs)
        classes.append(instance)
    return wrapper

def take(func):
    def wrapper(*args, **kwargs):
        typ: type = func(*args, **kwargs)
        for instance in classes:
            if isinstance(instance, typ):
                return instance
        raise Exception(f"given type bean not found. type:{typ} classes:{classes}")
    return wrapper

@take
def getInstance(typ: type) -> Any:
    return typ

if __name__ == "__main__":
    @register
    def testStr() -> str:
        return "aaa"

    testStr()

    class Test():
        test: str = getInstance(str)

    print(Test().test)
