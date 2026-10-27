# Errors and validation

promcraft rejects mistakes it can detect while a query is being built, so they surface as a
Python exception at the line that caused them instead of as a parse error from Prometheus.
Everything else, such as unknown metric names or functions applied to the wrong kind of
vector, is left to Prometheus.

## Literals

Duration fields must be non-negative, and only the documented units are accepted:

```pycon
>>> from promcraft import Duration, Hex, String

>>> Duration(m=-5)
Traceback (most recent call last):
    ...
ValueError: Duration fields must be non-negative (m); use neg=True
>>> Duration(min=5)
Traceback (most recent call last):
    ...
TypeError: Unexpected Duration arguments: min

```

Hexadecimal literals must be whole numbers, and a backtick string cannot contain a backtick:

```pycon
>>> Hex.from_value(3.7)
Traceback (most recent call last):
    ...
ValueError: Hex literals must be integers, got 3.7
>>> String("a`b", "`")
Traceback (most recent call last):
    ...
ValueError: Backtick-quoted strings cannot contain a backtick

```

## Selectors and subqueries

The `@` modifier takes a timestamp, `"start()"` or `"end()"`, and a subquery needs an
instant-vector expression:

```pycon
>>> from promcraft import InstantVector, RangeVector

>>> InstantVector("up", [], at="now")
Traceback (most recent call last):
    ...
ValueError: Invalid @ modifier 'now': expected a number, 'start()' or 'end()'
>>> RangeVector("up", [], Duration(m=5)).subquery(Duration(h=1))
Traceback (most recent call last):
    ...
TypeError: Subqueries require an instant-vector expression, not a range vector

```

## Binary operators

Modifiers are checked against the operator and its operands: `bool` only applies to
comparisons, group modifiers not to the set operators, and vector matching needs two vectors:

```pycon
>>> from promcraft import and_, div

>>> up = InstantVector("up", [])
>>> errors = InstantVector("errors_total", [])

>>> (up + 1).bool()
Traceback (most recent call last):
    ...
ValueError: The bool modifier is only valid for comparison operators, not +
>>> and_(errors, up).group_left([])
Traceback (most recent call last):
    ...
ValueError: Group modifiers are not valid for set operators (always many-to-many): and
>>> div(errors, 60).on(["job"])
Traceback (most recent call last):
    ...
ValueError: Vector matching requires two instant vectors, not a scalar operand: /

```

## Comparisons and truth values

Python's comparison operators build PromQL expressions, so a query has no truth value, and
comparing it with something that is neither a query nor a number is an error rather than
silently `False`:

```pycon
>>> if up > 0:
...     pass
Traceback (most recent call last):
    ...
TypeError: Query objects have no truth value; compare with `is None` instead
>>> up == "up"
Traceback (most recent call last):
    ...
TypeError: Cannot compare InstantVector with str; use `is` to check identity

```

## Formatting

`indent` takes a number of spaces or a whitespace string; `True` is rejected rather than
read as one space:

```pycon
>>> up.to_string(indent=True)
Traceback (most recent call last):
    ...
ValueError: Invalid indent_size

```
