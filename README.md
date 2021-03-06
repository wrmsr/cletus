This is an exploratory project and far from functional.


cletus, a python library for elasticsearch.
================================

The goal of cletus is to provide to python a set of utilities mostly equivalent
to those found in the elasticsearch java client. Ideally, code written for use
in jython against org.elasticsearch.* should work mostly unmodified when
executed in cpython against this library. While this is not an attempt at
implementing the native transport protocol in python (requests are intended to
go over http) it is a goal to provide an equivalent API.

Rationale is as follows:

* It eases transition between the library and the native client (beit in java or
  jython)
* It makes design decisions easy as it's largely a direct python translation
* Abstraction away from the elasticsearch backend present in other python
  offerings has, in my experience, been universally counterproductive

Notes:

* If you think kwargs obviate builders you should probably not be here.
* Literal interop (get-out-the-way mode) is a priority.
* Additional builder functionality is planned (add_should, add_filter, ...) but
  equivalence is the baseline.
* Builder methods are automatically exposed as both lower_case_underscore and
  lowerCamelCase. This allows both hot swapping with the native client (the
  primary design goal) and more pythonic PEP8 usage.
* I'd prefer to not hard-wire an HTTP client as everyone uses their own
  (half-dozen).
* I'm tempted to also generate equivalent parsers from the builder definitions
  simply because I can.
