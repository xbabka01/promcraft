"""PromQL function helpers (`rate`, `abs_`, `histogram_quantile`, ...)."""

from promcraft._base import DEFAULT_STYLE, Query, Style
from promcraft._operator import OPERAND_TYPE, _as_operand
from promcraft._scalar import SCALAR_TYPE, Float
from promcraft._string import STRING_TYPE, String


class Function(Query):
    """A PromQL function call, serialised as `name(arg1, arg2, ...)`.

    Every function helper ([`rate`][promcraft.rate], [`abs_`][promcraft.abs_], ...)
    returns one. Construct it directly only for a function that has no helper;
    raw numbers in `args` are wrapped in [`Float`][promcraft.Float].

    Args:
        name: PromQL function name, e.g. `"rate"`.
        args: Arguments in order; raw numbers are wrapped in [`Float`][promcraft.Float].
    """

    def __init__(self, name: str, args: list[OPERAND_TYPE]) -> None:
        self.name = name
        self.args = [_as_operand(arg) for arg in args]

    def to_string(
        self,
        indent: str | int | None = None,
        _indent_level: int = 0,
        *,
        style: Style = DEFAULT_STYLE,
    ) -> str:
        """Render this expression as a PromQL string."""
        sep, space, pad, _inner_pad = self.get_indent(indent, _indent_level)

        if not self.args:
            return f"{pad}{self.name}()"

        args_str = f",{sep}".join(
            arg.to_string(indent=indent, _indent_level=_indent_level + 1, style=style)
            for arg in self.args
        )
        return f"{pad}{self.name}({space}{args_str}{space}{pad})"


# ---------------------------------------------------------------------------
# Group A — Single instant-vector → instant-vector / scalar
# ---------------------------------------------------------------------------


def abs_(v: Query) -> Function:
    """Return `abs(v)`: the absolute value of each sample.

    Args:
        v: Instant vector to transform.
    """
    return Function("abs", [v])


def ceil(v: Query) -> Function:
    """Return `ceil(v)`: each sample rounded up to the nearest integer.

    Args:
        v: Instant vector to transform.
    """
    return Function("ceil", [v])


def floor(v: Query) -> Function:
    """Return `floor(v)`: each sample rounded down to the nearest integer.

    Args:
        v: Instant vector to transform.
    """
    return Function("floor", [v])


def sqrt(v: Query) -> Function:
    """Return `sqrt(v)`: the square root of each sample.

    Args:
        v: Instant vector to transform.
    """
    return Function("sqrt", [v])


def sgn(v: Query) -> Function:
    """Return `sgn(v)`: the sign of each sample.

    Returns `1.0` for positive values, `-1.0` for negative, and `0.0` for zero.

    Args:
        v: Instant vector to transform.
    """
    return Function("sgn", [v])


def exp(v: Query) -> Function:
    """Return `exp(v)`: e raised to the power of each sample.

    Args:
        v: Instant vector to transform.
    """
    return Function("exp", [v])


def ln(v: Query) -> Function:
    """Return `ln(v)`: the natural logarithm of each sample.

    Args:
        v: Instant vector to transform.
    """
    return Function("ln", [v])


def log2(v: Query) -> Function:
    """Return `log2(v)`: the base-2 logarithm of each sample.

    Args:
        v: Instant vector to transform.
    """
    return Function("log2", [v])


def log10(v: Query) -> Function:
    """Return `log10(v)`: the base-10 logarithm of each sample.

    Args:
        v: Instant vector to transform.
    """
    return Function("log10", [v])


def acos(v: Query) -> Function:
    """Return `acos(v)`: the arccosine of each sample, in radians.

    Args:
        v: Instant vector to transform.
    """
    return Function("acos", [v])


def acosh(v: Query) -> Function:
    """Return `acosh(v)`: the inverse hyperbolic cosine of each sample.

    Args:
        v: Instant vector to transform.
    """
    return Function("acosh", [v])


