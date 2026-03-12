from promcraft.base import Query
from promcraft.scalar import Scalar
from promcraft.string import String


class Function(Query):
    """A PromQL function call, serialised as ``name(arg1, arg2, ...)``.

    This class is the return type for all function helper functions in this
    module.  Construct it directly only when a helper does not exist for the
    function you need.
    """

    def __init__(self, name: str, args: list[Query]) -> None:
        self.name = name
        self.args = args

    def __str__(self) -> str:
        return f"{self.name}({', '.join(str(a) for a in self.args)})"


# ---------------------------------------------------------------------------
# Group A — Single instant-vector → instant-vector / scalar
# ---------------------------------------------------------------------------


def abs(v: Query) -> Function:
    """Return the absolute value of each float sample in ``v``."""
    return Function("abs", [v])


def ceil(v: Query) -> Function:
    """Round each float sample in ``v`` up to the nearest integer."""
    return Function("ceil", [v])


def floor(v: Query) -> Function:
    """Round each float sample in ``v`` down to the nearest integer."""
    return Function("floor", [v])


def sqrt(v: Query) -> Function:
    """Return the square root of each float sample in ``v``."""
    return Function("sqrt", [v])


def sgn(v: Query) -> Function:
    """Return the sign of each float sample in ``v``.

    Returns ``1.0`` for positive values, ``-1.0`` for negative, and ``0.0`` for zero.
    """
    return Function("sgn", [v])


def exp(v: Query) -> Function:
    """Return e raised to the power of each float sample in ``v``."""
    return Function("exp", [v])


def ln(v: Query) -> Function:
    """Return the natural logarithm of each float sample in ``v``."""
    return Function("ln", [v])


def log2(v: Query) -> Function:
    """Return the base-2 logarithm of each float sample in ``v``."""
    return Function("log2", [v])


def log10(v: Query) -> Function:
    """Return the base-10 logarithm of each float sample in ``v``."""
    return Function("log10", [v])


def acos(v: Query) -> Function:
    """Return the arccosine (in radians) of each float sample in ``v``."""
    return Function("acos", [v])


def acosh(v: Query) -> Function:
    """Return the inverse hyperbolic cosine of each float sample in ``v``."""
    return Function("acosh", [v])


def asin(v: Query) -> Function:
    """Return the arcsine (in radians) of each float sample in ``v``."""
    return Function("asin", [v])


def asinh(v: Query) -> Function:
    """Return the inverse hyperbolic sine of each float sample in ``v``."""
    return Function("asinh", [v])


def atan(v: Query) -> Function:
    """Return the arctangent (in radians) of each float sample in ``v``."""
    return Function("atan", [v])


def atanh(v: Query) -> Function:
    """Return the inverse hyperbolic tangent of each float sample in ``v``."""
    return Function("atanh", [v])


def cos(v: Query) -> Function:
    """Return the cosine of each float sample in ``v``."""
    return Function("cos", [v])


def cosh(v: Query) -> Function:
    """Return the hyperbolic cosine of each float sample in ``v``."""
    return Function("cosh", [v])


def sin(v: Query) -> Function:
    """Return the sine of each float sample in ``v``."""
    return Function("sin", [v])


def sinh(v: Query) -> Function:
    """Return the hyperbolic sine of each float sample in ``v``."""
    return Function("sinh", [v])


def tan(v: Query) -> Function:
    """Return the tangent of each float sample in ``v``."""
    return Function("tan", [v])


def tanh(v: Query) -> Function:
    """Return the hyperbolic tangent of each float sample in ``v``."""
    return Function("tanh", [v])


def deg(v: Query) -> Function:
    """Convert each float sample in ``v`` from radians to degrees."""
    return Function("deg", [v])


def rad(v: Query) -> Function:
    """Convert each float sample in ``v`` from degrees to radians."""
    return Function("rad", [v])


def timestamp(v: Query) -> Function:
    """Return the Unix timestamp (seconds since epoch) of each sample in ``v``."""
    return Function("timestamp", [v])


def sort(v: Query) -> Function:
    """Sort instant vector elements by float sample value, ascending."""
    return Function("sort", [v])


def sort_desc(v: Query) -> Function:
    """Sort instant vector elements by float sample value, descending."""
    return Function("sort_desc", [v])


def absent(v: Query) -> Function:
    """Return a 1-element vector with value 1 if ``v`` has no elements (``absent(v)``).

    Returns an empty vector when ``v`` is non-empty.
    """
    return Function("absent", [v])


def scalar(v: Query) -> Function:
    """Return ``v``'s single float sample value as a scalar (``scalar(v)``).

    Returns NaN if ``v`` does not contain exactly one element.
    """
    return Function("scalar", [v])


def histogram_count(v: Query) -> Function:
    """Return the count of observations in each native histogram sample."""
    return Function("histogram_count", [v])


def histogram_sum(v: Query) -> Function:
    """Return the sum of observations in each native histogram sample."""
    return Function("histogram_sum", [v])


