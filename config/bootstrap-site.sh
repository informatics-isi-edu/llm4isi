#!/bin/bash

set -e

if [[ "$#" -eq 0 ]]
then
  echo "Invalid parameter(s): must specify <-h|--host>, catalog <-c|--catalog>, and optional <-l|--label>"
  exit 1
fi

while [ "$#" -gt 0 ]; do
  case "$1" in
    -h) host="$2"; shift 2;;
    -c) catalog="$2"; shift 2;;
    -l) label="$2"; shift 2;;
    --host=*) host="${1#*=}"; shift 1;;
    --catalog=*) catalog="${1#*=}"; shift 1;;
    --label=*) label="${1#*=}"; shift 1;;
    --host|--catalog) echo "$1 requires an argument" >&2; exit 1;;

    -*) echo "unknown option: $1" >&2; exit 1;;
    *) echo "unrecognized argument: $1" >&2; exit 1;;
  esac
done

echo "Host = ${host}"
echo "Catalog = \"${catalog}"\"
echo "Label = \"${label:=${host}}"\"
echo "HeadTitle = \"${label:=${host}}"\"
echo "NavbarBrandText = \"${label:=${host}}"' Data Browser'\"

deriva-catalog-cli --host ${host} create --id "${catalog}" \
--owner 'https://auth.globus.org/3938e0d0-ed35-11e5-8641-22000ab4b42b' \
--auto-configure \
--configure-args includeWWWSchema='False' \
publicSchemaDisplayName='User Info' \
headTitle="${label:=${host}}" \
navbarBrandText="${label:=${host}}"' Data Browser'

deriva-acl-config --host ${host} --config ./self_serve_policy.json "${catalog}"
