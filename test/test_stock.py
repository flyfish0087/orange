"""
stock unittest
"""

import unittest
import pandas as pd

from stock import get_balance_sheet, get_profit_statement

BALANCE_SHEET_COLUMNS_NAME = [
    '货币资金(万元)', '结算备付金(万元)', '拆出资金(万元)', '交易性金融资产(万元)', '衍生金融资产(万元)',
    '应收票据(万元)', '应收账款(万元)', '预付款项(万元)', '应收保费(万元)', '应收分保账款(万元)',
    '应收分保合同准备金(万元)', '应收利息(万元)', '应收股利(万元)', '其他应收款(万元)', '应收出口退税(万元)',
    '应收补贴款(万元)', '应收保证金(万元)', '内部应收款(万元)', '买入返售金融资产(万元)', '存货(万元)',
    '待摊费用(万元)', '待处理流动资产损益(万元)', '一年内到期的非流动资产(万元)', '其他流动资产(万元)', '流动资产合计(万元)',
    '发放贷款及垫款(万元)', '可供出售金融资产(万元)', '持有至到期投资(万元)', '长期应收款(万元)', '长期股权投资(万元)',
    '其他长期投资(万元)', '投资性房地产(万元)', '固定资产原值(万元)', '累计折旧(万元)', '固定资产净值(万元)',
    '固定资产减值准备(万元)', '固定资产(万元)', '在建工程(万元)', '工程物资(万元)', '固定资产清理(万元)',
    '生产性生物资产(万元)', '公益性生物资产(万元)', '油气资产(万元)', '无形资产(万元)', '开发支出(万元)', '商誉(万元)',
    '长期待摊费用(万元)', '股权分置流通权(万元)', '递延所得税资产(万元)', '其他非流动资产(万元)', '非流动资产合计(万元)',
    '资产总计(万元)', '短期借款(万元)', '向中央银行借款(万元)', '吸收存款及同业存放(万元)', '拆入资金(万元)',
    '交易性金融负债(万元)', '衍生金融负债(万元)', '应付票据(万元)', '应付账款(万元)', '预收账款(万元)',
    '卖出回购金融资产款(万元)', '应付手续费及佣金(万元)', '应付职工薪酬(万元)', '应交税费(万元)', '应付利息(万元)',
    '应付股利(万元)', '其他应交款(万元)', '应付保证金(万元)', '内部应付款(万元)', '其他应付款(万元)', '预提费用(万元)',
    '预计流动负债(万元)', '应付分保账款(万元)', '保险合同准备金(万元)', '代理买卖证券款(万元)', '代理承销证券款(万元)',
    '国际票证结算(万元)', '国内票证结算(万元)', '递延收益(万元)', '应付短期债券(万元)', '一年内到期的非流动负债(万元)',
    '其他流动负债(万元)', '流动负债合计(万元)', '长期借款(万元)', '应付债券(万元)', '长期应付款(万元)',
    '专项应付款(万元)', '预计非流动负债(万元)', '长期递延收益(万元)', '递延所得税负债(万元)', '其他非流动负债(万元)',
    '非流动负债合计(万元)', '负债合计(万元)', '实收资本(或股本)(万元)', '资本公积(万元)', '减:库存股(万元)',
    '专项储备(万元)', '盈余公积(万元)', '一般风险准备(万元)', '未确定的投资损失(万元)', '未分配利润(万元)',
    '拟分配现金股利(万元)', '外币报表折算差额(万元)', '归属于母公司股东权益合计(万元)', '少数股东权益(万元)',
    '所有者权益(或股东权益)合计(万元)', '负债和所有者权益(或股东权益)总计(万元)'
]

PROFIT_STATEMENT_COLUMNS_NAME = [
    '营业总收入(万元)', '营业收入(万元)', '利息收入(万元)', '已赚保费(万元)', '手续费及佣金收入(万元)',
    '房地产销售收入(万元)', '其他业务收入(万元)', '营业总成本(万元)', '营业成本(万元)', '利息支出(万元)',
    '手续费及佣金支出(万元)', '房地产销售成本(万元)', '研发费用(万元)', '退保金(万元)', '赔付支出净额(万元)',
    '提取保险合同准备金净额(万元)', '保单红利支出(万元)', '分保费用(万元)', '其他业务成本(万元)', '营业税金及附加(万元)',
    '销售费用(万元)', '管理费用(万元)', '财务费用(万元)', '资产减值损失(万元)', '公允价值变动收益(万元)',
    '投资收益(万元)', '对联营企业和合营企业的投资收益(万元)', '汇兑收益(万元)', '期货损益(万元)', '托管收益(万元)',
    '补贴收入(万元)', '其他业务利润(万元)', '营业利润(万元)', '营业外收入(万元)', '营业外支出(万元)',
    '非流动资产处置损失(万元)', '利润总额(万元)', '所得税费用(万元)', '未确认投资损失(万元)', '净利润(万元)',
    '归属于母公司所有者的净利润(万元)', '被合并方在合并前实现净利润(万元)', '少数股东损益(万元)', '基本每股收益', '稀释每股收益'
]


class TestStock(unittest.TestCase):
    """
    测试股票接口
    """

    def test_get_balance_sheet(self):
        """
        测试资产负债表
        """
        balance_sheet = get_balance_sheet('002367')
        self.assertTrue(isinstance(balance_sheet, pd.DataFrame))
        self.assertEqual(
            list(balance_sheet.columns.values), BALANCE_SHEET_COLUMNS_NAME)
        self.assertEqual(balance_sheet.index.dtype, 'datetime64[ns]')
        for column_name in BALANCE_SHEET_COLUMNS_NAME:
            self.assertEqual(balance_sheet[column_name].dtype, 'float64')

    def test_get_profit_statement(self):
        """
        测试利润表
        """
        profit_statement = get_profit_statement('002367')
        self.assertTrue(isinstance(profit_statement, pd.DataFrame))
        self.assertEqual(
            list(profit_statement.columns.values),
            PROFIT_STATEMENT_COLUMNS_NAME)
        self.assertEqual(profit_statement.index.dtype, 'datetime64[ns]')
        for column_name in PROFIT_STATEMENT_COLUMNS_NAME:
            self.assertEqual(profit_statement[column_name].dtype, 'float64')
