from database.connection import get_session
import logging

logger = logging.getLogger(__name__)

CQL_STATEMENTS = [
    """CREATE KEYSPACE IF NOT EXISTS acme_dw
       WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}""",
    """CREATE TABLE IF NOT EXISTS acme_dw.asset (
        id TEXT,
        system_date TIMESTAMP,
        name TEXT,
        description TEXT,
        attributes MAP<TEXT, TEXT>,
        PRIMARY KEY (id, system_date)
    ) WITH CLUSTERING ORDER BY (system_date DESC)""",
    """CREATE TABLE IF NOT EXISTS acme_dw.data_source (
        id TEXT,
        system_date TIMESTAMP,
        name TEXT,
        description TEXT,
        attributes SET<TEXT>,
        PRIMARY KEY (id, system_date)
    ) WITH CLUSTERING ORDER BY (system_date DESC)""",
    """CREATE TABLE IF NOT EXISTS acme_dw.data (
        asset_id TEXT,
        data_source_id TEXT,
        business_date_year INT,
        business_date DATE,
        system_date TIMESTAMP,
        values_double MAP<TEXT, DOUBLE>,
        values_int MAP<TEXT, INT>,
        values_text MAP<TEXT, TEXT>,
        deleted BOOLEAN,
        PRIMARY KEY ((asset_id, data_source_id, business_date_year), business_date, system_date)
    ) WITH CLUSTERING ORDER BY (business_date DESC, system_date DESC)""",
    """CREATE TABLE IF NOT EXISTS acme_dw.totals (
        asset_id TEXT,
        business_date_year INT,
        cnt INT,
        PRIMARY KEY (asset_id, business_date_year)
    ) WITH CLUSTERING ORDER BY (business_date_year DESC)""",
    """CREATE TABLE IF NOT EXISTS acme_dw.regression_data (
        bdate DATE PRIMARY KEY,
        seconds INT,
        open DOUBLE,
        close DOUBLE,
        low DOUBLE,
        high DOUBLE
    )""",
    """CREATE TABLE IF NOT EXISTS acme_dw.regression_results (
        seconds INT PRIMARY KEY,
        open DOUBLE,
        prediction DOUBLE
    )""",
]


def create_tables():
    session = get_session()
    for stmt in CQL_STATEMENTS:
        try:
            session.execute(stmt)
        except Exception as e:
            logger.warning("Schema statement failed (may already exist): %s", e)
    logger.info("Database schema initialized")
