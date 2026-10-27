# Integrations

promcraft only builds query strings, so it works with any tool that accepts PromQL: pass
`str(query)` (or `query.to_string()`) wherever a query string is expected. The examples on
this page need third-party packages that promcraft does not depend on.

## Grafana dashboards

[Grafana template variables](https://grafana.com/docs/grafana/latest/dashboards/variables/)
such as `$__rate_interval` are written with [`Variable`][promcraft.Variable]. Build the query
for a panel first:

```pycon
>>> from promcraft import Label, RangeVector, Variable, rate

>>> received_bits = (
...     rate(
...         RangeVector(
...             "node_network_receive_bytes_total",
...             [
...                 Label.eq("job", "integrations/raspberrypi-node"),
...                 Label.neq("device", "lo"),
...             ],
...             Variable("__rate_interval"),
...         )
...     )
...     * 8
... )
>>> print(received_bits)
rate(node_network_receive_bytes_total{ job = "integrations/raspberrypi-node", device != "lo" }[$__rate_interval]) * 8

```

Then use it as a panel target with the
[Grafana Foundation SDK](https://pypi.org/project/grafana-foundation-sdk/)
(`pip install grafana-foundation-sdk`) to generate the dashboard JSON:

```python
from grafana_foundation_sdk.builders.dashboard import Dashboard, Row
from grafana_foundation_sdk.builders.prometheus import Dataquery as PrometheusQuery
from grafana_foundation_sdk.builders.timeseries import Panel as Timeseries
from grafana_foundation_sdk.cog.encoder import JSONEncoder
from grafana_foundation_sdk.models.common import TimeZoneBrowser


def build_dashboard() -> Dashboard:
    return (
        Dashboard("Node Exporter / Raspberry Pi")
        .uid("node-exporter-raspberry-pi")
        .tags(["generated", "raspberrypi-node-integration"])
        .refresh("1m")
        .time("now-30m", "now")
        .timezone(TimeZoneBrowser)
        .with_row(Row("Overview"))
        .with_panel(
            Timeseries()
            .title("Network received")
            .unit("bps")
            .with_target(
                PrometheusQuery()
                .expr(str(received_bits))
                .legend_format("{{device}}")
            )
        )
    )


if __name__ == "__main__":
    dashboard = build_dashboard().build()
    print(JSONEncoder(sort_keys=True, indent=2).encode(dashboard))
```

## Prometheus HTTP API

Send a query to the
[instant query endpoint](https://prometheus.io/docs/prometheus/latest/querying/api/#instant-queries)
`/api/v1/query`, here with [requests](https://pypi.org/project/requests/)
(`pip install requests`):

```python
import requests

from promcraft import InstantVector

query = InstantVector("up", [])
response = requests.get(
    "http://prometheus.example/api/v1/query",
    params={"query": str(query), "time": "2015-07-01T20:10:51.781Z"},
    timeout=10,
)
response.raise_for_status()
for sample in response.json()["data"]["result"]:
    print(sample["metric"], sample["value"])
```
