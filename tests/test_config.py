"""
Tests of website/config.py that need no database.
"""

import multiprocessing
import os

from website import config


def write(path, text):
    with open(path, "w") as F:
        F.write(text)


def test_each_configuration_has_its_own_secrets(tmp_path):
    for name, user, password in [("config", "mysite_web", "web-secret"), ("owner", "mysite_owner", "owner-secret")]:
        write(tmp_path / ("%s.ini" % name), "[postgresql]\nuser = %s\npassword = wrong\n" % user)
        secrets = "secrets.ini" if name == "config" else "%s-secrets.ini" % name
        write(tmp_path / secrets, "[postgresql]\npassword = %s\n" % password)
    web = config.configuration(str(tmp_path / "config.ini")).options["postgresql"]
    owner = config.configuration(str(tmp_path / "owner.ini")).options["postgresql"]
    assert (web["user"], web["password"]) == ("mysite_web", "web-secret")
    assert (owner["user"], owner["password"]) == ("mysite_owner", "owner-secret")


def _read_key(directory, start, results):
    os.environ["SITE_CONFIG"] = os.path.join(directory, "config.ini")
    start.wait()
    results.put(config.secret_key())


def test_secret_key_is_shared_by_concurrent_workers(tmp_path):
    # Workers of a server starting at once must all get the same, complete
    # key, whichever of them creates it
    ctx = multiprocessing.get_context("fork")
    start = ctx.Event()
    results = ctx.Queue()
    workers = [ctx.Process(target=_read_key, args=(str(tmp_path), start, results)) for _ in range(8)]
    for w in workers:
        w.start()
    start.set()
    keys = [results.get(timeout=60) for _ in workers]
    for w in workers:
        w.join()
    assert len(set(keys)) == 1 and len(keys[0]) == 64
    assert sorted(os.listdir(tmp_path)) == ["secret_key"]
