import gevent
import logging
import datetime
import socket
import stock.db_wrap as tu
import tushare as ts
import numpy as np
from .models import *
from gevent.queue import Queue
from gevent.pool import Group

logger = logging.getLogger("orange.storage")


def stock_basics():
    stock_basics = ts.get_stock_basics()
    # START
    if stock_basics['esp'].dtype == np.dtype('float64'):
        # rename 'eps' to 'esp'
        stock_basics["eps"] = stock_basics["esp"]
    else:
        # convert 'eps'
        # as I found 'esp' field was '0.147㈡' at Feb.26.2016
        # It cause SQL server error.
        logger.warn(u"'esp'非浮点类型")
        def _atof(str):
            try:
                return float(str)
            except ValueError:
                # I found 'esp' field was '0.000㈣' at Nov.8.2016
                return float(str[:-1])
        stock_basics["eps"] = stock_basics["esp"].apply(_atof)
    stock_basics = stock_basics.drop("esp", axis=1)
    # drop timeToMarket is zero
    stock_basics = stock_basics[stock_basics['timeToMarket']!=0]
    # change sql type
    stock_basics['timeToMarket'] = stock_basics['timeToMarket'].apply(lambda x:datetime.datetime.strptime(str(x), "%Y%m%d").date())
    # END

    stock_basics_list = [StockBasics(
            code = code,
            name = data['name'],
            industry = data['industry'],
            area = data['area'],
            pe = data['pe'],
            outstanding = data['outstanding'],
            totals = data['totals'],
            totalAssets = data['totalAssets'],
            liquidAssets = data['liquidAssets'],
            fixedAssets = data['fixedAssets'],
            reserved = data['reserved'],
            reservedPerShare = data['reservedPerShare'],
            eps = data['eps'],
            bvps = data['bvps'],
            pb = data['pb'],
            timeToMarket = str(data['timeToMarket']),
        ) for code, data in stock_basics.iterrows()]
    # 先清空
    StockBasics.objects.all().delete()
    # 再保存
    StockBasics.objects.bulk_create(stock_basics_list)


def _get_history_worker(todo_q, result_q):
    cons = ts.get_apis()
    while not todo_q.empty():
        try:
            (retry_count, stock_id) = todo_q.get(timeout=3)
            print("%(stock_id)s try %(retry_count)d times" % locals())
            # 获取历史数据
            his_data = ts.bar(stock_id, conn=cons, adj='qfq')
            result_q.put(his_data)
        except gevent.queue.Empty:
            return
        except socket.timeout:
            todo_q.put((retry_count+1, stock_id))
        except Exception as e:
            todo_q.put((retry_count+1, stock_id))
            print(e)
        gevent.sleep(0)


def _get_history():
    todo_q = Queue()
    # put all stocks' code
    for code in tu.get_stock_basics().index:
        todo_q.put((0, code))
   
    result_q = Queue()
    group = Group()
    # workers
    for i in range(10):
        group.add(gevent.spawn(_get_history_worker,
                               todo_q=todo_q, result_q=result_q))
    group.join()

    # collect history
    his_list = []
    while not result_q.empty():
        his_list.append(result_q.get())
    return his_list

    
def history():
    historys = _get_history()

    history_list = []
    for history in historys:
        for day, data in stock_basics.iterrows():
            history_list.append(History(
                code = data['code'],
                day = str(day),
                open = data['open'],
                close = data['close'],
                high = data['high'],
                low = data['low'],
                vol = data['vol'],
                amount = data['amount'],
            ))
    # 先清空
    History.objects.all().delete()
    # 再保存
    History.objects.bulk_create(history_list)