def asin(v: Query) -> Function:
    """Return `asin(v)`: the arcsine of each sample, in radians.

    Args:
        v: Instant vector to transform.
    """
    return Function("asin", [v])


def asinh(v: Query) -> Function:
    """Return `asinh(v)`: the inverse hyperbolic sine of each sample.

    Args:
        v: Instant vector to transform.
    """
    return Function("asinh", [v])


def atan(v: Query) -> Function:
    """Return `atan(v)`: the arctangent of each sample, in radians.

    Args:
        v: Instant vector to transform.
    """
    return Function("atan", [v])


def atanh(v: Query) -> Function:
    """Return `atanh(v)`: the inverse hyperbolic tangent of each sample.

    Args:
        v: Instant vector to transform.
    """
    return Function("atanh", [v])


def cos(v: Query) -> Function:
    """Return `cos(v)`: the cosine of each sample, taken as radians.

    Args:
        v: Instant vector to transform.
    """
    return Function("cos", [v])


def cosh(v: Query) -> Function:
    """Return `cosh(v)`: the hyperbolic cosine of each sample.

    Args:
        v: Instant vector to transform.
    """
    return Function("cosh", [v])


def sin(v: Query) -> Function:
    """Return `sin(v)`: the sine of each sample, taken as radians.

    Args:
        v: Instant vector to transform.
    """
    return Function("sin", [v])


def sinh(v: Query) -> Function:
    """Return `sinh(v)`: the hyperbolic sine of each sample.

    Args:
        v: Instant vector to transform.
    """
    return Function("sinh", [v])


def tan(v: Query) -> Function:
    """Return `tan(v)`: the tangent of each sample, taken as radians.

    Args:
        v: Instant vector to transform.
    """
    return Function("tan", [v])


def tanh(v: Query) -> Function:
    """Return `tanh(v)`: the hyperbolic tangent of each sample.

    Args:
        v: Instant vector to transform.
    """
    return Function("tanh", [v])


def deg(v: Query) -> Function:
    """Return `deg(v)`: each sample converted from radians to degrees.

    Args:
        v: Instant vector to transform.
    """
    return Function("deg", [v])


def rad(v: Query) -> Function:
    """Return `rad(v)`: each sample converted from degrees to radians.

    Args:
        v: Instant vector to transform.
    """
    return Function("rad", [v])


def timestamp(v: Query) -> Function:
    """Return `timestamp(v)`: the Unix timestamp of each sample, in seconds.

    Args:
        v: Instant vector whose sample timestamps are returned.
    """
    return Function("timestamp", [v])


def sort(v: Query) -> Function:
    """Return `sort(v)`: the elements sorted by sample value, ascending.

    Args:
        v: Instant vector to sort.
    """
    return Function("sort", [v])


def sort_desc(v: Query) -> Function:
    """Return `sort_desc(v)`: the elements sorted by sample value, descending.

    Args:
        v: Instant vector to sort.
    """
    return Function("sort_desc", [v])


def absent(v: Query) -> Function:
    """Return `absent(v)`: a single element with value `1` if `v` is empty.

    Returns an empty vector when `v` is non-empty.

    Args:
        v: Instant vector to check, usually a selector.
    """
    return Function("absent", [v])


def scalar(v: Query) -> Function:
    """Return `scalar(v)`: the value of a single-element `v` as a scalar.

    Returns NaN if `v` does not contain exactly one element.

    Args:
        v: Instant vector with a single element.
    """
    return Function("scalar", [v])


def histogram_count(v: Query) -> Function:
    """Return `histogram_count(v)`: the observation count of each native histogram.

    Args:
        v: Instant vector of native histograms.
    """
    return Function("histogram_count", [v])


def histogram_sum(v: Query) -> Function:
    """Return `histogram_sum(v)`: the sum of observations of each native histogram.

    Args:
        v: Instant vector of native histograms.
    """
    return Function("histogram_sum", [v])


