#!/bin/sh

# demonstrate the full lifecycle for sql blueprint, across multiple facilities

# now - create all missing parts for the 'sql' fittings
python -m plumbery fittings.yaml build sql

# immediately after - start all nodes of 'sql'
python -m plumbery fittings.yaml start sql

# polish all nodes in 'sql' blueprint
python -m plumbery fittings.yaml polish sql

# time to recycle resources - stop all nodes of 'sql', and reduce the bill
python -m plumbery fittings.yaml stop sql

# stop the bill - destroy all nodes of 'sql', and strip related storage
python -m plumbery fittings.yaml destroy sql

