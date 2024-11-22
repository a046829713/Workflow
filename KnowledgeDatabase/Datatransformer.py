import re
class Datatransformer():
    def find_department_path(self, department_structure, target, path=[]):
        """ to get department path"""
        for department, sub_departments in department_structure.items():
            current_path = path + [department]
            if department == target:
                return current_path
            if sub_departments:
                result = self.find_department_path(sub_departments, target, current_path)
                if result:
                    return result
        return []

    def clean_unit(self, x):
        if "組" in x:
            data = re.search(r'.*課([\u4e00-\u9fa5]+組)',x)
            if data:
                return data.group(1)
        
        if '課' in x:
            data = re.search(r'.*部([\u4e00-\u9fa5]+課)',x)
            if data:
                return data.group(1)

        return x