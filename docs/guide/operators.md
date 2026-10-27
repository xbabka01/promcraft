# Binary operators

Combine two query expressions with an arithmetic, comparison, logical/set, or trigonometric operator. Each operator has a module-level helper function, and this is the primary way to build binary expressions:

```python
from promcraft import (
    add,
    sub,
    mul,
    div,
    mod,
    pow_,
    eq,
    neq,
    lt,
    lte,
    gt,
    gte,
    and_,
    or_,
    unless,
    atan2,
    Float,
    InstantVector,
)

v1 = InstantVector("requests", [])
v2 = InstantVector("errors", [])

add(Float(1.0), Float(2.0))  # "1.0 + 2.0"
div(v2, v1)  # "errors{} / requests{}"
gt(v1, Float(0.0))  # "requests{} > 0.0"
and_(v1, v2)  # "requests{} and errors{}"
```

| Helper   | Symbol   | Category      |
|----------|----------|---------------|
| `add`    | `+`      | Arithmetic    |
| `sub`    | `-`      | Arithmetic    |
| `mul`    | `*`      | Arithmetic    |
| `div`    | `/`      | Arithmetic    |
| `mod`    | `%`      | Arithmetic    |
| `pow_`   | `^`      | Arithmetic    |
| `eq`     | `==`     | Comparison    |
| `neq`    | `!=`     | Comparison    |
| `lt`     | `<`      | Comparison    |
| `lte`    | `<=`     | Comparison    |
| `gt`     | `>`      | Comparison    |
| `gte`    | `>=`     | Comparison    |
| `and_`   | `and`    | Logical/Set   |
| `or_`    | `or`     | Logical/Set   |
| `unless` | `unless` | Logical/Set   |
| `atan2`  | `atan2`  | Trigonometric |

Python's own operators also work directly on any `Query` (`+ - * / % **`,
`== != < <= > >=`, `&` for `and`, `|` for `or`). Plain numbers are accepted on either side:

```python
requests + errors  # same as add(requests, errors)
errors / requests * 100  # "(errors{} / requests{}) * 100"
1 - errors / requests  # "1 - (errors{} / requests{})"
```

Because comparisons build PromQL expressions, `Query` objects have no truth value:
`bool(q)`, `if q:` and `q in some_list` raise `TypeError`. Comparing with anything that
isn't a query or a number (`q == "foo"`, `q != None`) raises `TypeError` too, rather than
silently returning `False`/`True`. Use `is None` / `is` instead.

## Nested expressions

Nested binary expressions are automatically parenthesized to preserve evaluation order
(function calls and aggregations are self-delimiting and are left unwrapped):

```python
inner = add(Float(1.0), Float(2.0))
outer = mul(inner, Float(3.0))
str(outer)  # "(1.0 + 2.0) * 3.0"
```

## `bool` modifier

Comparisons filter by default. `.bool()` makes them return `0`/`1` per element instead,
which PromQL requires when both sides are scalars. It is only valid on comparison operators:

```python
(v1 > 0).bool()  # "requests{} > bool 0"
(Float(1) > Float(2)).bool()  # "1 > bool 2"
gt(v1, v2).bool().on(["job"])  # "requests{} > bool on (job) errors{}"
```

## Unary minus

```python
-rate(v1[Duration(m=5)])  # "-rate(requests{}[5m])"
-(v1 + v2)  # "-(requests{} + errors{})"
```

In PromQL `-2 ^ 2` means `-(2 ^ 2)`, because `^` binds tighter than unary minus. promcraft therefore parenthesises a negative base of `^`, whether it is a literal or a negation:

```python
Float(-2) ** 2  # "(-2) ^ 2"
(-v1) ** 2  # "(-requests{}) ^ 2"
```

## Label matching

Use `.on()` or `.ignoring()` to control which labels are used for matching when combining two vector selectors:

```python
requests = InstantVector("http_requests_total", [])
errors = InstantVector("http_errors_total", [])

# Match on specific labels
expr = div(errors, requests).on(["job", "env"])
# 'http_errors_total{} / on (job, env) http_requests_total{}'

# Ignore specific labels
expr = div(errors, requests).ignoring(["instance"])
# 'http_errors_total{} / ignoring (instance) http_requests_total{}'
```

Matching and group modifiers need two vectors; using them with a scalar operand raises
`ValueError`.

## Grouping

Use `.group_left()` or `.group_right()` for many-to-one or one-to-many matching:

```python
# group_left: many left-side series match one right-side series;
# the listed labels are copied from the right ("one") side
expr = mul(requests, errors).on(["job"]).group_left(["env"])
# '... on (job) group_left (env) ...'

# group_right: the mirror image; without on/ignoring, `ignoring ()` is added
# because PromQL requires a matching clause before group_left/group_right
expr = mul(requests, errors).group_right([])
# '... ignoring () group_right () ...'
```

Group modifiers are rejected on the set operators `and`, `or` and `unless`, which are always many-to-many.

`.on()`, `.ignoring()`, `.group_left()`, and `.group_right()` are all chainable and each returns a new immutable instance, so they can be combined freely:

```python
mul(requests, errors).ignoring(["env"]).group_right(["env"])
```
