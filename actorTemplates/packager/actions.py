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
        sp.upload('{flist}', source='{source}')
        """.format(
            store_addr=service.model.data.storeAddr,
            namespace=service.model.data.namespace,
            source=service.model.data.sandboxPath,
            flist=service.model.data.flistName)

        cuisine.core.execute_jumpscript(upload)

    build(job.service, build_func)
