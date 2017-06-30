Graphitesend

https://github.com/daniellawrence/graphitesend
http://graphitesend.readthedocs.io/en/latest/


Graphitesend automatically creates a base name for data it sends, that name can be overridden as in this example:

g = graphitesend.init(graphite_server="address of server",system_name="foobar",prefix="ksp")

In [8]: g.send("test",45.1)
Out[8]: 'sent 37 long message: ksp.foobar.test 45.100000 1498803104\n'
