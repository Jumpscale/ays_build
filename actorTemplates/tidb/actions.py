def init(job):
    from JumpScale.baselib.atyourservice81.lib.AtYourServiceBuild import ensure_container
    ensure_container(job.service, root=False)


def install(job):
    from JumpScale.baselib.atyourservice81.lib.AtYourServiceBuild import build

    def build_func(cuisine):
        cuisine.development.rust.install()
        cuisine.apps.tidb.build(install=True, reset=True)

    build(job.service, build_func)
