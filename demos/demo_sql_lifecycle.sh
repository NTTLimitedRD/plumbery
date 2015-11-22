#!/bin/sh

# demonstrate the full lifecycle for sql blueprint, across multiple facilities

# now - create all missing parts for the 'sql' fittings
python build_sql_blueprint.py

# immediately after - start all nodes of 'sql', and polish them according to the plan
python start_sql_nodes.py

# time to recycle resources - stop all nodes of 'sql', and reduce the bill
python stop_sql_nodes.py

# stop the bill - destroy all nodes of 'sql', and strip related storage
python destroy_sql_nodes.py

