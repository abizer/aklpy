from __future__ import annotations
from collections.abc import Callable as F, Iterable
from collections import deque
import itertools
import functools
from typing import Any, cast as _cast, overload
from attrs import define
import inspect
# import toolz

_map = map
_filter = filter


def castfunc0(U, f):
    """casts a function as a thunk of type U."""
    return _cast(F[[], U], f)


def castfunc1(T1, U, f):
    """casts a function to the type (T1) -> U"""
    return _cast(F[[T1], U], f)


castfunc = castfunc1


def castfunc2(T1, T2, U, f):
    """casts a function to the type (T1, T2) -> U"""
    return _cast(F[[T1, T2], U], f)


def castfunc3(T1, T2, T3, U, f):
    """casts a function to the type (T1, T2, T3) -> U"""
    return _cast(F[[T1, T2, T3], U], f)


def castfunc4(T1, T2, T3, T4, U, f):
    """casts a function to the type (T1, T2, T3, T4) -> U"""
    return _cast(F[[T1, T2, T3, T4], U], f)


def castfunc5(T1, T2, T3, T4, T5, U, f):
    """casts a function to the type (T1, T2, T3, T4, T5) -> U"""
    return _cast(F[[T1, T2, T3, T4, T5], U], f)


def castfunc6(T1, T2, T3, T4, T5, T6, U, f):
    """casts a function to the type (T1, T2, T3, T4, T5, T6)->U"""
    return _cast(F[[T1, T2, T3, T4, T5, T6], U], f)


def identity[T](t: T) -> T:
    """returns the argument unmodified."""
    return t


get = identity


@define
class Piped[U]:
    """A class that wraps a value and a stack, to allow functions to be called in the order of methods:
    pipe(x) | f | g > h is the same as h(g(f(x))).

    The point of the class is that the pipes "|" check types.

    The class initialiser should not be used, instead call pipe(x).
    """

    _last: F[..., U] | U
    _stack: list

    def to[V](self, f: F[[U], V]) -> Piped[V]:
        """adds f to the stack of function calls"""
        self._stack.append(self._last)
        self._last = f  # type: ignore
        return _cast(Piped[V], self)

    def __or__[V](self, f: F[[U], V]) -> Piped[V]:
        """alias for Piped().to, i.e. pipe(x).to(f) is equivalent to pipe(x) | f."""
        return self.to(f)

    def get(self) -> U:
        """returns the result of applying the stack of functions to the initialised value"""
        if not self._stack:
            return _cast(U, self._last)
        out = self._stack[0]
        for f in self._stack[1:]:
            out = f(out)
        return _cast(F[..., U], self._last)(out)

    def get_and_then[V](self, f: F[[U], V]) -> V:
        """returns the result of applying the stack of functions to the initialised value,
        and then applying f"""
        return f(self.get())

    def __gt__[V](self, f: F[[U], V]) -> V:
        """alias for  Piped().get_and_then, i.e. pipe(x).get_and_then(f) is equivalent to pipe(x) > f."""
        return self.get_and_then(f)

    def __repr__(self) -> str:
        if not self._stack:
            return f"Piped({self._last}, len=1)"
        try:
            lines: list[str] = (
                inspect.getsource(_cast(F, self._last)).strip(" |").split("\n")
            )
            last_src = ";".join(line.strip() for line in lines)
        except TypeError:
            last_src = "<cannot inspect source>"
        return f"Piped({last_src},{' ... , ' if self._stack else ''}len = {len(self._stack) + 1})"

    def __len__(self) -> int:
        return len(self._stack) + 1


def pipe[T](t: T) -> Piped[T]:
    """The only intended method of creating a pipe."""
    return Piped(t, [])


def curry[T, U, V](f: F[[T, U], V]) -> F[[T], F[[U], V]]:
    """returns a curried version of f."""

    def curried_f(t: T) -> F[[U], V]:
        def c(u: U) -> V:
            return f(t, u)

        return c

    return curried_f


cast = curry(_cast)


def map[T, U](f: F[[T], U]) -> F[[Iterable[T]], Iterable[U]]:
    """curried version of map"""
    return curry(_map)(f)


# def starmap[**P, U](
#     f: F[P, U],
# ) -> F[[Iterable[Concatenate[P]]], Iterable[U]]:
#     def sm(xs: Iterable[Concatenate[P]]) -> Iterable[U]:
#         return _map(f, *xs)  # type: ignore

#     return sm


def starmap(f):
    """curried version of itertools.starmap. Currently not typed"""
    return map(star(f))


