from abc import ABC, abstractmethod


class AbstractObject(ABC):
    @abstractmethod
    def attributes(self):
        pass

    @abstractmethod
    def rule(self):
        pass

    @abstractmethod
    def description(self):
        pass


class Papertube(AbstractObject):
    def __init__(self,post_data:dict) -> None:
        self.post_data = post_data
        self.attributes()
        self.rule()
        self.merge_result_consume()

    def attributes(self):
        self.triImpellerSilencer = self.post_data.get('triImpellerSilencer')  # 樣式
        self.threeimpeller_select = self.post_data.get('threeimpeller_select') # 三葉輪附加紙管
        self.papertubelining = self.post_data.get('papertubelining')# 紙管內俓
        self.filminnerdiameter = self.post_data.get('filminnerdiameter') # 膠膜內徑
        self.filmlength = self.post_data.get('filmlength') # 紙管長度
        self.Threeimpellerlengths = self.post_data.get('Threeimpellerlengths') # 三葉輪長度
        self.result =[]
        self.consume = {}
        
    def description(self):
        return '這是用來判斷紙管(膠膜)'
    
    def rule(self):
        # {'triImpellerSilencer': '管塞', 'threeimpeller_select': '',
        # 'papertubelining': '38mm凸點', 'filminnerdiameter': '',
        # 'filmlength': '450mm', 'Threeimpellerlengths': ''}
        
        out_prod_num =''
        if self.triImpellerSilencer == '管塞':
            if self.papertubelining == '37mm凸點' and self.filmlength ==  '450mm':
                out_prod_num='W2020-38V'
        else:
            pass
        
        self.result.append(out_prod_num)
        
    def merge_result_consume(self):        
        out_dict ={}
        for each_prod_no in self.result:
            if each_prod_no in self.consume:
                out_dict.update({each_prod_no:self.consume[each_prod_no]})
            else:
                out_dict.update({each_prod_no:1})            
       
        self.mergedata = out_dict
        
class Cover(AbstractObject):
    def __init__(self,post_data:dict) -> None:
        self.post_data = post_data
        self.attributes()
        self.rule()
        self.merge_result_consume()
    def attributes(self):
        # 可選項目
        # 上底蓋 下底蓋 上頂蓋 下頂蓋
        # {'csrfmiddlewaretoken': 'qwffBbbzGGyD090jx0dr63s4U7oKrNeSVLtm0FHiyQd9LPWQeVDpfIEOSWM3yVbU',
        # '': '紅',
        # '': '紅',
        # '': '紅',
        # '': '紅',
        # '': '',
        # '': 'VMAXX',
        # '': '有'} 
        self.up_buttom_cover_color = self.post_data.get('up_buttom_cover_color')  
        self.down_buttom_cover_color = self.post_data.get('down_buttom_cover_color')  
        self.up_top_cover_color = self.post_data.get('up_top_cover_color')  
        self.down_top_cover_color = self.post_data.get('down_top_cover_color')  
        self.up_top_cover_tag = self.post_data.get('up_top_cover_tag')  
        self.down_top_cover_tag = self.post_data.get('down_top_cover_tag')  
        self.magnet = self.post_data.get('magnet')  

        
        self.result =[]
        self.consume = {}
        
    def description(self):
        return '這是用來判斷上下蓋的'

    def rule(self):        
        if self.up_top_cover_tag =='VMAXX' and self.up_top_cover_color =='紅':        
            self.result.append('W6160RU-01V')
        if self.down_top_cover_tag =='VMAXX' and self.down_top_cover_color =='紅':        
            self.result.append('W5150RU-01V')
        
        if self.up_top_cover_color =='紅' :        
            self.result.append('W5150R-41')
            
        if self.down_buttom_cover_color =='紅' :        
            self.result.append('W6580R-02')
            
    def merge_result_consume(self):        
        out_dict ={}
        for each_prod_no in self.result:
            if each_prod_no in self.consume:
                out_dict.update({each_prod_no:self.consume[each_prod_no]})
            else:
                out_dict.update({each_prod_no:1})            
       
        self.mergedata = out_dict
        
