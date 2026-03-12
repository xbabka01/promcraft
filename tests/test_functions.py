import pytest

from promcraft import (
    Duration,
    Float,
    Function,
    InstantVector,
    RangeVector,
    String,
    abs,
    absent,
    absent_over_time,
    acos,
    acosh,
    asin,
    asinh,
    atan,
    atanh,
    avg_over_time,
    ceil,
    changes,
    clamp,
    clamp_max,
    clamp_min,
    cos,
    cosh,
    count_over_time,
    day_of_month,
    day_of_week,
    day_of_year,
    days_in_month,
    deg,
    delta,
    deriv,
    double_exponential_smoothing,
    exp,
    floor,
    histogram_avg,
    histogram_count,
    histogram_fraction,
    histogram_quantile,
    histogram_stddev,
    histogram_stdvar,
    histogram_sum,
    hour,
    idelta,
    increase,
    info,
    irate,
    label_join,
    label_replace,
    last_over_time,
    ln,
    log2,
    log10,
    max_over_time,
    min_over_time,
    minute,
    month,
    pi,
    predict_linear,
    present_over_time,
    quantile_over_time,
    rad,
    rate,
    resets,
    round,
    scalar,
    sgn,
    sin,
    sinh,
    sort,
    sort_by_label,
    sort_by_label_desc,
    sort_desc,
    sqrt,
    stddev_over_time,
    stdvar_over_time,
    sum_over_time,
    tan,
    tanh,
    time,
    timestamp,
    vector,
    year,
)

_vec = InstantVector("http_requests_total", [])
_rvec = RangeVector("http_requests_total", [], Duration(m=5))


@pytest.mark.parametrize(
    "expr, expected",
    [
        (abs(_vec), "abs(http_requests_total{})"),
        (ceil(_vec), "ceil(http_requests_total{})"),
        (floor(_vec), "floor(http_requests_total{})"),
        (sqrt(_vec), "sqrt(http_requests_total{})"),
        (sgn(_vec), "sgn(http_requests_total{})"),
        (exp(_vec), "exp(http_requests_total{})"),
        (ln(_vec), "ln(http_requests_total{})"),
        (log2(_vec), "log2(http_requests_total{})"),
        (log10(_vec), "log10(http_requests_total{})"),
        (acos(_vec), "acos(http_requests_total{})"),
        (acosh(_vec), "acosh(http_requests_total{})"),
        (asin(_vec), "asin(http_requests_total{})"),
        (asinh(_vec), "asinh(http_requests_total{})"),
        (atan(_vec), "atan(http_requests_total{})"),
        (atanh(_vec), "atanh(http_requests_total{})"),
        (cos(_vec), "cos(http_requests_total{})"),
        (cosh(_vec), "cosh(http_requests_total{})"),
        (sin(_vec), "sin(http_requests_total{})"),
        (sinh(_vec), "sinh(http_requests_total{})"),
        (tan(_vec), "tan(http_requests_total{})"),
        (tanh(_vec), "tanh(http_requests_total{})"),
        (deg(_vec), "deg(http_requests_total{})"),
        (rad(_vec), "rad(http_requests_total{})"),
        (timestamp(_vec), "timestamp(http_requests_total{})"),
        (sort(_vec), "sort(http_requests_total{})"),
        (sort_desc(_vec), "sort_desc(http_requests_total{})"),
        (absent(_vec), "absent(http_requests_total{})"),
        (scalar(_vec), "scalar(http_requests_total{})"),
    ],
)
def test_single_instant_vector(expr: Function, expected: str) -> None:
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        (rate(_rvec), "rate(http_requests_total{}[5m])"),
        (irate(_rvec), "irate(http_requests_total{}[5m])"),
        (increase(_rvec), "increase(http_requests_total{}[5m])"),
        (delta(_rvec), "delta(http_requests_total{}[5m])"),
        (idelta(_rvec), "idelta(http_requests_total{}[5m])"),
        (deriv(_rvec), "deriv(http_requests_total{}[5m])"),
        (resets(_rvec), "resets(http_requests_total{}[5m])"),
        (changes(_rvec), "changes(http_requests_total{}[5m])"),
        (avg_over_time(_rvec), "avg_over_time(http_requests_total{}[5m])"),
        (min_over_time(_rvec), "min_over_time(http_requests_total{}[5m])"),
        (max_over_time(_rvec), "max_over_time(http_requests_total{}[5m])"),
        (sum_over_time(_rvec), "sum_over_time(http_requests_total{}[5m])"),
        (count_over_time(_rvec), "count_over_time(http_requests_total{}[5m])"),
        (stddev_over_time(_rvec), "stddev_over_time(http_requests_total{}[5m])"),
        (stdvar_over_time(_rvec), "stdvar_over_time(http_requests_total{}[5m])"),
        (last_over_time(_rvec), "last_over_time(http_requests_total{}[5m])"),
        (present_over_time(_rvec), "present_over_time(http_requests_total{}[5m])"),
        (absent_over_time(_rvec), "absent_over_time(http_requests_total{}[5m])"),
    ],
)
def test_single_range_vector(expr: Function, expected: str) -> None:
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        (pi(), "pi()"),
        (time(), "time()"),
    ],
)
def test_no_args(expr: Function, expected: str) -> None:
    assert str(expr) == expected


