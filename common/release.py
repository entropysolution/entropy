def fetch_git_release():
    try:
        with open('/srv/release.nfo', 'r') as nfo:
            commit_id = nfo.readline().strip()
            return commit_id[:8]
    except Exception as ex:
        return 'dev'
