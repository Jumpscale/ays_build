def init(job):
    from JumpScale.baselib.atyourservice81.lib.AtYourServiceBuild import ensure_container
    ensure_container(job.service, root=True)


def install(job):
    from JumpScale.baselib.atyourservice81.lib.AtYourServiceBuild import build

    def build_func(cuisine):
        cuisine.apps.grafana.build(reset=True)
        cuisine.apps.grafana.install(start=False)

    build(job.service, build_func)