class Productno(AbstractObject):
    def __init__(self,post_data:dict) -> None:
        self.post_data = post_data
        self.attributes()
        self.rule()
        self.merge_result_consume()
        
    def attributes(self):
        # 可選項目
        self.productnotypes = self.post_data.get('productnotypes') # 鐵條款式
        self.tensions =self.post_data.get('tensions') # 鐵條張力
        self.result =[]
        self.consume = {}
        
    def description(self):
        return '這是用來判斷鐵條款式的'

    def rule(self):
        if self.productnotypes == '組合款':
            self.result.extend(['W6580-07F','W758F-36','31-501','32-M505','143-M05-20S','W5160-23','15F03*R-M04-15S'])
            
            
        if self.tensions == '調節':
            self.result.extend(['W6580-38','4-M2029-15H','44-M223-330-A','4-M2333-10H','32-M808','W5160-39','W5160-24','4-801','44-M092-430','W5360-41','16-M08-08H','4-M1323-20Z','41-M223-330'])
        
        
        # 變更數量
        if '31-501' in self.result:
            self.consume.update({"31-501":10})        
        if '143-M05-20S' in self.result:
            self.consume.update({"143-M05-20S":10})            
        if '15F03*R-M04-15S' in self.result:
            self.consume.update({"15F03*R-M04-15S":4})            
        if '4-M2029-15H' in self.result:
            self.consume.update({"4-M2029-15H":2})            
        if '44-M223-330-A' in self.result:
            self.consume.update({"44-M223-330-A":2})
        if '4-M2333-10H' in self.result:
            self.consume.update({"4-M2333-10H":5})
        if 'W5160-24' in self.result:
            self.consume.update({"W5160-24":2})

    def merge_result_consume(self):        
        out_dict ={}
        for each_prod_no in self.result:
            if each_prod_no in self.consume:
                out_dict.update({each_prod_no:self.consume[each_prod_no]})
            else:
                out_dict.update({each_prod_no:1})            
       
        self.mergedata = out_dict
            
class Roller(AbstractObject):
    def __init__(self,post_data:dict) -> None:
        self.post_data = post_data
        self.attributes()
        self.rule()
        self.merge_result_consume()
        
    def attributes(self):
        # 'rollertypes': '直溝灰輪'
        self.rollertypes = self.post_data.get('rollertypes')
        self.result =[]
        self.consume = {}
        
    def description(self):
        return '這是用來判斷滾輪的'

    def rule(self):
        if self.rollertypes == '直溝灰輪':
            self.result.extend(['W658FVS-08S','W658FVS-09S'])

    def merge_result_consume(self):        
        out_dict ={}
        for each_prod_no in self.result:
            if each_prod_no in self.consume:
                out_dict.update({each_prod_no:self.consume[each_prod_no]})
            else:
                out_dict.update({each_prod_no:1})            
       
        self.mergedata = out_dict
        
class Foam(AbstractObject):
    def __init__(self,post_data:dict) -> None:
        self.post_data = post_data
        self.attributes()
        self.rule()
    
    def attributes(self):
        # 可選項目
        self.foam_is_have = self.post_data.get('foam_is_have')
        self.result =[]

    def description(self):
        return '這是用來判斷泡棉的'
    
    def rule(self):
        pass

class Handle(AbstractObject):
    def __init__(self,post_data:dict) -> None:
        self.post_data = post_data
        self.attributes()
        self.rule()
        
    def attributes(self):
        # 可選項目
        self.handletype = self.post_data.get('handletype')
        self.handlecolor = self.post_data.get('handlecolor')        
        self.result =[]


    def description(self):
        return '這是用來判斷手柄的'

    def rule(self):
        pass
    
