from django.shortcuts import render
from django.http import JsonResponse

import json
from stock import get_annual_report, get_tick_data, pct_change
from stock.tu_wrap import get_stock_basics

# Create your views here.


def annual_report(request, code):
    recent = request.GET.get('recent')

    report = get_annual_report(code)
    if recent:
        report = report[report.columns.tolist()[-int(recent):]]

    report.rename(columns=lambda x: str(x)[:10], inplace=True)

    year_yoy = pct_change(report, axis=1)
    year_yoy = (year_yoy * 100).round(2)

    report.fillna(0, inplace=True)
    year_yoy.fillna(0, inplace=True)

    data_dict = dict()
    data_dict['date'] = report.columns.tolist()

    data_dict['income'] = report.loc['销售额'].values.tolist()
    data_dict['profit'] = report.loc['净利润'].values.tolist()
    data_dict['liability'] = report.loc['所有债务'].values.tolist()

    data_dict['income_yoy'] = year_yoy.loc['销售额'].values.tolist()
    data_dict['profit_yoy'] = year_yoy.loc['净利润'].values.tolist()
    data_dict['liability_yoy'] = year_yoy.loc['所有债务'].values.tolist()

    return JsonResponse(data_dict)


def stock_list(request):
    return JsonResponse({
        "stocks": [
            "%s %s" % (row[1].name, row[1]['name'])
            for row in get_stock_basics().iterrows()
        ]
    })


def tick_data(request, code):
    start = request.GET.get('start')
    end = request.GET.get('end')
    tick_data = get_tick_data(code, start, end)

    data_dict = dict()
    data_dict['buy'] = [[
        row[1]['日期'] + ' ' + row[1]['时间'],
        row[1]['成交额'],
    ] for row in tick_data[tick_data['买卖类型'] == '买盘'].iterrows()]
    data_dict['sell'] = [[
        row[1]['日期'] + ' ' + row[1]['时间'],
        row[1]['成交额'],
    ] for row in tick_data[tick_data['买卖类型'] == '卖盘'].iterrows()]

    return JsonResponse(data_dict)