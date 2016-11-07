def init(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import ensure_container
    ensure_container(job.service, root=False)


def install(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import build

    def build_func(cuisine):
        cuisine.development.rust.install()
        cuisine.apps.tidb.build(install=True, start=False)

    build(job.service, build_func)