def histogram_avg(v: Query) -> Function:
    """Return `histogram_avg(v)`: the average observation of each native histogram.

    Args:
        v: Instant vector of native histograms.
    """
    return Function("histogram_avg", [v])


def histogram_stddev(v: Query) -> Function:
    """Return `histogram_stddev(v)`: the estimated standard deviation of each native histogram.

    Args:
        v: Instant vector of native histograms.
    """
    return Function("histogram_stddev", [v])


def histogram_stdvar(v: Query) -> Function:
    """Return `histogram_stdvar(v)`: the estimated variance of each native histogram.

    Args:
        v: Instant vector of native histograms.
    """
    return Function("histogram_stdvar", [v])


# ---------------------------------------------------------------------------
# Group B — Single range-vector → instant-vector
# ---------------------------------------------------------------------------


def avg_over_time(v: Query) -> Function:
    """Return `avg_over_time(v)`: the average value of each series over the range.

    Args:
        v: Range vector: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("avg_over_time", [v])


def min_over_time(v: Query) -> Function:
    """Return `min_over_time(v)`: the smallest value of each series in the range.

    Args:
        v: Range vector: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("min_over_time", [v])


def max_over_time(v: Query) -> Function:
    """Return `max_over_time(v)`: the largest value of each series in the range.

    Args:
        v: Range vector: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("max_over_time", [v])


def sum_over_time(v: Query) -> Function:
    """Return `sum_over_time(v)`: the sum of each series' values in the range.

    Args:
        v: Range vector: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("sum_over_time", [v])


def count_over_time(v: Query) -> Function:
    """Return `count_over_time(v)`: the number of samples of each series.

    Args:
        v: Range vector: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("count_over_time", [v])


def stddev_over_time(v: Query) -> Function:
    """Return `stddev_over_time(v)`: the population standard deviation of each series.

    Args:
        v: Range vector: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("stddev_over_time", [v])


def stdvar_over_time(v: Query) -> Function:
    """Return `stdvar_over_time(v)`: the population variance of each series.

    Args:
        v: Range vector: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("stdvar_over_time", [v])


def last_over_time(v: Query) -> Function:
    """Return `last_over_time(v)`: the most recent value of each series.

    Args:
        v: Range vector: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("last_over_time", [v])


def present_over_time(v: Query) -> Function:
    """Return `present_over_time(v)`: `1` for each series with any sample in the range.

    Args:
        v: Range vector: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("present_over_time", [v])


def absent_over_time(v: Query) -> Function:
    """Return `absent_over_time(v)`: a single element with value `1` if `v` has no samples.

    Args:
        v: Range vector: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("absent_over_time", [v])


def first_over_time(v: Query) -> Function:
    """Return `first_over_time(v)`: the oldest value of each series.

    Args:
        v: Range vector: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("first_over_time", [v])


def rate(v: Query) -> Function:
    """Return `rate(v)`: the per-second average rate of increase of a counter.

    Extrapolated to cover the full interval.  Use on monotonically increasing
    counters; automatically handles counter resets.

    Args:
        v: Range vector of a counter: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("rate", [v])


def irate(v: Query) -> Function:
    """Return `irate(v)`: the per-second rate from the last two samples of a counter.

    More responsive than `rate` but more sensitive to spikes.

    Args:
        v: Range vector of a counter: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("irate", [v])


def increase(v: Query) -> Function:
    """Return `increase(v)`: the increase of a counter over the range.

    Extrapolated to cover the full interval; handles counter resets.

    Args:
        v: Range vector of a counter: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("increase", [v])


def delta(v: Query) -> Function:
    """Return `delta(v)`: the difference between the first and last gauge value.

    Extrapolated to cover the full interval.  Use on gauges, not counters.

    Args:
        v: Range vector of a gauge: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("delta", [v])


def idelta(v: Query) -> Function:
    """Return `idelta(v)`: the difference between the last two gauge values.

    Args:
        v: Range vector of a gauge: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("idelta", [v])


