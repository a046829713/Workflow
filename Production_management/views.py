from django.http import FileResponse
from django.http import HttpResponse, Http404
from datetime import date
from django.core.cache import cache
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from workFlow.DataTransformer import querydict_to_dict
from .DataTransformer import Transformer
from dateutil.rrule import rrule, MONTHLY
import pandas as pd
from .Slow_Moving import Slow_Moving
from .models import HistoryDailyConsume
import json
from django.core.paginator import Paginator
import time
import numpy as np
import sys
from Company.utils.Debug_tool import get_size
from . import common
from Company.models import Form
from io import BytesIO
from django.urls import reverse
from .TreeTransformer import TreeTransformer
from django.http import JsonResponse
# Create your views here.


class ValueStreamMapView(LoginRequiredMixin, View):
    template_name = 'Production_management/value_stream_map.html'

    def get(self, request, *args, **kwargs):
        # 這裡放置需要傳遞到模板的上下文資料
        context = {
            'data': '這是 Value Stream Map 的示例數據',
            "treeApi" :reverse('treeApi'),
            "treeApiCheckTime" :reverse('treeApiCheckTime'),
            "getopenmaterials" :reverse('getopenmaterials')
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # 可以根據需求實作 post 方法來處理表單提交或其他動作
        return render(request, self.template_name)


class Line_Chart_View(LoginRequiredMixin, View):
    def get_min_data(self, prod_no):
        SM = Slow_Moving()
        SM.min_main(prod_no)
        product_last_day_data = cache.get('product_last_day_data', None)
        if product_last_day_data is None:
            product_last_day_data = Transformer().get_product_last_day()
            cache.set('product_last_day_data', product_last_day_data, 3000)
        df = SM.count_NoM(product_last_day_data)
        return df

    def get_cache(self):
        HDC_data = cache.get('HDC_data', None)
        # {date: 2007-05-20, close: 111.98}

        if HDC_data is None:
            all_data = HistoryDailyConsume.objects.all().values()

            cout_size = 0
            for each in all_data:
                cout_size += sys.getsizeof(each['date'])  # Bytes
                cout_size += sys.getsizeof(each['data'])  # Bytes
            print(cout_size)
            # test
            # obj = HistoryDailyConsume.objects.latest('date')
            # all_data  = [{'date':obj.date,"data":obj.data}]

            # print(all_data)
            HDC_data = []
            for _data in all_data:
                data = json.loads(_data['data'])
                HDC_data.append({'date': str(_data['date']), 'data': data})

            cache.set('HDC_data', HDC_data, 3000)

        return HDC_data

    def change_float_to_str(self, df):
        """
            為了避免前端渲染數字問題一率轉換成字串
        """
        # 更改畫面渲染樣式
        df['日用量'] = df['日用量'].apply(
            lambda x: 'nan' if x is None else f"{x:.2f}")
        df['SlowM(年)'] = df['SlowM(年)'].apply(lambda x: f"{x:.2f}")
        df['NoM(年)'] = df['NoM(年)'].apply(lambda x: f"{x:.2f}")

    def post(self, request):
        post_data = querydict_to_dict(request.POST)
        prod_no = post_data.get('prod_no')
        HDC_data = self.get_cache()
        df = self.get_min_data(prod_no)
        all_data = []
        for _data in HDC_data:
            new_map = {}
            new_map['date'] = _data['date']
            new_map['consume'] = round(_data['data'][prod_no], 3)
            all_data.append(new_map)

        daily_data = json.loads(
            HistoryDailyConsume.objects.latest('date').data)
        df['日用量'] = df['PROD_NO'].apply(lambda x: daily_data.get(x))
        df['SlowM(年)'] = df['PROD_QTY'] / df['日用量'] / 250

        df.rename(columns={
            "PROD_NO": "料號",
            "PROD_NAME": "品名規格",
            "PROD_QTY": "庫存量",
            "PROD_CTS": "標準單位總成本",
            "PROD_U": "基本單位",
            "MBAT_QTY": "生產批量",
            "BULW_QTY": "MOQ",
            'STRG_NA': '倉庫名稱'
        }, inplace=True)

        df = df[['料號', '品名規格', '倉庫名稱', '庫存量', '標準單位總成本', '基本單位',
                 '生產批量', 'MOQ', '日用量', 'SlowM(年)', 'NoM(年)']]

        self.change_float_to_str(df)

        context = {
            'all_data': json.dumps(all_data),
            "data": df.values.tolist(),
            "columns": df.columns.tolist(),
        }

        return render(request, "Production_management/line_chart.html", context)


class Slow_moving_View(LoginRequiredMixin, View):
    def _quantity_check(self, x, target_quantity):
        """_summary_

        Args:
            quantity (str): 用來判斷使用者是否有篩選過庫存數量
            x (_type_): _description_

        Returns:
            _type_: _description_
        """
        if target_quantity == 'zero' and x == 0:
            return True
        elif target_quantity == 'greater_than_zero_no_nan' and x != 0:
            if np.isnan(x):
                return False
            return True
        elif target_quantity == 'greater_than_zero' and x != 0:
            return True
        return False

    def _year_check(self, x, lable_year):
        if lable_year == "less_than_1" and x <= 1:
            return True
        elif lable_year == "1_to_3" and x > 1 and x <= 3:
            return True
        elif lable_year == "3_to_5" and x > 3 and x <= 5:
            return True
        elif lable_year == "more_than_5" and x > 5:
            return True
        return False

    def change_float_to_str(self, df):
        """
            為了避免前端渲染數字問題一率轉換成字串
        """
        # 更改畫面渲染樣式
        df['日用量'] = df['日用量'].apply(
            lambda x: 'nan' if x is None else f"{x:.2f}")
        df['SlowM(年)'] = df['SlowM(年)'].apply(lambda x: f"{x:.2f}")
        df['NoM(年)'] = df['NoM(年)'].apply(lambda x: f"{x:.2f}")

    def get_cache(self):
        # 嘗試從緩存中獲取數據
        df = cache.get('Slow_Moving_df', None)
        # 如果緩存中沒有數據，則進行查詢並將其存入緩存
        if df is None:
            SM = Slow_Moving()
            SM.main()
            df = SM.count_NoM(Transformer().get_product_last_day())

            # 將數據存入緩存，並設置300秒過期
            cache.set('Slow_Moving_df', df, 3000)
        return df

    def save_csv(self, df):
        # 提供給使用者可以下載本次的資料內容
        # 將數據存入緩存，並設置300秒過期
        cache.set('slow_moving_query_df', df, 3000)

    def get(self, request):
        df = self.get_cache()
        # 當使用者第一次進入時，不管之前的session如何一律清空
        if request.GET.get('page', None) is None:
            request.session['filter_conditions'] = {}

        filter_conditions = request.session.get('filter_conditions', {})

        if filter_conditions:
            part_name_and_number = filter_conditions['part_name_and_number']
            quantity = filter_conditions['quantity']
            daily_quantity = filter_conditions['daily_quantity']

            # 條件過濾1 料號搜尋:
            if part_name_and_number:
                df = df.loc[df.apply(
                    lambda x: True if part_name_and_number in x['PROD_NO'] or part_name_and_number in x['PROD_NAME'] else False, axis=1)]
            if quantity:
                df = df.loc[df['PROD_QTY'].apply(
                    self._quantity_check, args=(quantity,))]

        daily_data = json.loads(
            HistoryDailyConsume.objects.latest('date').data)
        df['日用量'] = df['PROD_NO'].apply(lambda x: daily_data.get(x))
        df['SlowM(年)'] = df['PROD_QTY'] / df['日用量'] / 250

        if filter_conditions:
            SlowMyear = filter_conditions['SlowMyear']
            NoMyear = filter_conditions['NoMyear']

            if SlowMyear:
                df = df.loc[df['SlowM(年)'].apply(
                    self._year_check, args=(SlowMyear,))]

            if NoMyear:
                df = df.loc[df['NoM(年)'].apply(
                    self._year_check, args=(NoMyear,))]

            if daily_quantity:
                df = df.loc[df['日用量'].apply(
                    self._quantity_check, args=(daily_quantity,))]

        # sort_conditions
        if filter_conditions:
            slow_sort_direction = filter_conditions['slow_sort_direction']
            if slow_sort_direction == 'DESC':
                df = df.sort_values('SlowM(年)', ascending=False)
            if slow_sort_direction == 'ASC':
                df = df.sort_values('SlowM(年)', ascending=True)
            NoM_direction = filter_conditions['NoM_direction']
            if NoM_direction == 'DESC':
                df = df.sort_values('NoM(年)', ascending=False)
            if NoM_direction == 'ASC':
                df = df.sort_values('NoM(年)', ascending=True)

        print(df)
        df.rename(columns={
            "PROD_NO": "料號",
            "PROD_NAME": "品名規格",
            "PROD_QTY": "庫存總量(各倉別加總)",
            "PROD_CTS": "標準單位總成本",
            "PROD_U": "基本單位",
            "MBAT_QTY": "生產批量",
            "BULW_QTY": "MOQ",
            "SAFE_QTY": "安全庫存",
        }, inplace=True)

        df = df[['料號', '品名規格', '庫存總量(各倉別加總)', '標準單位總成本', '基本單位',
                 '安全庫存', '生產批量', 'MOQ', '日用量', 'SlowM(年)', 'NoM(年)']]

        self.change_float_to_str(df)
        self.save_csv(df)

        page = request.GET.get('page', 1)
        # 設置分頁
        paginator = Paginator(df, 10)  # 每頁顯示10條數據
        data_page = paginator.page(page)

        # 獲取當前頁的數據
        data_list = data_page.object_list

        context = {
            "data": data_list.values.tolist(),
            "columns": df.columns.tolist(),
            "page_obj": data_page,
            "part_name_and_number": filter_conditions.get('part_name_and_number', ""),
            "quantity": filter_conditions.get('quantity', ""),
            "SlowMyear": filter_conditions.get('SlowMyear', ""),
            "NoMyear": filter_conditions.get('NoMyear', ""),
            "slow_sort_direction": filter_conditions.get('slow_sort_direction', ""),
            "NoM_direction": filter_conditions.get('NoM_direction', ""),
            'data_len': len(df.index)
        }

        return render(request, "Production_management/Slow_moving.html", context)

    def post(self, request, *args, **kwargs):
        post_data = querydict_to_dict(request.POST)
        part_name_and_number = post_data.get('part_name_and_number')
        quantity = post_data.get('quantity')
        daily_quantity = post_data.get('daily_quantity')
        SlowMyear = post_data.get('SlowMyear')
        NoMyear = post_data.get('NoMyear')
        slow_sort_direction = post_data.get(
            'slow_sort_direction')  # sort條件 只會兩者存其1
        NoM_direction = post_data.get('NoM_direction')  # sort條件 只會兩者存其1

        request.session['filter_conditions'] = {
            'part_name_and_number': part_name_and_number,
            'quantity': quantity,
            'daily_quantity': daily_quantity,
            'SlowMyear': SlowMyear,
            'NoMyear': NoMyear,
            'slow_sort_direction': slow_sort_direction,
            'NoM_direction': NoM_direction,

        }

        # 调整 request 对象，设置 page 参数为 1
        request.GET = request.GET.copy()
        request.GET['page'] = '1'
        return self.get(request, *args, **kwargs)


class Dailyvalue(LoginRequiredMixin, View):
    def get(self, request):
        context = {

        }

        return render(request, "Production_management/dailyvalue.html", context)

    def post(self, request):
        merge_mean_daily_value = {}
        data = querydict_to_dict(request.POST)
        start_date = data['start_date']
        end_date = data['end_date']
        prod_name_and_number = data['prod_name_and_number']

        # 嘗試從緩存中獲取數據
        consume_data = common.get_cached_consume_data()

        # 根據條件篩選消耗數據
        consume_data = common.filter_consume_data(
            consume_data, prod_name_and_number)

        if start_date:
            # 取得每個物料的第一天
            result_dict = Transformer().get_product_first_day()
            Correction_dict = common.calculate_correction_dict(
                result_dict, start_date, end_date)
            sum_days_map = common.calculate_sum_days_map(
                consume_data, Correction_dict)
            consume_map = common.calculate_consume_map(
                consume_data, Correction_dict)
            merge_mean_daily_value = common.calculate_merge_mean_daily_value(
                sum_days_map, consume_map)

        details = {each_column: Transformer.get_workdays(
            # 給使用者參考這段期間每個月多少天數
            int(each_column[:4]), int(each_column[-2:])) for each_column in Transformer.get_month_range(start_date, end_date)}

        # 將個別的日期放入，讓前端可以渲染
        for key, value in merge_mean_daily_value.items():
            merge_mean_daily_value[key] = [value, sum_days_map[key]]

        print(merge_mean_daily_value)
        context = {
            'start_date': start_date,
            "end_date": end_date,
            "prod_name_and_number": prod_name_and_number if prod_name_and_number else '',
            "merge_mean_daily_value": merge_mean_daily_value,
            "ask_price": True,
            'details': details,
            "sum_days_map": sum_days_map
        }
        return render(request, "Production_management/dailyvalue.html", context)

    def save_data(self, start_date, end_date, prod_name_and_number, data):
        """
            先保存下來，讓程序不需要再重新計算
        """
        df = pd.DataFrame.from_dict(data, orient='index')
        df = df.rename(columns={0: "IntervalDailyUsage"})
        dailyvalue_askprice_data = cache.get('dailyvalue_askprice_data', None)

        new_entry = {
            'start_date': start_date,
            "end_date": end_date,
            "prod_name_and_number": prod_name_and_number,
            'data': df,
        }

        if dailyvalue_askprice_data is None:
            dailyvalue_askprice_data = [new_entry]
        else:
            # 檢查是否已存在相同的條目
            entry_exists = any(
                start_date == each_info['start_date'] and
                end_date == each_info['end_date'] and
                prod_name_and_number == each_info['prod_name_and_number']
                for each_info in dailyvalue_askprice_data
            )

            if not entry_exists:
                dailyvalue_askprice_data.append(new_entry)

        cache.set('dailyvalue_askprice_data', dailyvalue_askprice_data, 1500)


def download_csv_two(request):
    """
        用於查詢時間內所有日用量下載的
    """
    data = querydict_to_dict(request.GET)
    # {'start_date': ['2023-12-01'], 'end_date': ['2023-12-31'], 'prod_name_and_number': ['']}
    start_date = data['start_date']
    end_date = data['end_date']
    prod_name_and_number = data['prod_name_and_number']

    # 嘗試從緩存中獲取數據
    consume_data = common.get_cached_consume_data()

    # 根據條件篩選消耗數據
    consume_data = common.filter_time_split(consume_data, start_date, end_date)

    if start_date:
        # 取得每個物料的第一天
        result_dict = Transformer().get_product_first_day()
        Correction_dict = common.calculate_correction_dict(
            result_dict, start_date, end_date)
        sum_days_map = common.calculate_sum_days_map(
            consume_data, Correction_dict)
        consume_map = common.calculate_consume_map(
            consume_data, Correction_dict)
        merge_mean_daily_value = common.calculate_merge_mean_daily_value(
            sum_days_map, consume_map)

    # 將個別的日期放入，提供更多資料
    for key, value in merge_mean_daily_value.items():
        merge_mean_daily_value[key] = [
            value, start_date, end_date, sum_days_map[key], result_dict[key]]

    print(merge_mean_daily_value)

    df = pd.DataFrame.from_dict(merge_mean_daily_value, orient='index')

    # 一次性完成重命名操作
    df = df.rename(columns={
        0: "日用量",
        1: "查詢起始日期",
        2: "查詢結束日期",
        3: "產品實際使用週期(天)",
        4: "入庫日"
    })

    # 使用 BytesIO 將 Excel 存儲到內存中
    with BytesIO() as output:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=True, sheet_name='Sheet1')

        output.seek(0)  # 將指針設置為文件開頭

        # 創建 HTTP 回應，傳輸 Excel 文件
        response = HttpResponse(output.getvalue(
        ), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="dayvaluebymonth.xlsx"'

        return response


def download_csv(request, table_name: str):
    """
        控管資料下載
    """
    if table_name == 'consume_data':
        # 嘗試從緩存中獲取數據
        data = cache.get('consume_data', None)
        # 如果緩存中沒有數據，則進行查詢並將其存入緩存
        if data is None:
            data = Transformer().getconsume(datetype='month')
            data = Transformer.get_dayvalue_intervial(data)
            # 將數據存入緩存，並設置1500秒過期
            cache.set('consume_data', data, 1500)
        file_name = "dayvaluebymonth.csv"

    elif table_name == 'slow_moving_query_df':
        data = cache.get('slow_moving_query_df', None)
        if data is None:
            SM = Slow_Moving()
            SM.main()
            df = SM.count_NoM(Transformer().get_product_last_day())

            daily_data = json.loads(
                HistoryDailyConsume.objects.latest('date').data)
            df['日用量'] = df['PROD_NO'].apply(lambda x: daily_data.get(x))
            df['SlowM(年)'] = df['PROD_QTY'] / df['日用量'] / 250

            data = df.rename(columns={
                "PROD_NO": "料號",
                "PROD_NAME": "品名規格",
                "PROD_QTY": "庫存總量(各倉別加總)",
                "PROD_CTS": "標準單位總成本",
                "PROD_U": "基本單位",
                "MBAT_QTY": "生產批量",
                "BULW_QTY": "MOQ",
                "SAFE_QTY": "安全庫存",
            })

            # 將數據存入緩存，並設置300秒過期
            cache.set('slow_moving_query_df', data, 3000)

        file_name = "slow_moving_query.csv"
    elif table_name == 'allHeavyworkorderFormsummary':
        all_object = Form.objects.filter(form_name='重工單').exclude(
            result='').exclude(result='取回')

        data_list = []
        for each_data in all_object:
            data_list.append({
                'form_id': each_data.form_id,
                'application_date': each_data.application_date,
                'quantity': each_data.data['quantity'],
                'prod_no_before': each_data.data['prod_no_before'],
                'prod_name_before': each_data.data['prod_name_before'],
                'prod_no_after': each_data.data['prod_no_after'],
                'prod_name_after': each_data.data['prod_name_after'],
                'Heavy_industry_projects': each_data.data['Heavy_industry_projects'].replace('\r\n', ''),
                'rebuild_reason': each_data.data['rebuild_reason'].replace('\r\n', ''),
                'source_notes': each_data.data['source_notes'].replace('\r\n', ''),
            })
        # 將 data_list 轉換成 DataFrame
        df = pd.DataFrame(data_list)

        data = df.rename(columns={
            "form_id": "表單編號",
            "application_date": "申請時間",
            "quantity": "數量",
            "prod_no_before": "產品編號(重工前)",
            "prod_name_before": "品名規格(重工前)",
            "prod_no_after": "產品編號(重工後)",
            "prod_name_after": "品名規格(重工後)",
            "Heavy_industry_projects": "重工項目",
            "rebuild_reason": "重工原因",
            "source_notes": "來源備註",
        })
        # 顯示 DataFrame
        data.set_index('表單編號', inplace=True)

        file_name = "所有重工單分析.csv"
    else:
        return HttpResponse(status=404)

    # 確保輸出為 UTF-8 編碼，並添加 BOM
    csv_string = '\ufeff' + \
        data.to_csv(index=True, encoding='utf-8-sig')  # type:ignore
    response = HttpResponse(csv_string, content_type="text/csv; charset=utf-8")
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response






class TreeAPIView(View):
    def get(self,request, *args, **kwargs):
        route_name = request.resolver_match.url_name
        if route_name  == 'treeApi':
            motherpd = request.GET.get('motherpd')        
            tree_data = TreeTransformer().getTreeData(motherpd)
            return JsonResponse(json.loads(tree_data), safe=False)
        elif route_name  == 'treeApiCheckTime':
            motherpd = request.GET.get('motherpd')
            useleadtime = request.GET.get('useleadtime')
            return JsonResponse(TreeTransformer().getTimeCheckData(motherpd, useleadtime), safe=False)
        elif route_name  == 'getopenmaterials':
            PROD_NO = request.GET.get('PROD_NO')
            qty_num = request.GET.get('qty_num')

            Treedata = json.loads(TreeTransformer().getTreeData(PROD_NO))

            consume_openmaterials_data = {}

            def _get_consume_openmaterials(data):
                for key, value in data.items():
                    if key == 'name':
                        each_name = value
                    if key == 'usefull_qty':
                        each_usefull_qty = value
                    if key == 'consume':
                        each_consume = value
                    if key == 'openmaterials':
                        each_openmaterials = value
                    if key == 'children' and each_openmaterials != '斷階':
                        for _ in value:
                            _get_consume_openmaterials(_)

                if '[' not in each_name and ']' not in each_name and each_openmaterials and each_openmaterials == '斷階':
                    consume_openmaterials_data[each_name] = [
                        each_openmaterials, each_consume, each_usefull_qty]

            _get_consume_openmaterials(Treedata)

            out_data = []
            for key,value in consume_openmaterials_data.items():
                if value[1] * float(qty_num) > value[2]:
                    out_data.append(key)
            
            return JsonResponse(out_data, safe=False)
        else:
            return JsonResponse({"message": "Unknown endpoint"}, status=404)
        

    
    def post(self,request):
        pass