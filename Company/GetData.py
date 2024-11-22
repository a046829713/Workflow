from .Database.SQL_operate import DB_operate
from anytree import Node
from anytree.exporter import DictExporter


def get_employee_children(data: dict):
    """
        取得公司上司下屬之關係
    """
    def general_node(root_name: str, parent_node):
        children_node_list = [subordinate for subordinate,
                              boss in data.items() if boss == root_name]
        for item in children_node_list:
            children_node = Node(item, parent=parent_node)
            general_node(item, children_node)

    # 第一個節點
    root_name = '游陳秀滿'
    root = Node(root_name)  # 成品件為1

    # 執行
    general_node(root_name, root)

    exporter = DictExporter()
    return exporter.export(root)


def parser_target_data(data: dict, target_name: str):
    """
    取得轄下資料

    Args:
        data (dict): {'name': '游陳秀滿', 'children': [{'name': '游大城', 'children': [{'name': '游英玉', 'children': [{'name': '莊玉英', 'children': [{'name': '陳綾利'}, {'name': '許伽綾'}, {'name': '林佳慧'}, {'name': '洪清香'}]}, {'name': '邱品諭'}, {'name': '游清惠', 'children': [{'name': '賴佩菁'}, {'name': '林育萍'}, {'name': '陳俐岑'}, {'name': '黃淑媛'}, {'name': '劉彥伶'}, {'name': '吳儀琳'}, {'name': '何貞儀'}]}, {'name': '許政宏'}, {'name': '陳保宏', 'children': [{'name': '林 智堅'}, {'name': '詹筑云'}, {'name': '羅一修'}]}, {'name': '曹明湖', 'children': [{'name': '張美芳', 'children': [{'name': '黃惠萍', 'children': [{'name': ' 張家毓'}, {'name': '魏瑜慧'}, {'name': '林筱庭'}, {'name': '蔡協津'}, {'name': '傅洸琳'}, {'name': '邱霆芳'}]}, {'name': '洪萱樺'}, {'name': '張仕育', 'children': [{'name': '吳玉皎'}, {'name': '蔡帛璟'}, {'name': '李家鄉'}, {'name': '羅文妤'}, {'name': '蔡名傑'}, {'name': '粘伯園'}, {'name': '丁時中'}, {'name': '洪鈺婷'}, {'name': '蔡江祥'}, {'name': '林哲佑'}, {'name': '連哲聖'}]}]}]}, {'name': '張璦麟', 'children': [{'name': '陳意萱'}]}, {'name': '李弘啓', 'children': [{'name': '張寶隆', 'children': [{'name': '林瑞菊', 'children': [{'name': '蕭永泰'}, {'name': '賴淑珍'}, {'name': '葉承峰'}, {'name': '陳昭茹'}, {'name': '阮氏蘭英'}, {'name': '阮玉德'}, {'name': '阮氏娥'}, {'name': '高氏嚴'}, {'name': '鄧文財弟'}, {'name': '黃氏莊'}, {'name': '黃氏青香'}, {'name': '阮氏花'}, {'name': '陳雅盈'}, {'name': '阮氏草'}, {'name': '林家希'}, {'name': '陳佳珮'}, {'name': '古玉璇'}, {'name': '謝翠香'}, {'name': '黃宜蓁'}, {'name': '邱欣翊'}, {'name': '葉惠萍'}, {'name': '周羽柔'}, {'name': '廖顯仁'}, {'name': '游依華'}, {'name': '楊秀青'}]}, {'name': '陳政益', 'children': [{'name': '陳桂娟'}, {'name': '阮氏玄'}, {'name': '阮世宇'}, {'name': '蔡佩娟'}, {'name': '劉士加'}, {'name': '阮文鹿'}, {'name': '吳佳靜'}, {'name': '張庭銚'}, {'name': '羅悅慈'}]}, {'name': '葉時甫', 'children': [{'name': '吳月嬌'}, {'name': '鄭育宗'}, {'name': '黎文明'}, {'name': '梁氏翠絨'}, {'name': '陳俊良'}, {'name': '何坤滉'}, {'name': '賴家慶'}, {'name': '劉于卉'}, {'name': '鄭宜軒'}, {'name': '張黃子琳'}, {'name': '黃琳鈴'}, {'name': '吳亦諺'}, {'name': '王鋕浧'}, {'name': '張雅婷'}, {'name': '林裕東'}]}]}]}, {'name': '游登期', 'children': [{'name': '王誠億'}, {'name': '胡智源'}, {'name': '林昆輝', 'children': [{'name': '林秋宏'}, {'name': '王青'}, {'name': '陳為強'}]}, {'name': '蕭仕澄'}, {'name': '何昆璋'}, {'name': '鍾育眠'}, {'name': '邱紹龍'}, {'name': '吳怡葶'}, {'name': '張雯晴'}, {'name': '呂展旻'}]}, {'name': '游鎮僑', 'children': [{'name': '官原吉'}, {'name': '洪振翔'}, {'name': '柳宥蓁'}, {'name': '張皓雯'}, {'name': '王俊淙'}, {'name': '陳忠城'}, {'name': '李宜珍'}, {'name': '劉安邦'}, {'name': '鄭振佑'}, {'name': '武春燕'}, {'name': '劉立威'}, {'name': '黎文善'}, {'name': '黃志彰'}, {'name': '武青松'}, {'name': '林詩涵'}, {'name': '阮明孝'}, {'name': '蔡淑如'}, {'name': '邱裕能'}, {'name': '吳家成'}, {'name': '曾苗耕'}, {'name': '阮 公榮'}, {'name': '陳光河'}]}]}]}]}
        target_name (str): 游英玉
    """
    def _parser_target_data(_data: dict, target_name: str):
        for key, val in _data.items():
            if key == 'name' and val == target_name:
                return _data['children'] if 'children' in _data else []

            if key == 'children':
                for each_data in val:
                    result = _parser_target_data(each_data, target_name)
                    if result:
                        return result
    out_result = _parser_target_data(data, target_name)

    if out_result is None:
        return []
    else:
        def _get_name_data(target_datas: list):
            name_datas = []

            def _parser_data(_data):
                for key, val in _data.items():
                    if key == 'name':
                        name_datas.append(val)

                    if key == 'children':
                        for _each_data in val:
                            _parser_data(_each_data)

            for _i in target_datas:
                _parser_data(_i)

            return name_datas

        return _get_name_data(out_result)


def get_employee_map(target_name: str):
    """_summary_

    Args:
        target_name (str): 游英玉

    Returns:
        _type_: _description_
    """
    employee = DB_operate(sqltype='MIS').get_pd_data(
        "select * from Company_employee")
    
    work_id_data = {value['name']: value['worker_id']
                    for key, value in employee[['worker_id', 'name']].to_dict('index').items()}
    
    employee = employee[['name', 'supervisor_name']]

    employee.set_index('name', inplace=True)
    data = employee.to_dict('index')

    parser_data = {key: val['supervisor_name'] for key, val in data.items()}

    subordinate_names = parser_target_data(
        get_employee_children(parser_data), target_name)

    return [work_id_data[each_name] for each_name in subordinate_names]