def report_data(year, quarter):
    report_data = ts.get_report_data(year, quarter)
    report_data.drop_duplicates(inplace=True)

    report_data_list = [ReportData(
            code = data['code'],
            name = data['name'],
            eps = data['eps'],
            eps_yoy = data['eps_yoy'],
            bvps = data['bvps'],
            roe = data['roe'],
            epcf = data['epcf'],
            net_profits = data['net_profits'],
            profits_yoy = data['profits_yoy'],
            distrib = data['distrib'],
            report_date = data['report_date'],
        ) for index, data in report_data.iterrows()]
    # 先清空
    ReportData.objects.all().delete()
    # 再保存
    ReportData.objects.bulk_create(report_data_list)


def profit_data(year, quarter):
    profit_data = ts.get_profit_data(year, quarter)
    profit_data.drop_duplicates(inplace=True)

    profit_data_list = [ProfitData(
            code = data['code'],
            name = data['name'],
            roe = data['roe'],
            net_profit_ratio = data['net_profit_ratio'],
            gross_profit_rate = data['gross_profit_rate'],
            net_profits = data['net_profits'],
            eps = data['eps'],
            business_income = data['business_income'],
            bips = data['bips'],
        ) for index, data in profit_data.iterrows()]
    # 先清空
    ProfitData.objects.all().delete()
    # 再保存
    ProfitData.objects.bulk_create(profit_data_list)


def operation_data(year, quarter):
    operation_data = ts.get_operation_data(year, quarter)
    operation_data.drop_duplicates(inplace=True)

    operation_data_list = [OperationData(
            code = data['code'],
            name = data['name'],
            arturnover = data['arturnover'],
            arturndays = data['arturndays'],
            inventory_turnover = data['inventory_turnover'],
            inventory_days = data['inventory_days'],
            currentasset_turnover = data['currentasset_turnover'],
            currentasset_days = data['currentasset_days'],
        ) for index, data in operation_data.iterrows()]
    # 先清空
    OperationData.objects.all().delete()
    # 再保存
    OperationData.objects.bulk_create(operation_data_list)


def growth_data(year, quarter):
    growth_data = ts.get_growth_data(year, quarter)
    growth_data.drop_duplicates(inplace=True)

    growth_data_list = [GrowthData(
            code = data['code'],
            name = data['name'],
            mbrg = data['mbrg'],
            nprg = data['nprg'],
            nav = data['nav'],
            targ = data['targ'],
            epsg = data['epsg'],
            seg = data['seg'],
        ) for index, data in growth_data.iterrows()]
    # 先清空
    GrowthData.objects.all().delete()
    # 再保存
    GrowthData.objects.bulk_create(growth_data_list)


def debtpaying_data(year, quarter):
    debtpaying_data = ts.get_debtpaying_data(year, quarter)
    debtpaying_data.drop_duplicates(inplace=True)
    debtpaying_data.replace({"--":np.NAN}, inplace=True)

    debtpaying_data_list = [DebtpayingData(
            code = data['code'],
            name = data['name'],
            currentratio = data['currentratio'],
            quickratio = data['quickratio'],
            cashratio = data['cashratio'],
            icratio = data['icratio'],
            sheqratio = data['sheqratio'],
            adratio = data['adratio'],
        ) for index, data in debtpaying_data.iterrows()]
    # 先清空
    DebtpayingData.objects.all().delete()
    # 再保存
    DebtpayingData.objects.bulk_create(debtpaying_data_list)


def cashflow_data(year, quarter):
    cashflow_data = ts.get_cashflow_data(year, quarter)
    cashflow_data.drop_duplicates(inplace=True)

    cashflow_data_list = [CashflowData(
            code = data['code'],
            name = data['name'],
            cf_sales = data['cf_sales'],
            rateofreturn = data['rateofreturn'],
            cf_nm = data['cf_nm'],
            cf_liabilities = data['cf_liabilities'],
            cashflowratio = data['cashflowratio'],
        ) for index, data in cashflow_data.iterrows()]
    # 先清空
    CashflowData.objects.all().delete()
    # 再保存
    CashflowData.objects.bulk_create(cashflow_data_list)
