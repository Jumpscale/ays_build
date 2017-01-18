def init(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import ensure_container
    ensure_container(job.service, root=False)


def install(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import build

    def build_func(cuisine):
        service = job.service

        cuisine.tools.sandbox.cleanup()

        sshkey = service.producers['sshkey'][0]
        cuisine.core.file_write("/root/.ssh/store_rsa", sshkey.model.data.keyPriv)
        cuisine.core.file_attribs('/root/.ssh/store_rsa', mode='0600')

        upload = r"""
        from JumpScale import j
        j.do.loadSSHKeys('/root/.ssh/store_rsa')
        stor_exec = j.tools.executor.getSSHBased('{store_addr}')
        stor_cuisine = j.tools.cuisine.get(stor_exec)
        ### upload to stor
        sp = stor_cuisine.tools.stor.getStorageSpace('{namespace}')
        sp.upload('{flist}', source='{source}', excludes=['/__pycache__/', '(.*)\\.pyc$', '^\/opt\/code.*'])
        """.format(
            store_addr=service.model.data.storeAddr,
            namespace=service.model.data.namespace,
            source=service.model.data.sandboxPath,
            flist=service.model.data.flistName)

        cuisine.core.execute_jumpscript(upload)

    build(job.service, build_func)


def clean(job):
    # look for build host os service
    builder_host = None
    service = job.service
    for parent in service.parents:
        if parent.model.role == 'os':
            builder_host = parent
            break
    else:
        raise j.exceptions.AYSNotFound("Can't find builder host os service")

    cuisine = builder_host.executor.cuisine
    cuisine.core.dir_remove('/mnt/building/opt')
    cuisine.core.execute_bash('docker rm -f packager cockpit portal jumpscale scality geodns php fs grafana python nodejs mongodb golang nginx shellinabox caddy influxdb redis')


def processChange(job):
    service = job.service
    args = job.model.args

    try:
        change_category = args.pop('changeCategory')
    except KeyError:
        # changeCategory not in args. we can't decide what to do
        return

    if change_category == 'dataschema':
        for key, value in args.items():
            capnp_key = j.data.hrd.sanitize_key(key)
            setattr(service.model.data, capnp_key, value)
        service.saveAll()
