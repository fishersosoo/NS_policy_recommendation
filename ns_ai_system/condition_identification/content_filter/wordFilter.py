def promiseFilter(sentence):
    if "承诺" in sentence:
        return True
    return False

def tiaojianFilter(sentence):
    if ("：" in sentence and '条件' in sentence) or('条件' in sentence and len(sentence)<=7):
        return True
    return False