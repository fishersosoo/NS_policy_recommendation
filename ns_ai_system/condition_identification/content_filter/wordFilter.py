def promiseFilter(sentence):
    if "承诺" in sentence:
        return False
    return True

def tiaojianFilter(sentence):
    if "：" in sentence and '条件' in sentence:
        return False
    return True