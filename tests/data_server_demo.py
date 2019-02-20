# coding=utf-8
from flask_jsonrpc.proxy import ServiceProxy

if __name__ == '__main__':
    # coding=utf-8
    url = "http://120.77.182.188:3306/data"
    server = ServiceProxy(service_url=url)
    # get guide text
    result = server.file.get_guide_text("40")
    print(result)
    # add callback
    callback_url = "http://....."
    result = server.file.register(callback_url, "demo")
    print(result)
    # change callback
    id = result["result"]
    new_callback_url="http://new"
    result = server.file.register(new_callback_url, "demo", id)
    print(result)