def deriv(v: Query) -> Function:
    """Return `deriv(v)`: the per-second derivative of a gauge.

    Estimated with simple linear regression over the range.

    Args:
        v: Range vector of a gauge: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("deriv", [v])


def resets(v: Query) -> Function:
    """Return `resets(v)`: the number of counter resets in the range.

    Args:
        v: Range vector of a counter: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("resets", [v])


def changes(v: Query) -> Function:
    """Return `changes(v)`: the number of times each value changed in the range.

    Args:
        v: Range vector of a gauge: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
    """
    return Function("changes", [v])


# ---------------------------------------------------------------------------
# Group C — No arguments
# ---------------------------------------------------------------------------


def pi() -> Function:
    """Return `pi()`: the constant π."""
    return Function("pi", [])


def time() -> Function:
    """Return `time()`: the evaluation time as seconds since the Unix epoch."""
    return Function("time", [])


# ---------------------------------------------------------------------------
# Group D — Scalar only → instant-vector
# ---------------------------------------------------------------------------


def vector(s: SCALAR_TYPE) -> Function:
    """Return `vector(s)`: scalar `s` as a single-element vector without labels.

    Args:
        s: Scalar to convert; a raw number is wrapped in [`Float`][promcraft.Float].
    """
    return Function("vector", [Float.from_value(s)])


# ---------------------------------------------------------------------------
# Group E — Instant-vector + optional scalar
# ---------------------------------------------------------------------------


def round_(v: Query, to_nearest: SCALAR_TYPE | None = None) -> Function:
    """Return `round(v, to_nearest)`: each sample rounded to a multiple of `to_nearest`.

    Without `to_nearest`, samples are rounded to the nearest integer.

    Args:
        v: Instant vector to round.
        to_nearest: Round to a multiple of this number instead of to an integer.

    Examples:
        >>> temperature = InstantVector("temperature_celsius", [])
        >>> print(round_(temperature))
        round(temperature_celsius{})
        >>> print(round_(temperature, 0.5))
        round(temperature_celsius{}, 0.5)
    """
    if to_nearest is None:
        return Function("round", [v])
    return Function("round", [v, Float.from_value(to_nearest)])


# ---------------------------------------------------------------------------
# Group F — Instant-vector + 1 required scalar
# ---------------------------------------------------------------------------


def clamp_max(v: Query, max: SCALAR_TYPE) -> Function:
    """Return `clamp_max(v, max)`: each sample capped at `max`.

    Args:
        v: Instant vector to clamp.
        max: Upper bound.

    Examples:
        >>> print(clamp_max(InstantVector("error_ratio", []), 1))
        clamp_max(error_ratio{}, 1)
    """
    return Function("clamp_max", [v, Float.from_value(max)])


def clamp_min(v: Query, min: SCALAR_TYPE) -> Function:
    """Return `clamp_min(v, min)`: each sample raised to at least `min`.

    Args:
        v: Instant vector to clamp.
        min: Lower bound.

    Examples:
        >>> print(clamp_min(InstantVector("free_bytes", []), 0))
        clamp_min(free_bytes{}, 0)
    """
    return Function("clamp_min", [v, Float.from_value(min)])


# ---------------------------------------------------------------------------
# Group G — Instant-vector + 2 required scalars
# ---------------------------------------------------------------------------


def clamp(v: Query, min: SCALAR_TYPE, max: SCALAR_TYPE) -> Function:
    """Return `clamp(v, min, max)`: each sample limited to [`min`, `max`].

    Args:
        v: Instant vector to clamp.
        min: Lower bound.
        max: Upper bound.

    Examples:
        >>> print(clamp(InstantVector("error_ratio", []), 0, 1))
        clamp(error_ratio{}, 0, 1)
    """
    return Function("clamp", [v, Float.from_value(min), Float.from_value(max)])


