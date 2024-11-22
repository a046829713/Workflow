# 所有的模板語言過濾器自訂義的都放在這裡


from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def to_float(value):
    try:
        return float(value)
    except ValueError:
        return value  # 如果转换失败，返回原始值

@register.filter
def replace_linebreaks(value):
    if isinstance(value,str):
        return mark_safe(value.replace('\n', '<br>'))
    else:
        return value


@register.filter(name='replace_special_mark')
def replace_special_mark(value: list):
    """將[] 從裡面移除 """

    # 如果傳進來的都沒有東西
    if not value:
        return ''
    
    if isinstance(value, str) :
        if "[" not in value and "]" not in value:
            value = [value]
        else:            
            value = json.loads(value.replace("'",'"'))
        
    out_str = ','
    return out_str.join(value)


@register.filter(name='get_element')
def get_element(value: list, arg):
    """
        自訂義模板語言

        value (list):Example 1 :['其它年資', '1'] Example 2 :['不拘', '']
            template like this : <option value="不拘" {% if form_data.年資|get_element:0 == "不拘" %}selected{% endif %}>不拘</option>
    """
    try:
        return value[arg]
    except IndexError:
        return None


@register.filter(name='get')
def get(dictionary, key):
    return dictionary.get(key)



@register.simple_tag
def get_matched_value(name_map, prod_no):
    return name_map.get(prod_no)