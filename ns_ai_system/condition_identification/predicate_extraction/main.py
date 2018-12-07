from condition_identification.predicate_extraction.tupletree_api import construct_tupletree_by_file
from condition_identification.predicate_extraction.tupletree_api import construct_tupletree_by_bytestr
if __name__ == '__main__':
    filename = r'C:\Users\edward\Desktop\指南们\26.txt'
    tree = construct_tupletree_by_file(filename)

    # bytestr = ""
    # tree = construct_tupletree_by_bytestr(bytestr)

    #print(tree.get_all_nodes())
    for node in tree.get_all_nodes():
        print(node['TYPE']+" : "+node['CONTENT'])

