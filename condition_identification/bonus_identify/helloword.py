from html_parser import HtmlParser

key_word=['奖励','补贴','补助','资助','支持']

def search_key(X):
    for key in key_word:
        if key in X:
            print(X)
            break;



if __name__ == '__main__':
    html = HtmlParser()
    file = open(r'F:\实验室项目\南沙\NS_policy_recommendation\res\doc\html\广州南沙新区(自贸片区)促进科技创新产业发展扶持办法｜广州市南沙区人民政府.html',
                encoding='utf8')
    t = html.load_file(file)
    e = html.parse_document(t)
    file.close()
    print(e)
    print(list(t))
