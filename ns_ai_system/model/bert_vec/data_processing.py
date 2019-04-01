# coding=utf-8
from concurrent.futures import ThreadPoolExecutor

from model.bert_vec.tokenization import convert_to_unicode


def _convert_to_feature(text, max_seq_len, tokenizer):
    """
    将字符串转化为id，并补全到最大长度

    Args:
        text:
        max_seq_len:
        tokenizer:

    Returns:

    """
    token = ["[CLS]"]
    token.extend(tokenizer.tokenize(text))
    if len(token) > max_seq_len - 1:
        token = token[0:(max_seq_len - 1)]
    token.append("[SEP]")
    input_ids = tokenizer.convert_tokens_to_ids(token)
    input_len = len(input_ids)
    while len(input_ids) < max_seq_len:
        input_ids.append(0)
    assert len(input_ids) == max_seq_len
    return input_ids, input_len


def convert_to_ids(strs, max_seq_len, tokenizer):
    """
    将多个字符串转换为id

    Args:
        tokenizer:
        strs: [str]. 字符串序列
        max_seq_len: int. 字符串最大长度

    Returns:
        list, shape: [len(strs), max_seq_len]
    """
    ids = []
    input_lens = []
    futures = []
    with ThreadPoolExecutor(16) as executor:
        for one in strs:
            futures.append(
                executor.submit(_convert_to_feature, convert_to_unicode(one), max_seq_len, tokenizer))
    i = 0
    for future in futures:
        a, b = future.result()
        if i == 0:
            print(a, b)
            i += 1
        ids.append(a)
        input_lens.append(b)
    return ids