# todo: see if this can simplify star https://stackoverflow.com/questions/67920245/can-the-unpacking-operator-be-typed-in-python-or-any-other-variadic-args-fu
@overload
def star[T1, T2, U](f: F[[T1, T2], U]) -> F[[tuple[T1, T2]], U]: ...
@overload
def star[T1, T2, T3, U](f: F[[T1, T2, T3], U]) -> F[[tuple[T1, T2, T3]], U]: ...
@overload
def star[T1, T2, T3, T4, U](
    f: F[[T1, T2, T3, T4], U],
) -> F[[tuple[T1, T2, T3, T4]], U]: ...
@overload
def star[T1, T2, T3, T4, T5, U](
    f: F[[T1, T2, T3, T4, T5], U],
) -> F[[tuple[T1, T2, T3, T4, T5]], U]: ...
@overload
def star[T1, T2, T3, T4, T5, T6, U](
    f: F[[T1, T2, T3, T4, T5, T6], U],
) -> F[[tuple[T1, T2, T3, T4, T5, T6]], U]: ...
@overload
def star[T1, T2, T3, T4, T5, T6, T7, U](
    f: F[[T1, T2, T3, T4, T5, T6, T7], U],
) -> F[[tuple[T1, T2, T3, T4, T5, T6, T7]], U]: ...
@overload
def star[T1, T2, T3, T4, T5, T6, T7, T8, U](
    f: F[[T1, T2, T3, T4, T5, T6, T7, T8], U],
) -> F[[tuple[T1, T2, T3, T4, T5, T6, T7, T8]], U]: ...
@overload
def star[T1, T2, T3, T4, T5, T6, T7, T8, T9, U](
    f: F[[T1, T2, T3, T4, T5, T6, T7, T8, T9], U],
) -> F[[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9]], U]: ...
def star[U, T](f: F[..., U]) -> F[..., U]:
    """auxilliary function to allow star destructuring.
    e.g. star(f)(xs) is the same as f(*xs)."""

    def starred(xs: T) -> U:
        return f(*xs)

    return starred


def flatmap[T, U](f: F[[T], Iterable[U]]) -> F[[Iterable[T]], Iterable[U]]:
    """curried version of flatmap i.e. itertools.chain.from_iterable"""
    return lambda x: itertools.chain.from_iterable(_map(f, x))


def reduce[T, U](f: F[[T, U], T], initial: T) -> F[[Iterable[U]], T]:
    """curried version of functools.reduce"""
    return lambda us: functools.reduce(f, us, initial)


reduceleft = reduce


# def reduceright[T, U](f: F[[U, T], T], initializer: T) -> [[Iterable[U]], T]:
# for


def fold[U](f: F[[U, U], U]) -> F[[Iterable[U]], U]:
    """curried version"""

    # raises index error if iterable is empty
    def _fold(iterable: Iterable[U]) -> U:
        us = iter(iterable)
        result = next(us)
        return functools.reduce(f, us, result)

    return _fold


foldleft = fold


# def foldright[U](f: F[[U, U], U]) -> F[[Iterable[U]], U]:
#     # raises index error if iterable is empty
#     def foldr(iterable: Iterable[U]) -> U:
#         us = iter(list(iterable)[::-1])
#         result = next(us)
#         return toolz.reduce(f, us, result)

#     return foldr


def filter[U](f: F[[U], bool]) -> F[[Iterable[U]], Iterable[U]]:
    """curried version of filter"""
    return lambda us: _filter(f, us)


def filterfalse[U](f: F[[U], bool]) -> F[[Iterable[U]], Iterable[U]]:
    """curried version of itertools.filterfalse"""
    return lambda us: itertools.filterfalse(f, us)


def dropwhile[U](f: F[[U], bool]) -> F[[Iterable[U]], Iterable[U]]:
    """curried version of itertools.dropwhile"""
    return lambda us: itertools.dropwhile(f, us)


def drop[U](n: int) -> F[[Iterable[U]], Iterable[U]]:
    """returns a function that drops the first n of an iterable."""
    counter = itertools.count()

    def incr():
        return next(counter)

    return dropwhile(lambda _: incr() < n)


def groupby[U, V](f: F[[U], V]) -> F[[Iterable[U]], itertools.groupby[V, U]]:
    """curried version of itertools.groupby"""
    return lambda us: itertools.groupby(us, f)


def islice[T](
    start: int | None = None, stop: int | None = None, step: int = 1
) -> F[[Iterable[T]], islice[T]]:  # type: ignore
    """curried version of itertools.islice"""
    return lambda us: itertools.islice(_cast(Iterable[T], us), start, stop, step)


pairwise = itertools.pairwise
takewhile = curry(itertools.takewhile)