def histogram_avg(v: Query) -> Function:
    """Return the mean of observed values in each native histogram sample."""
    return Function("histogram_avg", [v])


def histogram_stddev(v: Query) -> Function:
    """Return the estimated standard deviation of observations in a native histogram sample."""
    return Function("histogram_stddev", [v])


def histogram_stdvar(v: Query) -> Function:
    """Return the estimated standard variance of observations in a native histogram sample."""
    return Function("histogram_stdvar", [v])


# ---------------------------------------------------------------------------
# Group B — Single range-vector → instant-vector
# ---------------------------------------------------------------------------


def avg_over_time(v: Query) -> Function:
    """Average of all float samples in the specified range window."""
    return Function("avg_over_time", [v])


def min_over_time(v: Query) -> Function:
    """Minimum float sample value in the specified range window."""
    return Function("min_over_time", [v])


def max_over_time(v: Query) -> Function:
    """Maximum float sample value in the specified range window."""
    return Function("max_over_time", [v])


def sum_over_time(v: Query) -> Function:
    """Sum of all float samples in the specified range window."""
    return Function("sum_over_time", [v])


def count_over_time(v: Query) -> Function:
    """Count of all samples in the specified range window."""
    return Function("count_over_time", [v])


def stddev_over_time(v: Query) -> Function:
    """Population standard deviation of float samples in the range window."""
    return Function("stddev_over_time", [v])


def stdvar_over_time(v: Query) -> Function:
    """Population standard variance of float samples in the range window."""
    return Function("stdvar_over_time", [v])


def last_over_time(v: Query) -> Function:
    """Most recent float sample value in the specified range window."""
    return Function("last_over_time", [v])


def present_over_time(v: Query) -> Function:
    """Return value 1 for any series with at least one sample in the range window."""
    return Function("present_over_time", [v])


def absent_over_time(v: Query) -> Function:
    """Return a 1-element vector (value 1) if ``v`` has no samples in the range window."""
    return Function("absent_over_time", [v])


def rate(v: Query) -> Function:
    """Per-second average rate of increase of a counter over the range window.

    Extrapolated to cover the full interval.  Use on monotonically increasing
    counters; automatically handles counter resets.
    """
    return Function("rate", [v])


def irate(v: Query) -> Function:
    """Per-second instant rate of increase based on the last two data points in the range window.

    More responsive than ``rate`` but more sensitive to spikes.
    """
    return Function("irate", [v])


def increase(v: Query) -> Function:
    """Total increase of a counter over the range window, extrapolated to the full interval."""
    return Function("increase", [v])


def delta(v: Query) -> Function:
    """Difference between the first and last float sample over the range window.

    Extrapolated to cover the full interval.  Use on gauges, not counters.
    """
    return Function("delta", [v])


def idelta(v: Query) -> Function:
    """Difference between the last two float samples in the range window."""
    return Function("idelta", [v])


def deriv(v: Query) -> Function:
    """Per-second derivative of a gauge estimated via simple linear regression.

    Operates over the specified range window.
    """
    return Function("deriv", [v])


def resets(v: Query) -> Function:
    """Number of counter resets within the specified range window."""
    return Function("resets", [v])


def changes(v: Query) -> Function:
    """Number of times a gauge value changed within the specified range window."""
    return Function("changes", [v])


# ---------------------------------------------------------------------------
# Group C — No arguments
# ---------------------------------------------------------------------------


def pi() -> Function:
    """Return the mathematical constant π as a scalar."""
    return Function("pi", [])


def time() -> Function:
    """Return the current evaluation timestamp as seconds since Unix epoch."""
    return Function("time", [])


# ---------------------------------------------------------------------------
# Group D — Scalar only → instant-vector
# ---------------------------------------------------------------------------


def vector(s: Scalar) -> Function:
    """Convert scalar ``s`` into a single-element instant vector with no labels."""
    return Function("vector", [s])


# ---------------------------------------------------------------------------
# Group E — Instant-vector + optional scalar
# ---------------------------------------------------------------------------


def round(v: Query, to_nearest: Scalar | None = None) -> Function:
    """Round float samples to the nearest integer, or to a multiple of ``to_nearest``."""
    return Function("round", [v] if to_nearest is None else [v, to_nearest])


# ---------------------------------------------------------------------------
# Group F — Instant-vector + 1 required scalar
# ---------------------------------------------------------------------------


def clamp_max(v: Query, max: Scalar) -> Function:
    """Clamp float samples so that no value exceeds ``max``."""
    return Function("clamp_max", [v, max])


def clamp_min(v: Query, min: Scalar) -> Function:
    """Clamp float samples so that no value falls below ``min``."""
    return Function("clamp_min", [v, min])


# ---------------------------------------------------------------------------
# Group G — Instant-vector + 2 required scalars
# ---------------------------------------------------------------------------


def clamp(v: Query, min: Scalar, max: Scalar) -> Function:
    """Clamp float samples so all values fall within [``min``, ``max``]."""
    return Function("clamp", [v, min, max])


# ---------------------------------------------------------------------------
# Group H — Scalar first, then query
# ---------------------------------------------------------------------------


