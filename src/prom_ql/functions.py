from prom_ql.base import Query
from prom_ql.scalar import Scalar
from prom_ql.string import String


class Function(Query):
    def __init__(self, name: str, args: list[Query]) -> None:
        self.name = name
        self.args = args

    def __str__(self) -> str:
        return f"{self.name}({', '.join(str(a) for a in self.args)})"


# ---------------------------------------------------------------------------
# Group A — Single instant-vector → instant-vector / scalar
# ---------------------------------------------------------------------------


def abs(v: Query) -> Function:  # noqa: A001
    return Function("abs", [v])


def ceil(v: Query) -> Function:
    return Function("ceil", [v])


def floor(v: Query) -> Function:
    return Function("floor", [v])


def sqrt(v: Query) -> Function:
    return Function("sqrt", [v])


def sgn(v: Query) -> Function:
    return Function("sgn", [v])


def exp(v: Query) -> Function:
    return Function("exp", [v])


def ln(v: Query) -> Function:
    return Function("ln", [v])


def log2(v: Query) -> Function:
    return Function("log2", [v])


def log10(v: Query) -> Function:
    return Function("log10", [v])


def acos(v: Query) -> Function:
    return Function("acos", [v])


def acosh(v: Query) -> Function:
    return Function("acosh", [v])


def asin(v: Query) -> Function:
    return Function("asin", [v])


def asinh(v: Query) -> Function:
    return Function("asinh", [v])


def atan(v: Query) -> Function:
    return Function("atan", [v])


def atanh(v: Query) -> Function:
    return Function("atanh", [v])


def cos(v: Query) -> Function:
    return Function("cos", [v])


def cosh(v: Query) -> Function:
    return Function("cosh", [v])


def sin(v: Query) -> Function:
    return Function("sin", [v])


def sinh(v: Query) -> Function:
    return Function("sinh", [v])


def tan(v: Query) -> Function:
    return Function("tan", [v])


def tanh(v: Query) -> Function:
    return Function("tanh", [v])


def deg(v: Query) -> Function:
    return Function("deg", [v])


def rad(v: Query) -> Function:
    return Function("rad", [v])


def timestamp(v: Query) -> Function:
    return Function("timestamp", [v])


def sort(v: Query) -> Function:
    return Function("sort", [v])


def sort_desc(v: Query) -> Function:
    return Function("sort_desc", [v])


def absent(v: Query) -> Function:
    return Function("absent", [v])


def scalar(v: Query) -> Function:  # noqa: A001
    return Function("scalar", [v])


def histogram_count(v: Query) -> Function:
    return Function("histogram_count", [v])


def histogram_sum(v: Query) -> Function:
    return Function("histogram_sum", [v])


def histogram_avg(v: Query) -> Function:
    return Function("histogram_avg", [v])


def histogram_stddev(v: Query) -> Function:
    return Function("histogram_stddev", [v])


def histogram_stdvar(v: Query) -> Function:
    return Function("histogram_stdvar", [v])


# ---------------------------------------------------------------------------
# Group B — Single range-vector → instant-vector
# ---------------------------------------------------------------------------


def avg_over_time(v: Query) -> Function:
    return Function("avg_over_time", [v])


def min_over_time(v: Query) -> Function:
    return Function("min_over_time", [v])


def max_over_time(v: Query) -> Function:
    return Function("max_over_time", [v])


def sum_over_time(v: Query) -> Function:
    return Function("sum_over_time", [v])


def count_over_time(v: Query) -> Function:
    return Function("count_over_time", [v])


def stddev_over_time(v: Query) -> Function:
    return Function("stddev_over_time", [v])


def stdvar_over_time(v: Query) -> Function:
    return Function("stdvar_over_time", [v])


def last_over_time(v: Query) -> Function:
    return Function("last_over_time", [v])


def present_over_time(v: Query) -> Function:
    return Function("present_over_time", [v])


def absent_over_time(v: Query) -> Function:
    return Function("absent_over_time", [v])


def rate(v: Query) -> Function:
    return Function("rate", [v])


def irate(v: Query) -> Function:
    return Function("irate", [v])


def increase(v: Query) -> Function:
    return Function("increase", [v])


def delta(v: Query) -> Function:
    return Function("delta", [v])


def idelta(v: Query) -> Function:
    return Function("idelta", [v])


def deriv(v: Query) -> Function:
    return Function("deriv", [v])


def resets(v: Query) -> Function:
    return Function("resets", [v])


def changes(v: Query) -> Function:
    return Function("changes", [v])


