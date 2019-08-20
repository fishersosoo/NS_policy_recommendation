def promiseFilter(sentence):
    if "承诺" in sentence:
        return True
    return False

def tiaojianFilter(sentence):
    if "：" in sentence and '条件' in sentence:
        return True
    return False