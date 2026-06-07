import logging
import sys
import types

logger = logging.getLogger(__name__)

_cluster = None
_session = None

# Python 3.12+ removed the asyncore module that cassandra-driver relies on
# at import time. Provide a minimal stub so `from cassandra.cluster import Cluster`
# succeeds, then use the AsyncioConnection reactor for actual I/O.
if sys.version_info >= (3, 12) and "asyncore" not in sys.modules:
    _stub = types.ModuleType("asyncore")
    _stub.dispatcher = type("dispatcher", (), {})
    sys.modules["asyncore"] = _stub

# Now safe to reference cassandra imports at module level
from cassandra.io.asyncioreactor import AsyncioConnection  # noqa: E402


def init_cassandra():
    global _cluster, _session
    from cassandra.cluster import Cluster
    from cassandra.policies import DCAwareRoundRobinPolicy
    from config.settings import get_settings

    settings = get_settings()
    hosts = [h.strip() for h in settings.cassandra_hosts.split(",")]

    _cluster = Cluster(
        contact_points=hosts,
        port=settings.cassandra_port,
        load_balancing_policy=DCAwareRoundRobinPolicy(local_dc="datacenter1"),
        connection_class=AsyncioConnection,
    )
    _session = _cluster.connect()

    # Ensure keyspace exists before setting it (safe on fresh instances)
    _session.execute(
        f"CREATE KEYSPACE IF NOT EXISTS {settings.cassandra_keyspace} "
        "WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}"
    )
    _session.set_keyspace(settings.cassandra_keyspace)
    logger.info("Connected to Cassandra at %s", hosts)


def get_session():
    if _session is None:
        raise RuntimeError("Cassandra not initialized. Call init_cassandra() first.")
    return _session


def shutdown_cassandra():
    global _cluster, _session
    if _cluster:
        _cluster.shutdown()
        _cluster = None
        _session = None
        logger.info("Cassandra connection closed")