# ---------------------------------------------------------------------------
# Group H — Scalar first, then query
# ---------------------------------------------------------------------------


def quantile_over_time(phi: SCALAR_TYPE, v: Query) -> Function:
    """Return `quantile_over_time(phi, v)`: the `phi`-quantile of each series.

    Args:
        phi: Quantile to compute, from `0` to `1` (`0.95` is the 95th percentile).
        v: Range vector: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].

    Examples:
        >>> latency = InstantVector("latency_seconds", [])
        >>> print(quantile_over_time(0.95, latency[Duration(h=1)]))
        quantile_over_time(0.95, latency_seconds{}[1h])
    """
    return Function("quantile_over_time", [Float.from_value(phi), v])


def histogram_quantile(phi: SCALAR_TYPE, b: Query) -> Function:
    """Return `histogram_quantile(phi, b)`: the `phi`-quantile estimated from `b`.

    Args:
        phi: Quantile to compute, from `0` to `1` (`0.95` is the 95th percentile).
        b: Native histograms, or classic histogram buckets with an `le` label, usually `sum by (le)
            (rate(...))`.

    Examples:
        >>> buckets = InstantVector("http_request_duration_seconds_bucket", [])
        >>> print(histogram_quantile(0.95, sum_(rate(buckets[Duration(m=5)])).by(["le"])))
        histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{}[5m])) by (le))
    """
    return Function("histogram_quantile", [Float.from_value(phi), b])


# ---------------------------------------------------------------------------
# Group I — Two scalars + instant-vector
# ---------------------------------------------------------------------------


def histogram_fraction(lower: SCALAR_TYPE, upper: SCALAR_TYPE, b: Query) -> Function:
    """Return `histogram_fraction(lower, upper, b)`: the fraction in a value range.

    Estimates the fraction of observations in `b` between `lower` and `upper`; bounds that fall
    between bucket boundaries are interpolated as in
    [`histogram_quantile`][promcraft.histogram_quantile].

    Args:
        lower: Lower bound of the observed values; may be `float("-inf")`.
        upper: Upper bound of the observed values; may be `float("inf")`.
        b: Native histograms, or classic histogram buckets with an `le` label, as for
            [`histogram_quantile`][promcraft.histogram_quantile].

    Examples:
        Fraction of requests in the last hour that took 200ms or less:

        >>> duration = InstantVector("http_request_duration_seconds", [])
        >>> print(histogram_fraction(0, 0.2, rate(duration[Duration(h=1)])))
        histogram_fraction(0, 0.2, rate(http_request_duration_seconds{}[1h]))
    """
    return Function("histogram_fraction", [Float.from_value(lower), Float.from_value(upper), b])


# ---------------------------------------------------------------------------
# Group J — Range-vector + 1 scalar
# ---------------------------------------------------------------------------


def predict_linear(v: Query, t: SCALAR_TYPE) -> Function:
    """Return `predict_linear(v, t)`: the value of a gauge predicted `t` seconds ahead.

    Uses simple linear regression over the range.

    Args:
        v: Range vector of a gauge: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
        t: Number of seconds after the evaluation time to predict the value for.

    Examples:
        >>> free = InstantVector("disk_free_bytes", [])
        >>> print(predict_linear(free[Duration(h=6)], 4 * 3600))
        predict_linear(disk_free_bytes{}[6h], 14400)
    """
    return Function("predict_linear", [v, Float.from_value(t)])


# ---------------------------------------------------------------------------
# Group K — Range-vector + 2 scalars
# ---------------------------------------------------------------------------


