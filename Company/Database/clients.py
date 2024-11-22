from sqlalchemy import create_engine, engine


def get_mssql_financialdata_conn(sqltype) -> engine.base.Connection:
    """    
    user: root
    password: 123456
    host: localhost
    port: 3306
    database: financialdata
    如果有實體 IP，以上設定可以自行更改
    Returns:
        engine.base.Connection: _description_
    """
    # address = "mysql+pymysql://root:test@localhost:3306/crypto_data"
    if sqltype == 'MIS':
        address = "mssql+pymssql://MIS:22067856@192.168.2.10:1433/YBICO?charset=utf8"
    if sqltype == 'MISMIS':
        address = "mssql+pymssql://MIS:22067856@192.168.2.10:1433/MIS?charset=utf8"
    if sqltype == 'YBIT':
        address = "mssql+pymssql://YBIT:IT22067856!@192.168.2.251:49749/ERP3000_YB?charset=utf8"
    if sqltype == 'SA':
        address = "mssql+pymssql://sa:Yb55907632@192.168.2.251:49749/ERP3000_YB_TEST?charset=utf8"
    engine = create_engine(address)
    connect = engine.connect()
    return connect