class Bendpipe(AbstractObject):
    def __init__(self,post_data:dict) -> None:
        self.post_data = post_data
        self.attributes()
        self.rule()
        
    def attributes(self):
        # 可選項目
        self.bendpipecolor = self.post_data.get('bendpipecolor')
        self.result =[]

    def description(self):
        return '這是用來判斷彎管的'

    def rule(self):
        pass

    
class Pulltheblackball(AbstractObject):
    def __init__(self,post_data:dict) -> None:
        self.post_data = post_data
        self.attributes()
        self.rule()
        self.merge_result_consume()
        
    def attributes(self):
        # 可選項目
        self.is_have = self.post_data.get('pulltheblackballis_have')
        self.result = []
        self.consume = {}

    def description(self):
        return '這是用來判斷拉把黑球的'

    def rule(self):
        if self.is_have == '有':
            self.result.extend(['W6580-76','4-M0816-05H','P1200-15','5-S8','31L-M08-06Z','W5180-21','W5160-22','121-M08-30H','4-M0823-15H'])

    def merge_result_consume(self):        
        out_dict ={}
        for each_prod_no in self.result:
            if each_prod_no in self.consume:
                out_dict.update({each_prod_no:self.consume[each_prod_no]})
            else:
                out_dict.update({each_prod_no:1})            
       
        self.mergedata = out_dict
        
class Gear(AbstractObject):
    def __init__(self,post_data:dict) -> None:
        self.post_data = post_data
        self.attributes()
        self.rule()
        self.merge_result_consume()
        
    def attributes(self):
        # {'csrfmiddlewaretoken': 'qpusaIegdWeqbVFENbKeehxCCPMlKbmrydRdYgDXjX0OPKs5Pjv20bFyOrp2fqp4',}
        # 可選項目
        self.percent =  self.post_data.get('percent')
        self.result = []
        self.consume = {}
        
    def description(self):
        return '這是用來判斷齒輪的'

    def rule(self):
        if self.percent == '20%':
            self.result.extend(['W5150-60E','W5150-50E'])

        # 變更數量
        if 'W5150-60E' in self.result:
            self.consume.update({"W5150-60E":2})        
        if 'W5150-50E' in self.result:
            self.consume.update({"W5150-50E":2})
                        
    def merge_result_consume(self):        
        out_dict ={}
        for each_prod_no in self.result:
            if each_prod_no in self.consume:
                out_dict.update({each_prod_no:self.consume[each_prod_no]})
            else:
                out_dict.update({each_prod_no:1})            
       
        self.mergedata = out_dict

class Spring(AbstractObject):
    def attributes(self):
        # 可選項目
        self.strong = ['強', '中', '弱']

        # 實際項目
        self.target_strong = None

    def description(self):
        return '這是用來判斷彈簧的'



class ModelMergeTool():
    def __init__(self) -> None:
        """
            1. 應該要有驗證的功能(確保吐出的料號無誤)
            2. 
            
        """
        self.result =[]
        self.consume = {}
    
    def merge_Foam_Handle_Bendpipe(self,foam:Foam,handle:Handle,bendpipe:Bendpipe):
        if foam.foam_is_have == '有' and handle.handletype =='標準' and handle.handlecolor =='黑' and bendpipe.bendpipecolor=='紅黑':
            self.result.extend(['W658F-03','15F03*R-M04-15S'])
        
        
        if '15F03*R-M04-15S' in self.result:
            self.consume.update({'15F03*R-M04-15S':2})
        
        self.merge_result_consume()
        
    def merge_result_consume(self):        
        out_dict ={}
        for each_prod_no in self.result:
            if each_prod_no in self.consume:
                out_dict.update({each_prod_no:self.consume[each_prod_no]})
            else:
                out_dict.update({each_prod_no:1})            
       
        self.mergedata = out_dict
    
    def rule(self,*args):        
        for i in args:
            print(i.description(),i.mergedata)
            print('*'*120)
        print(self.mergedata)