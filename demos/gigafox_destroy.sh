#!/bin/sh

# demonstrates how to orchestrate all blueprints, across multiple facilities

# stop the bill - destroy nodes, and strip related storage
python -m plumbery fittings.yaml destroy

