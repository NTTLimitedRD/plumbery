#!/bin/sh

# demonstrate the full lifecycle for sql blueprint, across multiple facilities

# now - create all missing parts for the 'sql' fittings
python sql_build.py

# immediately after - start all nodes of 'sql'
python sql_start.py

# polish all nodes in 'sql' blueprint
python sql_polish.py

# time to recycle resources - stop all nodes of 'sql', and reduce the bill
python sql_stop.py

# stop the bill - destroy all nodes of 'sql', and strip related storage
python sql_destroy.py

