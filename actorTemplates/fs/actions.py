def init(job):
    from JumpScale.baselib.atyourservice81.lib.AtYourServiceBuild import ensure_container
    ensure_container(job.service, root=False)


def install(job):
    from JumpScale.baselib.atyourservice81.lib.AtYourServiceBuild import build

    def build_func(cuisine):
        cuisine.systemservices.g8osfs.build(start=False, reset=True)

    build(job.service, build_func)
