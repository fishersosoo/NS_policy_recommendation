# coding=utf-8
import json
import os
import sys

sys.path.append("/home/web/NS_policy_recommendation/ns_ai_system")
from condition_identification.predicate_extraction.findName import FindName
from service.file_processing import get_text_from_doc_bytes

if __name__ == '__main__':
    result = dict(sentence=[], word=[])
    path = sys.argv[1]
    files_path = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    count = 0
    for file_path in files_path:
        with open(file_path, "rb") as doc_file:
            text = get_text_from_doc_bytes(doc_file.read())
            # fn = FindName()
            with open(os.path.join(path, f"{count}.txt"), "w") as txt:
                txt.write(text)
            # content = fn.find_condition_by_str(text)
            # print(content)
        count += 1
        print(f"done:{count}/{len(files_path)}")
    with open(os.path.join(path, "result.json"),"w") as json_file:
        json.dump(result, json_file)
