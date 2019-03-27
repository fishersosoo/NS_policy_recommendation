from condition_identification.name_entity_recognition.util import cos_sim


def _get_fields(field_file):
    field = set()
    with open(field_file, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if line != '':
                field.add(line)
    return field


class Field(object):
    def __init__(self, field_file):
        """
        :param field_file: 指代候选的字段
        """
        self.field = _get_fields(field_file)
        self.field_dict = {}

    def compare_similarity(self, line, bc):
        max_value = 0
        max_word = ''
        for word in self.field:
            word = word.strip()
            flag = False
            for w in word:
                if w in line:
                    flag = True
                    break
            if flag:
                value = cos_sim(bc.encode([line]), bc.encode([word]))
                if max_value < value:
                    max_value = value
                    max_word = word
        return max_value, max_word

    def construct_field_dict(self, regs, bc):
        for line in regs:
            max_value, max_word = self.compare_similarity(line, bc)
            if max_word != '' and max_value > 0.945:
                self.field_dict[line] = max_word
        return self.field_dict

    def get_field_dict(self):
        return self.field_dict
