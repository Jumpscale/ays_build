def init(job):
    from JumpScale.baselib.atyourservice81.lib.AtYourServiceBuild import ensure_container
    ensure_container(job.service, root=False)


def install(job):
    from JumpScale.baselib.atyourservice81.lib.AtYourServiceBuild import build

    def build_func(cuisine):
        cuisine.development.php.build()
        cuisine.development.php.install()

    build(job.service, build_func)