def quantile_over_time(quantile: Scalar, v: Query) -> Function:
    """φ-quantile of float samples over the specified range window."""
    return Function("quantile_over_time", [quantile, v])


def histogram_quantile(phi: Scalar, b: Query) -> Function:
    """φ-quantile estimated from a classic or native histogram ``b``."""
    return Function("histogram_quantile", [phi, b])


# ---------------------------------------------------------------------------
# Group I — Two scalars + instant-vector
# ---------------------------------------------------------------------------


def histogram_fraction(lower: Scalar, upper: Scalar, b: Query) -> Function:
    """Estimated fraction of observations in histogram ``b`` within (``lower``, ``upper``]."""
    return Function("histogram_fraction", [lower, upper, b])


# ---------------------------------------------------------------------------
# Group J — Range-vector + 1 scalar
# ---------------------------------------------------------------------------


def predict_linear(v: Query, t: Scalar) -> Function:
    """Predict the value of a gauge ``t`` seconds from now using linear regression.

    The regression is computed over the specified range window.
    """
    return Function("predict_linear", [v, t])


# ---------------------------------------------------------------------------
# Group K — Range-vector + 2 scalars
# ---------------------------------------------------------------------------


def double_exponential_smoothing(v: Query, sf: Scalar, tf: Scalar) -> Function:
    """Produce a smoothed value using the Holt double exponential method.

    ``sf`` is the smoothing factor (0 < sf < 1); ``tf`` is the trend factor
    (0 < tf < 1).

    Note:
        Experimental — may change in future Prometheus releases.
    """
    return Function("double_exponential_smoothing", [v, sf, tf])


# ---------------------------------------------------------------------------
# Group L — Date/time with optional instant-vector
# ---------------------------------------------------------------------------


def day_of_month(v: Query | None = None) -> Function:
    """Day of the month (1–31) in UTC; defaults to ``time()`` when ``v`` is omitted."""
    return Function("day_of_month", [v] if v is not None else [])


def day_of_week(v: Query | None = None) -> Function:
    """Day of the week (0 = Sunday … 6 = Saturday) in UTC for each timestamp in ``v``."""
    return Function("day_of_week", [v] if v is not None else [])


def day_of_year(v: Query | None = None) -> Function:
    """Day of the year (1–365/366) in UTC for each timestamp in ``v``."""
    return Function("day_of_year", [v] if v is not None else [])


def days_in_month(v: Query | None = None) -> Function:
    """Number of days in the month in UTC for each timestamp in ``v``."""
    return Function("days_in_month", [v] if v is not None else [])


def hour(v: Query | None = None) -> Function:
    """Hour of the day (0–23) in UTC for each timestamp in ``v``."""
    return Function("hour", [v] if v is not None else [])


def minute(v: Query | None = None) -> Function:
    """Minute of the hour (0–59) in UTC for each timestamp in ``v``."""
    return Function("minute", [v] if v is not None else [])


def month(v: Query | None = None) -> Function:
    """Month of the year (1–12) in UTC for each timestamp in ``v``."""
    return Function("month", [v] if v is not None else [])


def year(v: Query | None = None) -> Function:
    """Year in UTC for each timestamp in ``v``."""
    return Function("year", [v] if v is not None else [])


# ---------------------------------------------------------------------------
# Group M — Label manipulation (String arguments)
# ---------------------------------------------------------------------------


def label_join(v: Query, dst_label: String, separator: String, *src_labels: String) -> Function:
    """Join ``src_labels`` values with ``separator`` and write the result to ``dst_label``.

    PromQL: ``label_join(v, dst_label, separator, src_label1, ...)``
    """
    return Function("label_join", [v, dst_label, separator, *src_labels])


def label_replace(
    v: Query,
    dst_label: String,
    replacement: String,
    src_label: String,
    regex: String,
) -> Function:
    """Match ``regex`` against ``src_label`` and write the substituted result to ``dst_label``.

    Capture groups from ``regex`` may be referenced in ``replacement`` as ``$1``, ``$2``, etc.

    PromQL: ``label_replace(v, dst_label, replacement, src_label, regex)``
    """
    return Function("label_replace", [v, dst_label, replacement, src_label, regex])


def sort_by_label(v: Query, *labels: String) -> Function:
    """Sort instant vector elements by the values of the specified labels, ascending."""
    return Function("sort_by_label", [v, *labels])


def sort_by_label_desc(v: Query, *labels: String) -> Function:
    """Sort instant vector elements by the values of the specified labels, descending."""
    return Function("sort_by_label_desc", [v, *labels])


# ---------------------------------------------------------------------------
# Group N — Optional second query argument
# ---------------------------------------------------------------------------


def info(v: Query, data_label_selector: Query | None = None) -> Function:
    """Add data labels from matching info series to each time series in ``v``.

    PromQL: ``info(v[, data_label_selector])``

    Note:
        Experimental — may change in future Prometheus releases.
    """
    return Function("info", [v] if data_label_selector is None else [v, data_label_selector])
