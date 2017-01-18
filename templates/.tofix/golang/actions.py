def init(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import ensure_container
    ensure_container(job.service, root=True)


def install(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import build

    def build_func(cuisine):
        cuisine.package.ensure('git')
        cuisine.development.golang.install()
        # cuisine.development.golang.install_godep()

    build(job.service, build_func)
