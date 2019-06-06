# coding=utf-8
def getNumofCommonSubstr(str1, str2):
    """python实现求两个字符串的最长公共子串方法

    用动态规划法求两个字符串的最长公共子串

     Args:
         str1: str
         str2: str
     Returns:
         str1str1[p - maxNum:p]: str,最长的公共子串
         maxNum: int  ，公共子串长度

    """
    lstr1 = len(str1)
    lstr2 = len(str2)
    record = [[0 for i in range(lstr2 + 1)] for j in range(lstr1 + 1)]  # 多一位,全零初始化二维数组
    maxNum = 0      # 最长匹配长度
    p = 0  # 匹配的起始位
    for i in range(lstr1):
        for j in range(lstr2):
            if str1[i] == str2[j]:     # 相同则累加
                record[i + 1][j + 1] = record[i][j] + 1
                if record[i + 1][j + 1] > maxNum:
                    maxNum = record[i + 1][j + 1]     # 获取最大匹配长度
                    p = i + 1    # 记录最大匹配长度的终止位置
    return str1[p - maxNum:p], maxNum

def cmp_stringlist(sl1,sl2):
    sl1 = set(sl1)
    sl2 = set(sl2)
    if len(sl1) != len(sl2):
        return False
    else:
        c = [x for x in sl1 if x in sl2]
        if len(c) != len(sl1):
            return False
        else:
            return True


if __name__ == '__main__':
    print(cmp_stringlist(['sds','sds1'],['sds1','sds']))