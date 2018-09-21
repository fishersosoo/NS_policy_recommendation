from jinja2 import Template
from conf import project
import sys
import os


def render(project):
    with open(os.path.join(sys.argv[1], "index.html"), "r") as f:
        template = Template(f.read())
    project_dir = os.path.join(sys.path[0], project)
    file_check(project_dir, [], [])
    rst = template.render(automodules=file_check(project_dir, [], []))
    with open(os.path.join(sys.argv[1], "index.rst"), "w") as f:
        f.write(rst)


def file_check(file_path, cur_module, modules):
    name = str(os.path.split(file_path)[-1])
    if name[:2] == "__":
        return modules
    # print(name)
    if os.path.isdir(file_path) is not True:
        # file
        if os.path.splitext(name)[-1] == ".py":
            cur_module = cur_module + [os.path.splitext(name)[0]]
            modules.append('.'.join(cur_module))
            return modules
        return modules
    else:
        # dir
        for item in os.listdir(file_path):
            item_path = os.path.join(file_path, item)
            modules = file_check(item_path, cur_module + [name], modules)
        cur_module = cur_module + [name]
        # print(cur_module)
        modules.append('.'.join(cur_module))
        return modules


if __name__ == "__main__":
    import os
    import sys

    sys.path.insert(0, os.path.abspath('..'))
    render(project)