# ---------------------------------------------------------------------------
# Group C — No arguments
# ---------------------------------------------------------------------------


def pi() -> Function:
    return Function("pi", [])


def time() -> Function:
    return Function("time", [])


# ---------------------------------------------------------------------------
# Group D — Scalar only → instant-vector
# ---------------------------------------------------------------------------


def vector(s: Scalar) -> Function:
    return Function("vector", [s])


# ---------------------------------------------------------------------------
# Group E — Instant-vector + optional scalar
# ---------------------------------------------------------------------------


def round(v: Query, to_nearest: Scalar | None = None) -> Function:  # noqa: A001
    return Function("round", [v] if to_nearest is None else [v, to_nearest])


# ---------------------------------------------------------------------------
# Group F — Instant-vector + 1 required scalar
# ---------------------------------------------------------------------------


def clamp_max(v: Query, max: Scalar) -> Function:  # noqa: A002
    return Function("clamp_max", [v, max])


def clamp_min(v: Query, min: Scalar) -> Function:  # noqa: A002
    return Function("clamp_min", [v, min])


# ---------------------------------------------------------------------------
# Group G — Instant-vector + 2 required scalars
# ---------------------------------------------------------------------------


def clamp(v: Query, min: Scalar, max: Scalar) -> Function:  # noqa: A002
    return Function("clamp", [v, min, max])


# ---------------------------------------------------------------------------
# Group H — Scalar first, then query
# ---------------------------------------------------------------------------


def quantile_over_time(quantile: Scalar, v: Query) -> Function:
    return Function("quantile_over_time", [quantile, v])


def histogram_quantile(phi: Scalar, b: Query) -> Function:
    return Function("histogram_quantile", [phi, b])


# ---------------------------------------------------------------------------
# Group I — Two scalars + instant-vector
# ---------------------------------------------------------------------------


def histogram_fraction(lower: Scalar, upper: Scalar, b: Query) -> Function:
    return Function("histogram_fraction", [lower, upper, b])


# ---------------------------------------------------------------------------
# Group J — Range-vector + 1 scalar
# ---------------------------------------------------------------------------


def predict_linear(v: Query, t: Scalar) -> Function:
    return Function("predict_linear", [v, t])


# ---------------------------------------------------------------------------
# Group K — Range-vector + 2 scalars
# ---------------------------------------------------------------------------


def double_exponential_smoothing(v: Query, sf: Scalar, tf: Scalar) -> Function:
    return Function("double_exponential_smoothing", [v, sf, tf])


# ---------------------------------------------------------------------------
# Group L — Date/time with optional instant-vector
# ---------------------------------------------------------------------------


def day_of_month(v: Query | None = None) -> Function:
    return Function("day_of_month", [v] if v is not None else [])


def day_of_week(v: Query | None = None) -> Function:
    return Function("day_of_week", [v] if v is not None else [])


def day_of_year(v: Query | None = None) -> Function:
    return Function("day_of_year", [v] if v is not None else [])


def days_in_month(v: Query | None = None) -> Function:
    return Function("days_in_month", [v] if v is not None else [])


def hour(v: Query | None = None) -> Function:
    return Function("hour", [v] if v is not None else [])


def minute(v: Query | None = None) -> Function:
    return Function("minute", [v] if v is not None else [])


def month(v: Query | None = None) -> Function:
    return Function("month", [v] if v is not None else [])


def year(v: Query | None = None) -> Function:
    return Function("year", [v] if v is not None else [])


# ---------------------------------------------------------------------------
# Group M — Label manipulation (String arguments)
# ---------------------------------------------------------------------------


def label_join(v: Query, dst_label: String, separator: String, *src_labels: String) -> Function:
    return Function("label_join", [v, dst_label, separator, *src_labels])


def label_replace(
    v: Query,
    dst_label: String,
    replacement: String,
    src_label: String,
    regex: String,
) -> Function:
    return Function("label_replace", [v, dst_label, replacement, src_label, regex])


def sort_by_label(v: Query, *labels: String) -> Function:
    return Function("sort_by_label", [v, *labels])


def sort_by_label_desc(v: Query, *labels: String) -> Function:
    return Function("sort_by_label_desc", [v, *labels])


# ---------------------------------------------------------------------------
# Group N — Optional second query argument
# ---------------------------------------------------------------------------


def info(v: Query, data_label_selector: Query | None = None) -> Function:
    return Function("info", [v] if data_label_selector is None else [v, data_label_selector])
