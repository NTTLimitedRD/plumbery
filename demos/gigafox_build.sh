#!/bin/sh

# demonstrates how to orchestrate all blueprints, across multiple facilities

# build missing parts of the fittings plan, across all facilities
python -m plumbery fittings.yaml build

