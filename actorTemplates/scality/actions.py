def init(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import ensure_container
    ensure_container(job.service, root=False)


def install(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import build

    def build_func(cuisine):
        cuisine.apps.s3server.install(storageLocation="/data/data", metaLocation="/data/meta/", start=False)

    build(job.service, build_func)
