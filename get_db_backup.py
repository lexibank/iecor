"""
Gets the specified DB backup (via its name) from CDSTAR, i.e.:

>>> python get_db_backup.py DB_BACKUP_NAME

A target database name might also be specified for loading the backup, i.e.:

>>> python get_db_backup.py DB_BACKUP_NAME TARGET_DB
"""

import sys

import os
from fabric.api import local
from pycdstar.api import Cdstar

SERVICE_URL = os.environ.get('CDSTAR_URL')
USER = os.environ.get('CDSTAR_USER')
PW = os.environ.get('CDSTAR_PWD')


def get_from_cdstar(cdstar_urllib_response, fn='db_dump.gz'):
    with open(fn, 'wb') as f:
        while True:
            chunk = cdstar_urllib_response.read(1024)

            if not chunk:
                break

            f.write(chunk)


def main():
    if len(sys.argv) < 2:
        raise ValueError('Search query is required.')

    if len(sys.argv) > 2:
        db_name = sys.argv[2]
    else:
        db_name = 'cobl_old'

    cdstar = Cdstar(user=USER, password=PW, service_url=SERVICE_URL)
    search_res = cdstar.search(sys.argv[1], index='fulltext')

    if search_res.hitcount is not 1:
        raise ValueError('Nothing found or ambiguous search.')
    else:
        # Checksum or bitstream URL might be better in case of multiple
        # backups with the same name.
        file_resp = search_res[0].resource.read()
        get_from_cdstar(file_resp)

        local('createdb %s' % db_name)
        local('gunzip -c db_dump.gz | psql -1 -d %s' % db_name)


if __name__ == "__main__":
    main()
