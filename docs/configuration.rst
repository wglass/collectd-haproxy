Configuration
=============

Configuring the collectd-haproxy plugin is done just like any other python-based
plugin for collectd, for details see the `python plugin docs`_.

There are six available options (only the `Socket` option is required)::

    LoadPlugin "python"

    <Plugin python>
        Import "collectd_haproxy"

        <Module haproxy>
          Socket "/var/run/haproxy.sock"
          IncludeInfo true
          IncludeStats true
          IncludeFrontendStats true
          IncludeBackendStats true
          IncludeServerStats true
        </Module>
    </Plugin>


Socket *(required)*
~~~~~~~~~~~~~~~~~~~

This is the path where the HAProxy socket file is located, e.g.
`/var/run/haproxy.sock`


IncludeInfo
~~~~~~~~~~~

A boolean value denoting whether or not to collect the "info" metrics that
describe the state of the whole HAProxy process, metrics such as uptime seconds,
current total connections, size of the run queue, etc.

Defaults to `true`


IncludeStats
~~~~~~~~~~~~

Flag for whether to collect proxy "stats" metrics.  These are detailed metrics
for individual proxies in HAProxy, such as HTTP status 200 response count, bytes
in/out, queued request count, etc.  The full list of metrics available can be
found in the `HAProxy 'show stats' docs`_.

More granular control of which stats to collectd is available via the
:ref:`IncludeFrontendStats`, :ref:`IncludeBackendStats` and
:ref:`IncludeServerStats` options.

This option takes precedence over the more granular ones.  That is, if
`IncludeStats` is false, no proxy-level stats will be collected regardless of the
other `Include*Stats` option values.

Defaults to `true`


.. _includefrontendstats:

IncludeFrontendStats
~~~~~~~~~~~~~~~~~~~~

Granular flag for collecting stats for the "frontend" of a proxy, where
connections are accepted.

Defaults to `true`


.. _includebackendstats:

IncludeBackendStats
~~~~~~~~~~~~~~~~~~~

Granular flag for collecting aggregate stats for the "backend" of a proxy. Each
proxy can have any number of individual servers in a backend, and these stats
are aggregated across the whole lot.

Defaults to `true`


.. _includeserverstats:

IncludeServerStats
~~~~~~~~~~~~~~~~~~

Granular flag for collecting stats for individual servers that make up the
backends of proxies.

.. note::

   This doesn't include ways to filter specific servers, it merely determines
   whether stats at the individual server level are collected at all or not.

Defaults to `true`

.. _`python plugin docs`: https://collectd.org/documentation/manpages/collectd-python.5.shtml
.. _`HAProxy 'show stats' docs`: http://cbonte.github.io/haproxy-dconv/configuration-1.5.html#9.1
