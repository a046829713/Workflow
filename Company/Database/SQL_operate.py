import json
from . import router
from sqlalchemy import text
from ..utils import Debug_tool
import pandas as pd


class DB_operate():
    def __init__(self, sqltype) -> None:
        self.sqltype = sqltype

    def change_db_data(self, text_msg: str) -> None:
        """ 用於下其他指令
        Args:
            text_msg (str): SQL_Query
        Returns:
            None
        """
        try:

            self.userconn = router.Router(
                self.sqltype).mssql_financialdata_conn
            with self.userconn as conn:
                conn.execute(text(text_msg))
        except Exception as e:
            Debug_tool.debug.print_info()

    def get_db_data(self, text_msg: str) -> list:
        """
            專門用於select from
        """
        try:
            self.userconn = router.Router(
                self.sqltype).mssql_financialdata_conn
            with self.userconn as conn:

                result = conn.execute(
                    text(text_msg)
                )
                # 資料範例{'Date': '2022/07/01', 'Time': '09:25:00', 'Open': '470', 'High': '470', 'Low': '470', 'Close': '470', 'Volume': '10'}

                return list(result)
        except:
            Debug_tool.debug.print_info()

    def get_pd_data(self, text_msg: str) -> pd.DataFrame():
        """
            專門用於pd 讀取資料庫
        """
        try:
            self.userconn = router.Router(
                self.sqltype).mssql_financialdata_conn
            with self.userconn as conn:

                return pd.read_sql(text(text_msg), conn)
        except:
            Debug_tool.debug.print_info()

    def put_pd_data(self, todaysoutput_df: pd.DataFrame) -> None:
        """
            專門用於pd 讀取資料庫
        """
        try:
            self.userconn = router.Router(
                self.sqltype).mssql_financialdata_conn
            with self.userconn as conn:

                return todaysoutput_df.to_sql('todaysoutput', conn, if_exists="replace")
        except:
            Debug_tool.debug.print_info()

    def change_special_db(self, sql: text, params: dict) -> None:
        """
            專門用於特殊形態的sql
        """
        self.userconn = router.Router(self.sqltype).mssql_financialdata_conn
        with self.userconn as conn:

            result = conn.execute(
                sql, **params
            )

    def change_special_db_add(self, sql: text, params: tuple) -> None:
        """
            專門用於特殊形態的sql
        """
        self.userconn = router.Router(self.sqltype).mssql_financialdata_conn
        with self.userconn as conn:

            result = conn.execute(
                sql, *params
            )