def test_vector() -> None:
    assert str(vector(Float(1.0))) == "vector(1.0)"


@pytest.mark.parametrize(
    "expr, expected",
    [
        (round(_vec), "round(http_requests_total{})"),
        (round(_vec, Float(0.5)), "round(http_requests_total{}, 0.5)"),
    ],
)
def test_round(expr: Function, expected: str) -> None:
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        (clamp(_vec, Float(0.0), Float(1.0)), "clamp(http_requests_total{}, 0.0, 1.0)"),
        (clamp_min(_vec, Float(0.0)), "clamp_min(http_requests_total{}, 0.0)"),
        (clamp_max(_vec, Float(1.0)), "clamp_max(http_requests_total{}, 1.0)"),
    ],
)
def test_clamp(expr: Function, expected: str) -> None:
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        (
            quantile_over_time(Float(0.9), _rvec),
            "quantile_over_time(0.9, http_requests_total{}[5m])",
        ),
        (
            histogram_quantile(Float(0.95), _vec),
            "histogram_quantile(0.95, http_requests_total{})",
        ),
        (
            histogram_fraction(Float(0.0), Float(1.0), _vec),
            "histogram_fraction(0.0, 1.0, http_requests_total{})",
        ),
    ],
)
def test_scalar_then_query(expr: Function, expected: str) -> None:
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        (
            predict_linear(_rvec, Float(3600.0)),
            "predict_linear(http_requests_total{}[5m], 3600.0)",
        ),
        (
            double_exponential_smoothing(_rvec, Float(0.1), Float(0.5)),
            "double_exponential_smoothing(http_requests_total{}[5m], 0.1, 0.5)",
        ),
    ],
)
def test_range_vector_with_scalars(expr: Function, expected: str) -> None:
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        (day_of_month(), "day_of_month()"),
        (day_of_month(_vec), "day_of_month(http_requests_total{})"),
        (day_of_week(), "day_of_week()"),
        (day_of_week(_vec), "day_of_week(http_requests_total{})"),
        (day_of_year(), "day_of_year()"),
        (days_in_month(), "days_in_month()"),
        (hour(), "hour()"),
        (hour(_vec), "hour(http_requests_total{})"),
        (minute(), "minute()"),
        (month(), "month()"),
        (year(), "year()"),
        (year(_vec), "year(http_requests_total{})"),
    ],
)
def test_datetime_functions(expr: Function, expected: str) -> None:
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        (
            label_join(
                _vec,
                String("instance"),
                String(", "),
                String("host"),
                String("job"),
            ),
            'label_join(http_requests_total{}, "instance", ", ", "host", "job")',
        ),
        (
            label_replace(
                _vec,
                String("job"),
                String("${1}"),
                String("job"),
                String("(.*)"),
            ),
            'label_replace(http_requests_total{}, "job", "${1}", "job", "(.*)")',
        ),
        (
            sort_by_label(_vec, String("job")),
            'sort_by_label(http_requests_total{}, "job")',
        ),
        (
            sort_by_label(_vec, String("job"), String("env")),
            'sort_by_label(http_requests_total{}, "job", "env")',
        ),
        (
            sort_by_label_desc(_vec, String("job")),
            'sort_by_label_desc(http_requests_total{}, "job")',
        ),
    ],
)
def test_label_manipulation(expr: Function, expected: str) -> None:
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        (info(_vec), "info(http_requests_total{})"),
        (
            info(_vec, InstantVector("target_info", [])),
            "info(http_requests_total{}, target_info{})",
        ),
    ],
)
def test_info(expr: Function, expected: str) -> None:
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        (histogram_count(_vec), "histogram_count(http_requests_total{})"),
        (histogram_sum(_vec), "histogram_sum(http_requests_total{})"),
        (histogram_avg(_vec), "histogram_avg(http_requests_total{})"),
        (histogram_stddev(_vec), "histogram_stddev(http_requests_total{})"),
        (histogram_stdvar(_vec), "histogram_stdvar(http_requests_total{})"),
    ],
)
def test_histogram_functions(expr: Function, expected: str) -> None:
    assert str(expr) == expected


def test_function_str_repr() -> None:
    f = Function("my_func", [_vec, Float(1.0)])
    assert str(f) == "my_func(http_requests_total{}, 1.0)"


def test_function_no_args_str() -> None:
    f = Function("noop", [])
    assert str(f) == "noop()"
