from typing import Any, Callable, Dict, List, Union

classes: Dict[str, Dict[str, Any]] = {}

def register(func: Callable[[], Any]) -> Callable:
    def wrapper(*args, **kwargs):
        # DIコンテナに登録するインスタンスを取得
        instanceToBeAdded: Any = func(*args, **kwargs)

        # __qualname__でフルのクラス名を取得
        instanceClassName = type(instanceToBeAdded).__qualname__

        # インスタンスを生成したデコレータのついた関数の名前を取得
        functionName = func.__name__

        # 既に登録されているインスタンスの辞書を取得。まだ何も登録されていない場合は空の辞書になる
        # この辞書は 関数名 to インスタンス
        instanceDictOfSpecifiedClass: Dict[str, Any] = {}
        if instanceClassName in classes:
            instanceDictOfSpecifiedClass.update(classes[instanceClassName])

        # 同名の関数を通じて登録されたインスタンスがあれば後勝ち
        instanceDictOfSpecifiedClass[functionName] = instanceToBeAdded

        # 登録
        classes[instanceClassName] = instanceDictOfSpecifiedClass
    return wrapper

def take(func: Callable[[type, Union[str, None]], Any]) -> Callable:
    def wrapper(*args, **kwargs):
        typ: type = args[0]
        qualifier: Union[str, None] = args[1]
        # 与えられた型名が辞書に登録されているかチェック
        if typ.__name__ in classes:
            instanceDictOfSpecifiedClass: Dict[str, Any] = classes[typ.__qualname__]

            instanceList: List[Any] = list(instanceDictOfSpecifiedClass.values())

            # 対象の型のインスタンスが一つしかなければ、名前にかかわらずそのインスタンスを返す
            if len(instanceList) == 1:
                # 念のため本当に与えられた型のインスタンスかどうかチェック
                if isinstance(instanceList[0], typ):
                    return instanceList[0]
            # 対象の型のインスタンスが複数あれば、指定の名前を持っているインスタンスを返す
            # インスタンスがない場合もこのブロックに入るがこの後一致することはないので問題ない
            else:
                # 与えられた名前が辞書にあるかチェック
                if qualifier in instanceDictOfSpecifiedClass.keys():
                    # 念のため本当に与えられた型のインスタンスかどうかチェック
                    if isinstance(instanceDictOfSpecifiedClass[qualifier], typ):
                        return instanceDictOfSpecifiedClass[qualifier]
        # インスタンスが見つからない
        raise Exception(f"given type bean not found. type:{typ}, qualifier:{qualifier}, classes:{classes}")
    return wrapper

@take
def getInstance(typ: type, qualifier: Union[str, None]) -> Any:
    pass

if __name__ == "__main__":
    class Ins():
        test: str = "aaa"

    @register
    def testIns() -> Ins:
        return Ins()

    @register
    def testStr() -> str:
        return "aaa"

    @register
    def testStr2() -> str:
        return "bbb"

    testIns()
    testStr()
    testStr2()

    class Test():
        test: Ins = getInstance(Ins, None)
        test2: str = getInstance(str, "testStr")

    print(Test().test, Test().test2)
