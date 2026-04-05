If you already use monitoring tools you know how hard it is to switch from one another.
You should have uniform interface for all your monitoring means - whether it is a simple
write to file or sending metrics to some monitoring system like Graphite or Prometheus, DataDog, etc.

Now, besides that, there are healthchecks, which are basically a special kind of metrics.

For example, you have a web application and you want to monitor its health. You can write
a simple healthcheck which will check that your web application is up and running and
then your monitoring system will check periodically that healthcheck.

For web application it is usually done by exposing some endpoint which either returns 200 or 503.
With additional info of what exactly failed (and maybe even when).

For non-web applications it is usually done by writing some metrics to monitoring system,
but then your platform that runs your application should be able to check that metrics!

For many currently available services like AWS ECS, Kubernetes, etc. it is not possible
because they expect either healthcheck endpoint or they use docker healtchecks which
is basically a custom shell command that should return 0 or 1.

Again, the specifics on how to figure out whether your service is healthy or not is
not a concern of this library. It is up to you to implement it. This library only
provides a way to expose that information in a uniform way.

If your non-web application is able to write to files, then for lowest possible overhead
you could implement a healthcheck that writes to a json file and then inside HEALTHCHECK
command you can read that using `jq` or something like that.

For a little bit more of overhead you can use this library to expose healthcheck metrics
via HTTP endpoint and then use that endpoint in your HEALTHCHECK command.

Bear in mind that healthcheck is a binary thing - either it is healthy or not. So
you should carefully choose what to expose as a healthcheck metric. For example,
if you have a database connection pool, then you can expose the number of connections
in that pool as a healthcheck metric. If that number is 0, then your service is unhealthy.
If that number is greater than 0, then your service is healthy.

But if your service is talking to another service only on non-critical path, then
you should not expose that as a healthcheck metric. Because if that service is down,
then your service is still healthy, it is just that some non-critical functionality.
It is then the job of a monitoring system to alert you that some non-critical functionality
is not working.

Since the majority of platforms that monitor your healthcheck 
usually only take into account whether your service is healthy or not only for the purpose
of adding a new and removing an old instance of your service - you should be very
careful with how you implement your healthcheck.


ARCHITECTURE
------------

Push vs. Pull

PushOutput means that your application will push metrics to some monitoring system (DataDog, SNS/SQS, etc.).
PullOutput means that your application will expose metrics via HTTP endpoint (in the future maybe via tcp/udp) and
monitoring system will pull them from there.


- Monitor
  - Monitor Data
    - Metric1 (Counter)
      - Host
      - Key
      - Value
      - Tags
      - Timestamp
      - TTL?
      - Type
      - Unit?
      - Rate?
    - Metric2 (Gauge)
    - Metric3 (Histogram)
    - Metric4 (Summary)
    - Metric5 (Info)
    - Metric6 (State (enum in prom))
  - Monitor Output
    - Output1 (Graphite)
    - Output2 (Prometheus)
    - Output3 (DataDog)
    - Output4 (File)
    - Output5 (Stdout)
    - Output6 (Stderr)
    - Output7 (HTTP)
    - Output8 (Healthcheck)