def double_exponential_smoothing(v: Query, sf: SCALAR_TYPE, tf: SCALAR_TYPE) -> Function:
    """Return `double_exponential_smoothing(v, sf, tf)`: a smoothed gauge value.

    Uses Holt's double exponential smoothing over the range.

    Args:
        v: Range vector of a gauge: a [`RangeVector`][promcraft.RangeVector] or a
            [`Subquery`][promcraft.Subquery].
        sf: Smoothing factor, between `0` and `1` (exclusive); lower values give more weight to old
            data.
        tf: Trend factor, between `0` and `1` (exclusive); higher values give more weight to trends
            in the data.

    Note:
        Experimental — may change in future Prometheus releases.

    Examples:
        >>> temperature = InstantVector("temperature_celsius", [])
        >>> print(double_exponential_smoothing(temperature[Duration(h=1)], 0.3, 0.1))
        double_exponential_smoothing(temperature_celsius{}[1h], 0.3, 0.1)
    """
    return Function(
        "double_exponential_smoothing", [v, Float.from_value(sf), Float.from_value(tf)]
    )


# ---------------------------------------------------------------------------
# Group L — Date/time with optional instant-vector
# ---------------------------------------------------------------------------


def day_of_month(v: Query | None = None) -> Function:
    """Return `day_of_month(v)`: the day of the month (1-31) of each timestamp, in UTC.

    Args:
        v: Instant vector of Unix timestamps; `None` uses the evaluation time (`vector(time())`).
    """
    return Function("day_of_month", [v] if v is not None else [])


def day_of_week(v: Query | None = None) -> Function:
    """Return `day_of_week(v)`: the day of the week (0 = Sunday … 6 = Saturday), in UTC.

    Args:
        v: Instant vector of Unix timestamps; `None` uses the evaluation time (`vector(time())`).
    """
    return Function("day_of_week", [v] if v is not None else [])


def day_of_year(v: Query | None = None) -> Function:
    """Return `day_of_year(v)`: the day of the year (1-366) of each timestamp, in UTC.

    Args:
        v: Instant vector of Unix timestamps; `None` uses the evaluation time (`vector(time())`).
    """
    return Function("day_of_year", [v] if v is not None else [])


def days_in_month(v: Query | None = None) -> Function:
    """Return `days_in_month(v)`: the number of days in the month (28-31), in UTC.

    Args:
        v: Instant vector of Unix timestamps; `None` uses the evaluation time (`vector(time())`).
    """
    return Function("days_in_month", [v] if v is not None else [])


def hour(v: Query | None = None) -> Function:
    """Return `hour(v)`: the hour of the day (0-23) of each timestamp, in UTC.

    Args:
        v: Instant vector of Unix timestamps; `None` uses the evaluation time (`vector(time())`).

    Examples:
        >>> print(hour())
        hour()
        >>> print(hour(timestamp(InstantVector("up", []))))
        hour(timestamp(up{}))
    """
    return Function("hour", [v] if v is not None else [])


def minute(v: Query | None = None) -> Function:
    """Return `minute(v)`: the minute of the hour (0-59) of each timestamp, in UTC.

    Args:
        v: Instant vector of Unix timestamps; `None` uses the evaluation time (`vector(time())`).
    """
    return Function("minute", [v] if v is not None else [])


def month(v: Query | None = None) -> Function:
    """Return `month(v)`: the month of the year (1-12) of each timestamp, in UTC.

    Args:
        v: Instant vector of Unix timestamps; `None` uses the evaluation time (`vector(time())`).
    """
    return Function("month", [v] if v is not None else [])


def year(v: Query | None = None) -> Function:
    """Return `year(v)`: the year of each timestamp, in UTC.

    Args:
        v: Instant vector of Unix timestamps; `None` uses the evaluation time (`vector(time())`).
    """
    return Function("year", [v] if v is not None else [])


# ---------------------------------------------------------------------------
# Group M — Label manipulation (String arguments)
# ---------------------------------------------------------------------------


