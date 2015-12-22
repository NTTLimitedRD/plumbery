#!/bin/sh

# demonstrates how to orchestrate all blueprints, across multiple facilities

# time to recycle resources - stop nodes, and reduce the bill
python -m plumbery fittings.yaml stop