def take[T](n: int) -> F[[Iterable[T]], itertools.takewhile[T]]:
    """returns a function that takes the first n of an iterable."""
    counter = itertools.count()

    def incr():
        return next(counter)

    return takewhile(lambda _: incr() < n)


def tail[T](n: int) -> F[[Iterable[T]], deque[T]]:
    """returns a function that takes the last n of an iterable."""

    def t(xs: Iterable[T]) -> deque[T]:
        return deque(xs, maxlen=n)

    return t


def last[T](xs: Iterable[T]) -> T:
    """returns the last element of an iterable."""
    return tail(1)(xs)[0]


def tee(n: int = 2):
    """curried version of itertools.tee"""
    return lambda xs: itertools.tee(xs, n)


zip_longest = itertools.zip_longest

product = itertools.product


def permutations[T](
    n: int | None = None,
) -> F[[Iterable[T]], itertools.permutations[tuple[T, ...]]]:
    """curried version of itertools.permutations"""

    def p(xs: Iterable[T]) -> itertools.permutations[tuple[T, ...]]:
        return itertools.permutations(xs, n)

    return p


def combinations[T](n: int) -> F[[Iterable[T]], itertools.combinations[tuple[T, ...]]]:
    """curried version of itertools.combinations"""

    def c(xs: Iterable[T]) -> itertools.combinations[tuple[T, ...]]:
        return itertools.combinations(xs, n)

    return c


def combinations_with_replacement[T](
    n: int,
) -> F[[Iterable[T]], itertools.combinations_with_replacement[tuple[T, ...]]]:
    """curried version of itertools.combinations_with_replacement"""

    def c(xs: Iterable[T]) -> itertools.combinations_with_replacement[tuple[T, ...]]:
        return itertools.combinations_with_replacement(xs, n)

    return c


@overload
def accumulate[S, T](
    func: F[[S, T], T], initial: S
) -> F[[Iterable[T]], Iterable[S]]: ...
@overload
def accumulate[T](func: F[[T, T], T]) -> F[[Iterable[T]], Iterable[T]]: ...
def accumulate(func, initial=None) -> F:
    """curried version of itertools.accumulate"""
    return lambda iterable: itertools.accumulate(iterable, func, initial=initial)


def count[U](xs: Iterable[U]):
    """counts the number of elements in xs. NOT related to itertools.count"""
    return reduce(lambda a, _: a + 1, 0)(xs)


def countfrom(firstval=0, step=1):
    """alias for itertools.count. NOT related to typipe.count"""
    return itertools.count(firstval, step)


# imported here just for completeness
cycle = itertools.cycle
repeat = itertools.repeat


def batched[T](n: int) -> F[[Iterable[T]], itertools.batched[T]]:
    """curried version of itertools.batched"""

    def b(xs: Iterable[T]) -> itertools.batched[T]:
        return itertools.batched(xs, n)

    return b


def tapwith[T](side_effect: F[[T], Any]) -> F[[T], T]:
    """'taps' the stream: applies side_effect at this point, discarding the output, without affecting the stream.
    Warning: If T is Iterable, then this will consume it, so you should use tapcopywith."""

    def tw(t: T) -> T:
        side_effect(t)
        return t

    return tw


def tapcopywith[T](side_effect: F[[Iterable[T]], Any]) -> F[[Iterable[T]], Iterable[T]]:
    """'taps' the stream: applies side_effect at this point, discarding the output.
    Before applying side_effect, tee is used to make an independent iterator so that
    side_effect does nto consume the stream."""

    def tcw(ts: Iterable[T]) -> Iterable[T]:
        ts1, ts2 = itertools.tee(ts)
        side_effect(ts1)
        return ts2

    return tcw


def tap[T](t: T) -> T:
    """'taps' the stream with print. This is a 'functional' version of print,
    allowing you to inspect the output."""
    print(t)
    return t


if __name__ == "__main__":

    def times_two(x: int) -> int:
        return 2 * x

    out = (
        pipe(253)
        | times_two
        | times_two
        | times_two
        | str
        | tap  # prints 2024
        | (lambda s: f"hello {s}!!")
        | (lambda s: _cast(str, s).upper())
    )

    print(out.get())  # HELLO 2024!!

    # its_typechecked = (
    #     pipe(253)
    #     | times_two
    #     | times_two
    #     | times_two
    #     | times_two
    #     | times_two
    #     | str
    #     | times_two  # typechecker should point out error on this line
    #     | times_two
    #     | times_two
    #     | times_two
    # )

    x = (
        pipe(1)
        | times_two
        | times_two
        | times_two
        | range
        | map(times_two)
        | map(times_two)
        | map(times_two)
        | map(str)
        | list[str]
        | tap
        > count
    )

    y = pipe((1, 2))
    print(x)
