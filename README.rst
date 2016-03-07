HAProxy stats for Collectd
==========================

.. image::
    https://img.shields.io/pypi/v/collectd-haproxy.svg
    :target: PyPI_
    :alt: Python Package Version
.. image::
    https://readthedocs.org/projects/collectd-haproxy/badge/?version=latest
    :target: https://collectd-haproxy.readthedocs.org/en/latest
    :alt: Documentation Status
.. image::
    https://travis-ci.org/wglass/collectd-haproxy.svg?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/wglass/collectd-haproxy
.. image:: https://landscape.io/github/wglass/collectd-haproxy/master/landscape.svg?style=flat
   :alt: Code Health
   :target: https://landscape.io/github/wglass/collectd-haproxy/master

A plugin for collectd_ to gather metrics for a local HAProxy_ instance, with a
focus on easy installation and configuration.

.. image:: http://collectd-haproxy.readthedocs.org/en/latest/_images/graphs.png
   :alt: Graphs made with HAProxy stats
   :align: center

(graphs made with Grafana_)


Installation
------------

The project is on PyPI_ so installation is a simple `pip` command::

    pip install collectd-haproxy

.. note::

   If collectd is running with a virtualenv activated (under an isolated
   supervisord_ setup, for instance) make sure the `collectd-haproxy` package
   is installed and available in the virtualenv's module path or collectd will
   run into an `ImportError`.


In order to function properly, the local HAProxy instance will need to have
the "stats socket" enabled, details about how to do that can be found
`here`_.

Configuration
-------------

The most basic configuration is to specify where the HAProxy socket file is
located::

    LoadPlugin "python"

    <Plugin python>
        Import "collectd_haproxy"

        <Module haproxy>
          Socket "/var/run/haproxy.sock"
        </Module>
    </Plugin>

For details on all of the options available, `read the docs`_!


Development
~~~~~~~~~~~

The code is hosted on GitHub_

To file a bug or possible enhancement see the `Issue Tracker`_, also found
on GitHub.


License
~~~~~~~
\(c\) 2015-2016 William Glass

collectd-haproxy is licensed under the terms of the MIT license.  See the
LICENSE_ file for more details.


.. _collectd: https://collectd.org
.. _HAProxy: http://www.haproxy.org
.. _Grafana: http://grafana.org
.. _PyPI: http://pypi.python.org/pypi/collectd-haproxy
.. _here: https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#9.2
.. _supervisord: http://supervisord.org
.. _`read the docs`: http://collectd-haproxy.readthedocs.org/
.. _GitHub: https://github.com/wglass/collectd-haproxy
.. _`Issue Tracker`: https://github.com/wglass/collectd-haproxy/issues
.. _LICENSE: https://github.com/wglass/collectd-haproxy/blob/master/LICENSE
