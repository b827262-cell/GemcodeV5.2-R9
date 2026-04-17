import git, os

BASE="./workspace"

def init_repo():
    if not os.path.exists(BASE):
        os.makedirs(BASE)
    if not os.path.exists(BASE+"/.git"):
        git.Repo.init(BASE)
    return "ok"

def commit(msg="update"):
    try:
        repo = git.Repo(BASE)
        repo.git.add(A=True)
        repo.index.commit(msg)
        return "committed"
    except Exception as e:
        return str(e)
