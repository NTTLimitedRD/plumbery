#!/bin/sh

echo "Enter your CaaS API username:"
read MCP_USERNAME

echo "Enter your CaaS API password:"
read -s MCP_PASSWORD

echo "Enter the URL of the fittings file you want to deploy:"
read FITTINGS_URL

echo "Enter the password for deploying new servers:"
read SHARED_SECRET

docker run -e "MCP_USERNAME=$MCP_USERNAME" -e "MCP_PASSWORD=$MCP_PASSWORD" -e "SHARED_SECRET=$SHARED_SECRET" -e "FITTINGS=$FITTINGS_URL" dimensiondataresearch/plumbery