def label_join(
    v: Query, dst_label: STRING_TYPE, separator: STRING_TYPE, *src_labels: STRING_TYPE
) -> Function:
    """Return `label_join(v, ...)`: `v` with `src_labels` values joined into `dst_label`.

    Args:
        v: Instant vector to relabel.
        dst_label: Label to write the joined value to.
        separator: String placed between the source label values.
        *src_labels: Labels whose values are joined, in order.

    Examples:
        >>> print(label_join(InstantVector("up", []), "address", ":", "host", "port"))
        label_join(up{}, "address", ":", "host", "port")
    """
    return Function(
        "label_join",
        [
            v,
            String.from_value(dst_label),
            String.from_value(separator),
            *(String.from_value(label) for label in src_labels),
        ],
    )


def label_replace(
    v: Query,
    dst_label: STRING_TYPE,
    replacement: STRING_TYPE,
    src_label: STRING_TYPE,
    regex: STRING_TYPE,
) -> Function:
    """Return `label_replace(v, ...)`: `v` with `dst_label` set from a match on `src_label`.

    Capture groups from `regex` may be referenced in `replacement` as `$1`, `$2`, etc.

    Args:
        v: Instant vector to relabel.
        dst_label: Label to write the replacement to.
        replacement: Value to write; may reference capture groups of `regex` as `$1`, `$2`, ...
        src_label: Label whose value `regex` is matched against.
        regex: RE2 regular expression, fully anchored; series it does not match are returned
            unchanged.

    Examples:
        >>> up = InstantVector("up", [])
        >>> print(label_replace(up, "host", "$1", "instance", "(.*):.*"))
        label_replace(up{}, "host", "$1", "instance", "(.*):.*")
    """
    return Function(
        "label_replace",
        [
            v,
            String.from_value(dst_label),
            String.from_value(replacement),
            String.from_value(src_label),
            String.from_value(regex),
        ],
    )


def sort_by_label(v: Query, *labels: STRING_TYPE) -> Function:
    """Return `sort_by_label(v, label, ...)`: the elements sorted by label, ascending.

    Args:
        v: Instant vector to sort.
        *labels: Labels to sort by, in order of priority.

    Examples:
        >>> print(sort_by_label(InstantVector("up", []), "job", "instance"))
        sort_by_label(up{}, "job", "instance")
    """
    return Function("sort_by_label", [v, *(String.from_value(label) for label in labels)])


def sort_by_label_desc(v: Query, *labels: STRING_TYPE) -> Function:
    """Return `sort_by_label_desc(v, label, ...)`: the elements sorted by label, descending.

    Args:
        v: Instant vector to sort.
        *labels: Labels to sort by, in order of priority.

    Examples:
        >>> print(sort_by_label_desc(InstantVector("up", []), "job", "instance"))
        sort_by_label_desc(up{}, "job", "instance")
    """
    return Function("sort_by_label_desc", [v, *(String.from_value(label) for label in labels)])


# ---------------------------------------------------------------------------
# Group N — Optional second query argument
# ---------------------------------------------------------------------------


def info(v: Query, data_label_selector: Query | None = None) -> Function:
    """Return `info(v, data_label_selector)`: `v` with data labels from info series.

    Args:
        v: Instant vector to add data labels to.
        data_label_selector: Braces with label matchers only (an
            [`InstantVector`][promcraft.InstantVector] with an empty metric name), restricting
            which info series and data labels are used. A matcher that does not match the
            empty string drops series that have no matching info series. `None` adds every
            data label of the matching `target_info` series.

    Note:
        Experimental — may change in future Prometheus releases. Needs the
        `--enable-feature=promql-experimental-functions` flag.

    Examples:
        >>> requests = InstantVector("http_requests_total", [])
        >>> cluster = InstantVector("", [Label.re("k8s_cluster_name", ".+")])
        >>> print(info(requests))
        info(http_requests_total{})
        >>> print(info(requests, cluster))
        info(http_requests_total{}, { k8s_cluster_name =~ ".+" })
    """
    return Function("info", [v] if data_label_selector is None else [v, data_label_selector])
